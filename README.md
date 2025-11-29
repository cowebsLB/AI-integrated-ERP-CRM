# AI-integrated-ERP-CRM

A comprehensive Enterprise Resource Planning (ERP) and Customer Relationship Management (CRM) system enhanced with AI capabilities for intelligent automation, predictive analytics, and data-driven decision making.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Core Features](#core-features)
- [AI Integration Points](#ai-integration-points)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Development Roadmap](#development-roadmap)
- [Key Modules](#key-modules)

## 🎯 Project Overview

This system combines traditional ERP and CRM functionalities with modern AI capabilities to provide:

- **Unified Platform**: Single system for managing both internal operations and customer relationships
- **Intelligent Automation**: AI-powered workflows and decision support
- **Predictive Analytics**: Forecast trends, customer behavior, and business metrics
- **Smart Insights**: Automated analysis and recommendations
- **Enhanced User Experience**: Natural language interfaces and intelligent assistants

## 🚀 Core Features

### ERP Modules

1. **Financial Management**
   - Accounting and bookkeeping
   - Budget planning and forecasting
   - Financial reporting and analytics
   - Invoice management
   - Payment processing

2. **Inventory Management**
   - Stock tracking and control
   - Warehouse management
   - Supply chain optimization
   - Purchase order management
   - Vendor management

3. **Human Resources**
   - Employee management
   - Payroll processing
   - Attendance tracking
   - Performance management
   - Recruitment and onboarding

4. **Project Management**
   - Task and milestone tracking
   - Resource allocation
   - Time tracking
   - Project analytics
   - Collaboration tools

5. **Manufacturing/Operations**
   - Production planning
   - Quality control
   - Equipment maintenance
   - Work order management

### CRM Modules

1. **Contact Management**
   - Customer database
   - Contact history
   - Relationship mapping
   - Communication logs

2. **Sales Management**
   - Lead management
   - Opportunity tracking
   - Sales pipeline
   - Quote and proposal generation
   - Sales forecasting

3. **Marketing Automation**
   - Campaign management
   - Email marketing
   - Social media integration
   - Lead scoring
   - Marketing analytics

4. **Customer Service**
   - Ticket management
   - Support portal
   - Knowledge base
   - Live chat integration
   - Customer feedback

5. **Analytics & Reporting**
   - Sales reports
   - Customer insights
   - Performance dashboards
   - Custom reports

## 🤖 AI Integration Points

### 1. **Intelligent Sales Assistant**

- Lead scoring and prioritization
- Sales opportunity prediction
- Optimal pricing recommendations
- Next best action suggestions
- Automated follow-up reminders

### 2. **Predictive Analytics**

- Sales forecasting
- Inventory demand prediction
- Customer churn prediction
- Revenue forecasting
- Market trend analysis

### 3. **Natural Language Processing (NLP)**

- Chatbot for customer support
- Voice-to-text for notes and logs
- Sentiment analysis of customer communications
- Automated email categorization
- Document summarization

### 4. **Intelligent Automation**

- Automated data entry and validation
- Smart invoice processing (OCR + AI)
- Automated report generation
- Workflow optimization
- Anomaly detection

### 5. **Recommendation Engine**

- Product recommendations for customers
- Cross-sell and upsell opportunities
- Content personalization
- Optimal inventory levels
- Resource allocation suggestions

### 6. **AI-Powered Insights**

- Business intelligence dashboards
- Automated insights generation
- Pattern recognition
- Risk assessment
- Performance optimization suggestions

## 💻 Technology Stack

### GUI Framework

- **Framework**: PyQt6
- **UI Components**: Qt Designer for UI design
- **Charts/Visualization**: PyQtGraph / Matplotlib / Plotly
- **Styling**: QSS (Qt Style Sheets)

### Backend & Core

- **Language**: Python 3.10+
- **Framework**: Custom application architecture
- **ORM**: SQLAlchemy
- **Authentication**: Custom JWT-based or session-based auth
- **File Storage**: Local filesystem / SQLite for file metadata

### Database

- **Local**: SQLite (primary database for fast local operations)
- **Cloud Sync**: Supabase (PostgreSQL-based cloud database for backup and multi-device sync)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic

**Dual-Database Architecture:**

- ✅ **SQLite** - Fast local operations, works offline
- ✅ **Supabase** - Cloud backup, multi-device sync, online access
- ✅ **Sync Queue** - Automatic background synchronization
- ✅ **Offline-First** - App works without internet, syncs when online

**How it works:**

1. All operations write to local SQLite immediately (fast, offline-capable)
2. Changes are queued for sync to Supabase
3. Background service syncs queue automatically
4. Pull changes from Supabase on startup/request
5. Conflict resolution strategies (local-first, remote-first, or merge)

**Why this approach?**

- ⚡ Instant local operations (no network latency)
- 📱 Works offline (queue syncs when online)
- ☁️ Cloud backup and multi-device access
- 🔄 Automatic synchronization
- 💾 Best of both worlds (local speed + cloud benefits)

### AI/ML

- **LLM**: Ollama with TinyLlama (638MB quantized, recommended) or Hugging Face
- **AI Features**: Data-aware chat, AI-powered insights, analytics charts
- **ML Framework**: Scikit-learn (for traditional ML tasks, optional)
- **NLP**: Ollama API / Transformers (Hugging Face) for model integration
- **Text Processing**: spaCy / NLTK (optional)
- **Embeddings**: Sentence Transformers (optional)

### Data Processing

- **Data Analysis**: Pandas / NumPy
- **Date/Time**: python-dateutil
- **CSV/Excel**: openpyxl / pandas
- **PDF Processing**: PyPDF2 / pdfplumber (for invoice processing)

### Utilities

- **Configuration**: python-dotenv / configparser
- **Logging**: Python logging module
- **Testing**: pytest / unittest
- **Type Checking**: mypy (optional)

### Third-party Integrations (Optional)

- **Payment**: Stripe API / PayPal API
- **Email**: smtplib / sendgrid-python
- **Calendar**: icalendar
- **Export**: ReportLab (PDF generation)

## 🏗️ System Architecture

### Desktop Application Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  PyQt6 GUI Layer                         │
│  (Main Window, Dialogs, Widgets, Views)                │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Application Controller                      │
│         (Business Logic, State Management)              │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌─────────▼──────────┐
│  ERP/CRM       │      │   AI Service       │
│  Modules       │      │   (Ollama/AI)      │
│  (Services)    │      │                    │
└───────┬────────┘      └─────────┬──────────┘
        │                         │
        └────────────┬────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌─────────▼──────────┐
│   Local DB     │      │   Sync Service     │
│   (SQLite)     │◄────►│   (Queue Manager)  │
└────────────────┘      └─────────┬──────────┘
                                  │
                          ┌───────▼──────────┐
                          │   Supabase       │
                          │   (Cloud DB)     │
                          └──────────────────┘
                                  │
                          ┌───────▼──────────┐
                          │   File System    │
                          │   (Documents)    │
                          └──────────────────┘
```

### Application Structure

1. **GUI Layer (PyQt6)**:
   - Main window with navigation
   - Module-specific views and dialogs
   - Custom widgets and components
   - Charts and visualizations

2. **Business Logic Layer**:
   - ERP modules (Financial, Inventory, HR, Projects)
   - CRM modules (Sales, Marketing, Customer Service)
   - Data validation and business rules
   - Workflow management

3. **AI Service Layer**:
   - Ollama/TinyLlama integration (638MB quantized)
   - Data-aware AI that queries database
   - AI chat interface with conversation history
   - AI Insights with interactive charts
   - Prompt engineering for different use cases
   - Context management for conversations

4. **Data Access Layer**:
   - SQLAlchemy models and repositories
   - Local SQLite database (primary)
   - Sync queue management
   - Supabase integration
   - Query optimization
   - Data migration handling

5. **Sync Service Layer**:
   - Sync queue management
   - Automatic background sync
   - Push/pull operations
   - Conflict resolution
   - Sync status tracking

5. **Utilities & Services**:
   - Authentication and authorization
   - Configuration management
   - Logging and error handling
   - Export/import functionality

## 📅 Development Roadmap

### Phase 1: Foundation (Weeks 1-4) ✅ COMPLETED

- [x] Python project setup and structure
- [x] PyQt6 main window and navigation
- [x] Database schema design (SQLAlchemy models)
- [x] Database initialization and migrations (Alembic)
- [x] Ollama/TinyLlama integration setup
- [x] Configuration management
- [x] Sync queue system (SQLite ↔ Supabase)

### Phase 2: Core ERP Features (Weeks 5-10) ✅ COMPLETED

- [x] Financial management module (PyQt6 UI + backend)
  - [x] Invoice management with line items
  - [x] Payment tracking
  - [x] Account management
  - [x] Transaction recording
- [x] Inventory management (PyQt6 UI + backend)
  - [x] Product management
  - [x] Stock tracking
  - [x] Vendor management
  - [x] Purchase orders
- [x] Human Resources module
  - [x] Employee management
  - [x] Attendance tracking
- [x] Project Management module
  - [x] Project tracking
  - [x] Task management
- [x] Basic reporting and dashboards (PyQtGraph)
- [x] Data tables and forms for ERP modules

### Phase 3: Core CRM Features (Weeks 11-16) ✅ COMPLETED

- [x] Contact and lead management (PyQt6 UI)
  - [x] Contact CRUD with search
  - [x] Communication logging
- [x] Sales pipeline and opportunity tracking
  - [x] Lead management
  - [x] Opportunity tracking
  - [x] Quote generation
- [x] Marketing automation basics
  - [x] Campaign management
  - [x] Campaign-contact associations
- [x] Customer service ticketing
  - [x] Ticket management
  - [x] Ticket responses
- [x] CRM-specific dashboards and visualizations

### Phase 4: AI Integration - Phase 1 (Weeks 17-22) ✅ COMPLETED

- [x] Ollama/TinyLlama service wrapper and integration
- [x] AI chat interface in PyQt6
  - [x] Data-aware AI that queries database
  - [x] Conversation history
  - [x] Real-time responses
- [x] AI Insights module with charts
  - [x] Financial analytics charts
  - [x] Inventory analytics charts
  - [x] Sales pipeline visualizations
  - [x] HR analytics
  - [x] Project analytics
  - [x] CRM analytics

### Phase 5: Advanced Features (Weeks 23-28) 🚧 IN PROGRESS

- [x] Advanced analytics and BI dashboards (PyQtGraph)
  - [x] Module-specific chart tabs
  - [x] Real-time data visualization
- [ ] Workflow automation engine
- [ ] Document processing (PDF parsing with AI)
- [ ] Recommendation engine using AI
- [x] Natural language query interface (via AI chat)
- [ ] Report generation with AI assistance

### Phase 6: AI Integration - Phase 2 (Weeks 29-34)

- [ ] Predictive analytics for inventory (TinyLlama + scikit-learn)
- [ ] Customer churn prediction
- [ ] Advanced automation workflows with AI
- [ ] AI-powered insights generation
- [ ] Smart notifications and alerts
- [ ] AI-assisted report writing

### Phase 7: Integration & Polish (Weeks 35-40)

- [ ] Third-party integrations (payment, email APIs)
- [ ] Performance optimization (async operations, caching)
- [ ] Security hardening (data encryption, secure storage)
- [ ] Comprehensive testing (pytest)
- [ ] UI/UX polish and theming
- [ ] Documentation and user guides
- [ ] Packaging for distribution (PyInstaller/cx_Freeze)

### Phase 8: Launch & Iteration (Ongoing)

- [ ] Beta testing with select users
- [ ] Bug fixes and improvements
- [ ] Feature enhancements based on feedback
- [ ] Scaling and optimization

## 📦 Key Modules

### 1. **Authentication & Authorization**

- Session-based or JWT authentication
- Role-based access control (RBAC)
- User permission management
- Secure password storage (bcrypt)

### 2. **Data Management**

- CRUD operations for all entities
- Data validation and sanitization
- Audit logging
- Data import/export

### 3. **Workflow Engine**

- Customizable business rules
- Automated task assignment
- Approval workflows
- Event-driven automation

### 4. **Reporting & Analytics**

- Pre-built report templates
- Custom report builder
- Real-time dashboards
- Data visualization
- Scheduled reports

### 5. **Integration Hub**

- REST API for external integrations
- Webhook support
- Data synchronization
- Third-party connector library

### 6. **AI Service Layer (Ollama/TinyLlama)**

- Ollama integration (recommended - 638MB quantized model)
- Hugging Face fallback support
- Data-aware AI that queries database directly
- AI chat interface with conversation history
- AI Insights module with interactive charts
- Prompt templates for different use cases
- Context management for conversations
- Integration with business logic

## 🔒 Security Considerations

- Data encryption at rest and in transit
- Regular security audits
- GDPR/CCPA compliance
- Role-based permissions
- API rate limiting
- Input validation and sanitization
- Regular backups and disaster recovery

## 📊 Success Metrics

- User adoption rate
- System performance (response times)
- AI prediction accuracy
- Customer satisfaction scores
- Revenue impact from AI recommendations
- Automation efficiency gains

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- TinyLlama model installed locally (or path configured)
- PyQt6 dependencies

### Installation

1. **Clone the repository** (or navigate to project directory)

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment**:
   - Create a `.env` file in the project root
   - Set `TINYLLAMA_PATH` to your TinyLlama folder path (if not using Hugging Face default)
   - Example: `TINYLLAMA_PATH=C:/path/to/your/tinyllama`

   **Database Configuration:**
   - SQLite is used by default (no setup needed)
   - For Supabase sync (optional but recommended):

     ```
     SUPABASE_URL=https://your-project.supabase.co
     SUPABASE_KEY=your-anon-key
     SUPABASE_ENABLED=true
     SYNC_AUTO=true
     SYNC_INTERVAL=300
     ```

6. **Initialize database**:

   ```bash
   python -c "from src.database.base import init_db; init_db()"
   ```

   This creates the SQLite database file at `data/erp_crm.db` (or uses your configured database).

7. **Run the application**:

   ```bash
   python main.py
   ```

### TinyLlama Setup

**Where to place your TinyLlama folder:**

1. **Recommended:** Place it in the project's `models/` directory:

   ```
   models/
   └── tinyllama/    ← Place your TinyLlama folder here
   ```

2. **Or place it anywhere** and use an absolute path in `.env`

3. **In your `.env` file**, set the path:

   ```env
   TINYLLAMA_PATH=./models/tinyllama
   # Or absolute path: TINYLLAMA_PATH=C:/path/to/tinyllama
   ```

**See `TINYLLAMA_SETUP.md` for detailed instructions and troubleshooting.**

Alternatively, the application will automatically download from Hugging Face if the path is not set.

### Auto-Updater Configuration

The app includes an automatic update checker that monitors GitHub releases from [cowebsLB/AI-integrated-ERP-CRM](https://github.com/cowebsLB/AI-integrated-ERP-CRM).

**Default Configuration:**
- Repository: `cowebsLB/AI-integrated-ERP-CRM`
- Auto-check on startup: Enabled

**To customize** (optional), add to `.env`:
```env
GITHUB_REPO_OWNER=cowebsLB
GITHUB_REPO_NAME=AI-integrated-ERP-CRM
CHECK_UPDATES_ON_STARTUP=true
```

**To use the updater:**
1. **Create releases** on GitHub with semantic version tags (e.g., `v1.0.0`, `v1.2.3`)
2. **Check for updates** via `Help → Check for Updates` or automatically on startup
3. The app will notify users when a newer version is available

**See `docs/UPDATE_SETUP.md` for detailed instructions.**

### Supabase Sync Setup (Optional but Recommended)

For cloud backup and multi-device sync:

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Add to `.env`:

   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_ENABLED=true
   SYNC_AUTO=true
   ```

3. Create matching tables in Supabase (see `docs/SYNC_SETUP.md` for detailed instructions)

The app works offline with SQLite, and syncs to Supabase when online. See `docs/SYNC_SETUP.md` for complete setup guide.

## 🤝 Contributing

[To be added]

## 📄 License

[See LICENSE file]

---

## ✅ Completed Features

### Core Modules

- ✅ **Financial Management** - Invoices, payments, accounts, transactions
- ✅ **Inventory Management** - Products, vendors, purchase orders, stock tracking
- ✅ **Human Resources** - Employee management, attendance tracking
- ✅ **Project Management** - Projects, tasks, milestones
- ✅ **Contact Management** - Contacts, communications, search
- ✅ **Sales Management** - Leads, opportunities, quotes, pipeline
- ✅ **Marketing** - Campaigns, campaign management
- ✅ **Customer Service** - Support tickets, ticket responses

### AI Features

- ✅ **AI Chat** - Data-aware chat that queries your database
- ✅ **AI Insights** - Interactive charts and analytics for all modules
- ✅ **Ollama Integration** - 638MB quantized TinyLlama model
- ✅ **Data Queries** - Ask questions like "How many customers do I have?"

### Infrastructure

- ✅ **Dual Database** - SQLite (local) + Supabase (cloud sync)
- ✅ **Sync Queue** - Automatic background synchronization
- ✅ **Dashboard** - Overview statistics and metrics
- ✅ **All Modules in Toolbar** - Quick access to all features

---

**Status**: Core Features Complete ✅ | Advanced Features in Progress 🚧

**Last Updated**: 2025