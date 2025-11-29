# Auto-Updater Setup Guide

The application includes an automatic update checker that monitors GitHub releases for new versions.

## Configuration

### 1. Set GitHub Repository Information

Add the following to your `.env` file:

```env
# GitHub Repository Configuration
GITHUB_REPO_OWNER=your-username
GITHUB_REPO_NAME=AI-integrated-ERP-CRM

# Update Check Settings
CHECK_UPDATES_ON_STARTUP=true
AUTO_CHECK_UPDATES=true
```

Or set them directly in `config.py`:

```python
GITHUB_REPO_OWNER = "your-username"
GITHUB_REPO_NAME = "AI-integrated-ERP-CRM"
CHECK_UPDATES_ON_STARTUP = True
AUTO_CHECK_UPDATES = True
```

### 2. Version Tagging

For the updater to work correctly, your GitHub releases must follow semantic versioning:

- **Format**: `v1.0.0`, `v1.2.3`, `v2.0.0-beta.1`, etc.
- **Examples**:
  - `v1.0.0` ✅
  - `v1.2.3` ✅
  - `v2.0.0-beta.1` ✅
  - `1.0.0` ✅ (v prefix is optional)
  - `release-1.0.0` ❌ (won't work)

### 3. Creating a Release

1. Go to your GitHub repository
2. Click on "Releases" → "Create a new release"
3. Choose a tag (e.g., `v1.0.1`)
4. Fill in the release title and description
5. Optionally attach release assets (installers, binaries, etc.)
6. Click "Publish release"

## How It Works

### Automatic Checks

- **On Startup**: If `CHECK_UPDATES_ON_STARTUP=true`, the app checks for updates 2 seconds after launch
- **Manual Check**: Users can check for updates via `Help → Check for Updates`

### Update Detection

The updater:
1. Queries the GitHub Releases API
2. Compares the latest release version with the current app version
3. Shows an update dialog if a newer version is available
4. Opens the release page in the browser when user clicks "Download Update"

### Update Dialog Features

- Shows current and latest version
- Displays release notes
- Warns if it's a pre-release
- Options to:
  - Download update (opens GitHub release page)
  - Remind later
  - Skip this version

## User Experience

### When Update is Available

1. User sees a dialog with:
   - New version number
   - Release notes
   - Download button
2. Clicking "Download Update" opens the GitHub release page
3. User downloads and installs manually

### When No Update Available

- Manual check: Shows "You are using the latest version" message
- Automatic check: No notification (silent)

## Troubleshooting

### Update Check Fails

**Error**: "GitHub repository not configured"
- **Solution**: Set `GITHUB_REPO_OWNER` and `GITHUB_REPO_NAME` in `.env` or `config.py`

**Error**: "Network error checking for updates"
- **Solution**: Check your internet connection
- The app will continue to work normally if update check fails

**Error**: "Invalid version format"
- **Solution**: Ensure your release tags follow semantic versioning (e.g., `v1.0.0`)

### Updates Not Detected

1. **Check version format**: Release tag must be parseable (e.g., `v1.0.0`)
2. **Check current version**: Update `APP_VERSION` in `config.py` to match your latest release
3. **Check API access**: Ensure the repository is public or you have proper authentication

## Advanced Configuration

### Disable Auto-Check

Set in `.env`:
```env
CHECK_UPDATES_ON_STARTUP=false
AUTO_CHECK_UPDATES=false
```

### Custom Asset Download

The updater can find specific assets by pattern. Modify `get_download_url()` in `update_service.py`:

```python
# Example: Find Windows installer
download_url = update_service.get_download_url("windows.exe")
```

## Security Notes

- The updater only reads from GitHub's public API (no authentication required for public repos)
- No automatic installation - users must manually download and install
- All update checks are done over HTTPS
- The updater respects pre-release flags and won't auto-suggest pre-releases unless configured

## Future Enhancements

Potential improvements:
- Automatic download and installation
- Background update downloads
- Update notifications in system tray
- Delta updates (only download changes)
- Rollback functionality

