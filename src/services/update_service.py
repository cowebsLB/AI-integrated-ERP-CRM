"""
Auto-updater service that checks for updates from GitHub releases.
"""
import logging
import json
import re
from typing import Optional, Dict, Any
from pathlib import Path
from packaging import version
import requests
from PyQt6.QtCore import QObject, pyqtSignal, QThread

import config

logger = logging.getLogger(__name__)


class UpdateChecker(QThread):
    """Thread for checking updates without blocking the UI."""
    
    update_available = pyqtSignal(dict)  # Emits update info if available
    check_complete = pyqtSignal(bool)  # Emits True if update available, False otherwise
    error_occurred = pyqtSignal(str)  # Emits error message
    
    def __init__(self, repo_owner: str, repo_name: str, current_version: str):
        super().__init__()
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        self.latest_release = None
    
    def run(self):
        """Check for updates in background thread."""
        try:
            latest_release = self.check_for_updates()
            if latest_release:
                self.latest_release = latest_release
                self.update_available.emit(latest_release)
                self.check_complete.emit(True)
            else:
                self.check_complete.emit(False)
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            self.error_occurred.emit(str(e))
            self.check_complete.emit(False)
    
    def check_for_updates(self) -> Optional[Dict[str, Any]]:
        """Check GitHub releases for updates."""
        try:
            # GitHub API endpoint for releases
            api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
            
            logger.info(f"Checking for updates at: {api_url}")
            
            # Make request with timeout
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            
            # Extract version from tag name (e.g., "v1.0.0" -> "1.0.0")
            tag_name = release_data.get("tag_name", "")
            latest_version = re.sub(r'^v', '', tag_name, flags=re.IGNORECASE)
            
            if not latest_version:
                logger.warning("No version tag found in release")
                return None
            
            # Compare versions
            try:
                # Handle version strings that might not be valid
                current_ver = version.parse(self.current_version)
                latest_ver = version.parse(latest_version)
                
                if latest_ver > current_ver:
                    logger.info(f"Update available: {self.current_version} -> {latest_version}")
                    return {
                        "version": latest_version,
                        "tag_name": tag_name,
                        "name": release_data.get("name", ""),
                        "body": release_data.get("body", ""),
                        "published_at": release_data.get("published_at", ""),
                        "html_url": release_data.get("html_url", ""),
                        "assets": release_data.get("assets", []),
                        "prerelease": release_data.get("prerelease", False),
                        "draft": release_data.get("draft", False)
                    }
                else:
                    logger.info(f"Already on latest version: {self.current_version}")
                    return None
                    
            except version.InvalidVersion as e:
                logger.error(f"Invalid version format: {e}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error checking for updates: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error checking for updates: {e}")
            raise


class UpdateService(QObject):
    """Service for managing application updates."""
    
    def __init__(self, repo_owner: str = None, repo_name: str = None):
        super().__init__()
        self.repo_owner = repo_owner or getattr(config, 'GITHUB_REPO_OWNER', '')
        self.repo_name = repo_name or getattr(config, 'GITHUB_REPO_NAME', '')
        self.current_version = config.APP_VERSION
        self.update_checker = None
        self.latest_release = None
    
    def check_for_updates(self, callback=None) -> Optional[Dict[str, Any]]:
        """Check for updates synchronously (blocking)."""
        if not self.repo_owner or not self.repo_name:
            logger.warning("GitHub repository not configured")
            return None
        
        try:
            api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            tag_name = release_data.get("tag_name", "")
            latest_version = re.sub(r'^v', '', tag_name, flags=re.IGNORECASE)
            
            if not latest_version:
                return None
            
            current_ver = version.parse(self.current_version)
            latest_ver = version.parse(latest_version)
            
            if latest_ver > current_ver:
                self.latest_release = {
                    "version": latest_version,
                    "tag_name": tag_name,
                    "name": release_data.get("name", ""),
                    "body": release_data.get("body", ""),
                    "published_at": release_data.get("published_at", ""),
                    "html_url": release_data.get("html_url", ""),
                    "assets": release_data.get("assets", []),
                    "prerelease": release_data.get("prerelease", False),
                    "draft": release_data.get("draft", False)
                }
                return self.latest_release
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            if callback:
                callback(None, str(e))
            return None
    
    def check_for_updates_async(self, on_update_available=None, on_check_complete=None, on_error=None):
        """Check for updates asynchronously (non-blocking)."""
        if not self.repo_owner or not self.repo_name:
            logger.warning("GitHub repository not configured")
            if on_error:
                on_error("GitHub repository not configured")
            return
        
        # Create and start update checker thread
        self.update_checker = UpdateChecker(self.repo_owner, self.repo_name, self.current_version)
        
        if on_update_available:
            self.update_checker.update_available.connect(on_update_available)
        if on_check_complete:
            self.update_checker.check_complete.connect(on_check_complete)
        if on_error:
            self.update_checker.error_occurred.connect(on_error)
        
        self.update_checker.start()
    
    def get_download_url(self, asset_name_pattern: str = None) -> Optional[str]:
        """Get download URL for the latest release asset."""
        if not self.latest_release:
            return None
        
        assets = self.latest_release.get("assets", [])
        if not assets:
            # Return the release page URL if no assets
            return self.latest_release.get("html_url")
        
        if asset_name_pattern:
            # Find asset matching pattern
            for asset in assets:
                if asset_name_pattern.lower() in asset.get("name", "").lower():
                    return asset.get("browser_download_url")
        
        # Return first asset if no pattern specified
        return assets[0].get("browser_download_url") if assets else None
    
    def is_update_available(self) -> bool:
        """Check if an update is available."""
        return self.latest_release is not None

