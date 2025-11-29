# Supabase Sync Setup Guide

This guide explains how to set up and use the dual-database architecture with SQLite (local) and Supabase (cloud sync).

## Architecture Overview

The application uses an **offline-first** approach:

- **SQLite** - Fast local database (primary)
- **Supabase** - Cloud PostgreSQL database (sync target)
- **Sync Queue** - Tracks changes to be synced
- **Auto-sync** - Background service syncs automatically

## Setup Instructions

### 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Note your project URL and anon key

### 2. Configure Environment Variables

Add to your `.env` file:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_ENABLED=true

# Sync Settings
SYNC_AUTO=true              # Enable automatic background sync
SYNC_INTERVAL=300           # Sync every 5 minutes (in seconds)
SYNC_ON_STARTUP=true        # Sync on application startup
```

### 3. Create Tables in Supabase

You need to create matching tables in Supabase. The sync service will push/pull data to/from these tables.

Example SQL for a `contacts` table:

```sql
CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Important:** Table names and column names should match your SQLAlchemy models.

### 4. Enable Row Level Security (Optional)

For production, enable RLS in Supabase:

```sql
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;

-- Create policy (example - adjust as needed)
CREATE POLICY "Users can manage their own contacts"
ON contacts
FOR ALL
USING (auth.uid() = user_id);
```

## Using Sync in Your Models

### Option 1: Use SyncableMixin (Automatic)

```python
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from src.database.base import Base
from src.database.mixins import SyncableMixin
from sqlalchemy import event

class Contact(Base, SyncableMixin):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Register event listeners for automatic sync
event.listen(Contact, 'after_insert', Contact.after_insert)
event.listen(Contact, 'after_update', Contact.after_update)
event.listen(Contact, 'after_delete', Contact.after_delete)
```

### Option 2: Manual Sync Queue

```python
from src.services.sync_service import SyncService

sync_service = SyncService()

# After creating/updating a record
contact = Contact(name="John Doe", email="john@example.com")
db.add(contact)
db.commit()

# Add to sync queue
sync_service.add_to_queue(
    table_name="contacts",
    record_id=str(contact.id),
    operation="create",
    data=contact.to_dict()
)
```

## Sync Operations

### Manual Sync

```python
from src.services.sync_manager import SyncManager

sync_manager = SyncManager()
sync_manager.sync_now()  # Trigger immediate sync
```

### Check Sync Status

```python
status = sync_manager.get_status()
print(f"Pending: {status['pending']}")
print(f"Synced: {status['synced']}")
print(f"Failed: {status['failed']}")
```

### Pull from Supabase

```python
from src.services.sync_service import SyncService
from datetime import datetime, timedelta

sync_service = SyncService()

# Pull all records updated in the last hour
last_sync = datetime.utcnow() - timedelta(hours=1)
records = sync_service.pull_from_supabase("contacts", last_sync)

# Process and merge with local database
for record in records:
    # Your merge logic here
    pass
```

## Sync Queue Management

### View Queue Status

The sync queue is stored in the `sync_queue` table. You can query it:

```python
from src.database.base import SessionLocal
from src.database.sync_queue import SyncQueue

db = SessionLocal()
pending = db.query(SyncQueue).filter(SyncQueue.status == "pending").all()
```

### Retry Failed Syncs

Failed items can be retried by resetting their status:

```python
failed_items = db.query(SyncQueue).filter(SyncQueue.status == "failed").all()
for item in failed_items:
    if item.retry_count < 5:  # Max retries
        item.status = "pending"
        item.retry_count += 1
db.commit()
```

### Clear Old Synced Items

```python
sync_service.clear_synced_items(older_than_days=7)
```

## Conflict Resolution

When the same record is modified both locally and in Supabase, conflicts can occur. The sync service supports different strategies:

1. **Local-first** (default) - Local changes take precedence
2. **Remote-first** - Supabase changes take precedence
3. **Merge** - Attempt to merge changes (requires custom logic)

Configure in `sync_metadata` table:

```python
from src.database.sync_queue import SyncMetadata

metadata = SyncMetadata(
    table_name="contacts",
    conflict_resolution="local"  # or "remote" or "merge"
)
```

## Best Practices

1. **Always write to local SQLite first** - This ensures fast, offline-capable operations
2. **Let auto-sync handle background sync** - Don't manually sync on every operation
3. **Handle sync failures gracefully** - Check sync status and retry if needed
4. **Use transactions** - Wrap related operations in transactions
5. **Monitor sync queue** - Regularly check for failed items
6. **Test offline scenarios** - Ensure app works without internet

## Troubleshooting

### Sync not working

1. Check Supabase credentials in `.env`
2. Verify `SUPABASE_ENABLED=true`
3. Check logs for error messages
4. Verify table names match between local and Supabase

### High number of failed syncs

1. Check network connectivity
2. Verify Supabase table structure matches local models
3. Check for data type mismatches
4. Review error messages in `sync_queue.error_message`

### Performance issues

1. Increase `SYNC_INTERVAL` to reduce sync frequency
2. Limit batch size in `push_pending_changes(limit=50)`
3. Clear old synced items regularly
4. Consider syncing only changed tables

## Example: Complete Model with Sync

```python
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from src.database.base import Base
from src.database.mixins import SyncableMixin
from sqlalchemy import event

class Invoice(Base, SyncableMixin):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)  # Store as cents
    status = Column(String(20), default="draft")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Override to_dict if needed for custom serialization."""
        return {
            "id": self.id,
            "invoice_number": self.invoice_number,
            "customer_id": self.customer_id,
            "amount": self.amount,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

# Register sync events
event.listen(Invoice, 'after_insert', Invoice.after_insert)
event.listen(Invoice, 'after_update', Invoice.after_update)
event.listen(Invoice, 'after_delete', Invoice.after_delete)
```

## Next Steps

- Create your database models
- Set up Supabase tables
- Test sync functionality
- Implement conflict resolution if needed
- Add sync status UI indicators
