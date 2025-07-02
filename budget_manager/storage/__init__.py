"""
Storage backends for Budget Manager.
Supports multiple storage options including PostgreSQL, SQLite, and GitHub.
"""

from .github_storage import GitHubStorageAdapter, GITHUB_SETUP_INSTRUCTIONS

__all__ = ['GitHubStorageAdapter', 'GITHUB_SETUP_INSTRUCTIONS'] 