#!/usr/bin/env python3
"""
Backup and Restore System for Streamlit Cloud Deployments
Prevents data loss during redeployments by storing data in the repository.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Any

from sqlalchemy import text
from budget_manager.core.database import DatabaseManager
from budget_manager.services.auth_service import AuthService


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime and date objects."""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


class BackupRestoreSystem:
    """Handles backup and restore operations for the budget manager database."""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.auth_service = AuthService()
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self, filename: str = None) -> str:
        """
        Create a complete backup of the database to JSON.
        
        Args:
            filename: Custom filename for backup. If None, generates timestamped name.
            
        Returns:
            Path to the created backup file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"budget_backup_{timestamp}.json"
        
        backup_path = self.backup_dir / filename
        
        print(f"🗄️ Creating backup: {backup_path}")
        
        backup_data = {
            "metadata": {
                "backup_date": datetime.now().isoformat(),
                "version": "1.0",
                "database_type": self.db_manager.get_connection_info()["database_type"]
            },
            "data": {
                "users": self._backup_users(),
                "income_entries": self._backup_income_entries(),
                "expenses": self._backup_expenses(),
                "savings_goals": self._backup_savings_goals()
            }
        }
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
        
        # Also create a "latest" backup for easy deployment restoration
        latest_path = self.backup_dir / "latest_backup.json"
        shutil.copy2(backup_path, latest_path)
        
        print(f"✅ Backup created successfully!")
        print(f"   📁 Full backup: {backup_path}")
        print(f"   🔄 Latest backup: {latest_path}")
        
        return str(backup_path)
    
    def _backup_users(self) -> List[Dict[str, Any]]:
        """Backup all users (excluding sensitive password data)."""
        with self.db_manager.get_session() as session:
            result = session.execute(text("""
                SELECT id, username, email, full_name, created_at, last_login, is_active
                FROM users
                WHERE is_active = 1
            """))
            
            return [dict(row._mapping) for row in result]
    
    def _backup_income_entries(self) -> List[Dict[str, Any]]:
        """Backup all income entries."""
        with self.db_manager.get_session() as session:
            result = session.execute(text("""
                SELECT id, user_id, amount, month, description, created_at
                FROM income_entries
            """))
            
            return [dict(row._mapping) for row in result]
    
    def _backup_expenses(self) -> List[Dict[str, Any]]:
        """Backup all expenses."""
        with self.db_manager.get_session() as session:
            result = session.execute(text("""
                SELECT id, user_id, amount, description, category, expense_date, created_at
                FROM expenses
            """))
            
            return [dict(row._mapping) for row in result]
    
    def _backup_savings_goals(self) -> List[Dict[str, Any]]:
        """Backup all savings goals."""
        with self.db_manager.get_session() as session:
            result = session.execute(text("""
                SELECT id, user_id, target_amount, month, description, created_at
                FROM savings_goals
            """))
            
            return [dict(row._mapping) for row in result]
    
    def restore_from_backup(self, backup_file: str = None) -> bool:
        """
        Restore database from a backup file.
        
        Args:
            backup_file: Path to backup file. If None, uses latest_backup.json
            
        Returns:
            True if restore was successful
        """
        if backup_file is None:
            backup_file = self.backup_dir / "latest_backup.json"
        else:
            backup_file = Path(backup_file)
        
        if not backup_file.exists():
            print(f"❌ Backup file not found: {backup_file}")
            return False
        
        print(f"🔄 Restoring from backup: {backup_file}")
        
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Verify backup format
            if "metadata" not in backup_data or "data" not in backup_data:
                print("❌ Invalid backup file format")
                return False
            
            print(f"📅 Backup date: {backup_data['metadata']['backup_date']}")
            
            # Restore data
            self._restore_users(backup_data["data"]["users"])
            self._restore_income_entries(backup_data["data"]["income_entries"])
            self._restore_expenses(backup_data["data"]["expenses"])
            self._restore_savings_goals(backup_data["data"]["savings_goals"])
            
            print("✅ Database restored successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error restoring backup: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _restore_users(self, users_data: List[Dict[str, Any]]):
        """Restore users table."""
        print("👥 Restoring users...")
        
        with self.db_manager.get_session() as session:
            for user_data in users_data:
                # Check if user already exists
                existing = session.execute(text(
                    "SELECT id FROM users WHERE username = :username"
                ), {"username": user_data["username"]}).fetchone()
                
                if not existing:
                    # Create user with default password (they'll need to change it)
                    session.execute(text("""
                        INSERT INTO users (id, username, email, full_name, created_at, last_login, is_active, password_hash, salt)
                        VALUES (:id, :username, :email, :full_name, :created_at, :last_login, :is_active, 
                               'default_hash_needs_reset', 'default_salt')
                    """), user_data)
        
        print(f"   ✅ Restored {len(users_data)} users")
    
    def _restore_income_entries(self, income_data: List[Dict[str, Any]]):
        """Restore income entries."""
        print("💰 Restoring income entries...")
        
        with self.db_manager.get_session() as session:
            for entry in income_data:
                session.execute(text("""
                    INSERT OR REPLACE INTO income_entries (id, user_id, amount, month, description, created_at)
                    VALUES (:id, :user_id, :amount, :month, :description, :created_at)
                """), entry)
        
        print(f"   ✅ Restored {len(income_data)} income entries")
    
    def _restore_expenses(self, expenses_data: List[Dict[str, Any]]):
        """Restore expenses."""
        print("💸 Restoring expenses...")
        
        with self.db_manager.get_session() as session:
            for expense in expenses_data:
                session.execute(text("""
                    INSERT OR REPLACE INTO expenses (id, user_id, amount, description, category, expense_date, created_at)
                    VALUES (:id, :user_id, :amount, :description, :category, :expense_date, :created_at)
                """), expense)
        
        print(f"   ✅ Restored {len(expenses_data)} expenses")
    
    def _restore_savings_goals(self, goals_data: List[Dict[str, Any]]):
        """Restore savings goals."""
        print("🎯 Restoring savings goals...")
        
        with self.db_manager.get_session() as session:
            for goal in goals_data:
                session.execute(text("""
                    INSERT OR REPLACE INTO savings_goals (id, user_id, target_amount, month, description, created_at)
                    VALUES (:id, :user_id, :target_amount, :month, :description, :created_at)
                """), goal)
        
        print(f"   ✅ Restored {len(goals_data)} savings goals")
    
    def should_restore_on_startup(self) -> bool:
        """
        Check if we should restore from backup on startup.
        
        Returns:
            True if database is empty or missing critical data
        """
        try:
            with self.db_manager.get_session() as session:
                # Check if we have any users
                result = session.execute(text("SELECT COUNT(*) as count FROM users"))
                user_count = result.fetchone()[0]
                
                # Check if we have any financial data
                result = session.execute(text("""
                    SELECT 
                        (SELECT COUNT(*) FROM income_entries) as income_count,
                        (SELECT COUNT(*) FROM expenses) as expense_count,
                        (SELECT COUNT(*) FROM savings_goals) as goals_count
                """))
                counts = result.fetchone()
                
                # If no users or very little data, we should restore
                if user_count == 0 or (counts[0] + counts[1] + counts[2]) < 5:
                    return True
                
                return False
                
        except Exception as e:
            print(f"⚠️ Error checking database status: {e}")
            return True  # If we can't check, assume we need to restore
    
    def auto_restore_on_startup(self) -> bool:
        """
        Automatically restore from backup if needed on app startup.
        
        Returns:
            True if restoration was performed and successful
        """
        if not self.should_restore_on_startup():
            print("📊 Database has sufficient data, skipping auto-restore")
            return False
        
        print("🔄 Database appears empty, attempting auto-restore...")
        
        # Try to restore from latest backup
        return self.restore_from_backup()


def main():
    """Command line interface for backup operations."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python backup_system.py backup [filename]    # Create backup")
        print("  python backup_system.py restore [filename]   # Restore from backup")
        print("  python backup_system.py auto-restore         # Auto-restore if needed")
        sys.exit(1)
    
    command = sys.argv[1]
    backup_system = BackupRestoreSystem()
    
    if command == "backup":
        filename = sys.argv[2] if len(sys.argv) > 2 else None
        backup_system.create_backup(filename)
        
    elif command == "restore":
        filename = sys.argv[2] if len(sys.argv) > 2 else None
        success = backup_system.restore_from_backup(filename)
        sys.exit(0 if success else 1)
        
    elif command == "auto-restore":
        success = backup_system.auto_restore_on_startup()
        if success:
            print("✅ Auto-restore completed successfully")
        else:
            print("ℹ️ No restore needed or restore failed")
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
