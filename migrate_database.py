#!/usr/bin/env python3
"""
Database Migration Script for Multi-User Support
Adds user_id columns to existing tables and migrates data.
"""

import sys
from pathlib import Path
from datetime import datetime

from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

from budget_manager.core.database import DatabaseManager
from budget_manager.services.auth_service import AuthService, AuthenticationError
from budget_manager.core.models import UserCreate


def check_column_exists(engine, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    inspector = inspect(engine)
    try:
        columns = inspector.get_columns(table_name)
        return any(col['name'] == column_name for col in columns)
    except:
        return False


def check_table_exists(engine, table_name: str) -> bool:
    """Check if a table exists."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def create_default_user(auth_service: AuthService) -> int:
    """Create a default user for migrating existing data."""
    try:
        # Check if default user already exists
        existing_user = auth_service.get_user_by_username("default_user")
        if existing_user:
            print(f"✅ Default user already exists: {existing_user.username} (ID: {existing_user.id})")
            return existing_user.id
        
        # Create default user
        default_user_data = UserCreate(
            username="default_user",
            email="default@budgetmanager.local",
            password="changeme123",
            full_name="Default User (Migration)"
        )
        
        user_profile = auth_service.register_user(default_user_data)
        print(f"✅ Created default user: {user_profile.username} (ID: {user_profile.id})")
        print(f"   📧 Email: {user_profile.email}")
        print(f"   🔑 Password: changeme123 (please change this after migration)")
        
        return user_profile.id
        
    except AuthenticationError as e:
        print(f"❌ Failed to create default user: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error creating default user: {e}")
        return None


def migrate_table_add_user_id(engine, table_name: str, default_user_id: int) -> bool:
    """Add user_id column to a table and assign existing data to default user."""
    try:
        with engine.connect() as conn:
            trans = conn.begin()
            
            try:
                # Check if user_id column already exists
                if check_column_exists(engine, table_name, 'user_id'):
                    print(f"✅ Table '{table_name}' already has user_id column")
                    return True
                
                print(f"🔧 Adding user_id column to '{table_name}' table...")
                
                # Add user_id column
                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN user_id INTEGER"))
                
                # Update existing records to belong to default user
                result = conn.execute(text(f"UPDATE {table_name} SET user_id = :user_id WHERE user_id IS NULL"), 
                                    {"user_id": default_user_id})
                
                updated_rows = result.rowcount
                if updated_rows > 0:
                    print(f"   📊 Assigned {updated_rows} existing records to default user")
                
                trans.commit()
                print(f"✅ Successfully migrated '{table_name}' table")
                return True
                
            except Exception as e:
                trans.rollback()
                raise e
            
    except Exception as e:
        print(f"❌ Failed to migrate '{table_name}' table: {e}")
        return False


def verify_migration(engine) -> bool:
    """Verify that the migration was successful."""
    try:
        tables_to_check = ['expenses', 'income_entries', 'savings_goals']
        
        for table_name in tables_to_check:
            if not check_table_exists(engine, table_name):
                continue  # Skip if table doesn't exist yet
                
            if not check_column_exists(engine, table_name, 'user_id'):
                print(f"❌ Migration failed: '{table_name}' table missing user_id column")
                return False
        
        # Test a simple query
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) as count FROM users"))
            user_count = result.fetchone()[0]
            print(f"✅ Migration verification passed - {user_count} users in database")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration verification failed: {e}")
        return False


def backup_database(db_manager: DatabaseManager) -> bool:
    """Create a backup of the database before migration."""
    try:
        if not db_manager.db_url.startswith('sqlite:///'):
            print("ℹ️  Backup only supported for SQLite databases")
            return True
        
        # Extract database path
        db_path = Path(db_manager.db_url.replace('sqlite:///', ''))
        if not db_path.exists():
            print("ℹ️  No existing database to backup")
            return True
        
        # Create backup
        backup_path = db_path.parent / f"{db_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Failed to create backup: {e}")
        return True  # Don't fail migration if backup fails


def main():
    """Main migration function."""
    print("🔄 Database Migration: Adding Multi-User Support")
    print("=" * 60)
    
    try:
        # Initialize database manager with simplified settings for migration
        print("🔧 Initializing database connection...")
        
        # Create a simpler database manager for migration
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        
        # Get database URL - check both possible SQLite locations
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            # Use SQLite path - check local data directory first, then home directory
            from pathlib import Path
            
            # Check if local data/budget.db exists (preferred for apps)
            local_data_dir = Path("./data")
            local_db_path = local_data_dir / "budget.db"
            
            # Check if home directory database exists
            home_data_dir = Path.home() / ".budget_manager"
            home_db_path = home_data_dir / "budget.db"
            
            if local_db_path.exists():
                print(f"📁 Using local database: {local_db_path}")
                database_url = f"sqlite:///{local_db_path}"
            elif home_db_path.exists():
                print(f"📁 Using home directory database: {home_db_path}")
                database_url = f"sqlite:///{home_db_path}"
            else:
                # Default to local data directory (create if needed)
                local_data_dir.mkdir(exist_ok=True)
                print(f"📁 Creating new database: {local_db_path}")
                database_url = f"sqlite:///{local_db_path}"
        
        print(f"📁 Database URL: {database_url}")
        
        # Create simple engine for migration
        engine = create_engine(database_url, echo=False)
        
        # Test connection
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Cannot connect to database: {e}")
            sys.exit(1)
        
        # Now create proper database manager and auth service
        db_manager = DatabaseManager()
        auth_service = AuthService()
        
        # Create backup
        print("\n📦 Creating backup...")
        backup_database(db_manager)
        
        # Check if users table exists
        if not check_table_exists(engine, 'users'):
            print("\n👥 Users table doesn't exist - creating new database schema...")
            # This will create all tables with proper schema
            from budget_manager.core.models import Base
            Base.metadata.create_all(bind=engine)
            print("✅ New database schema created successfully")
            return
        
        # Check if migration is needed
        tables_to_migrate = []
        for table_name in ['expenses', 'income_entries', 'savings_goals']:
            if check_table_exists(engine, table_name):
                if not check_column_exists(engine, table_name, 'user_id'):
                    tables_to_migrate.append(table_name)
        
        if not tables_to_migrate:
            print("\n✅ Database is already up to date - no migration needed!")
            return
        
        print(f"\n🔧 Migration needed for tables: {', '.join(tables_to_migrate)}")
        
        # Create default user for existing data
        print("\n👤 Setting up default user...")
        default_user_id = create_default_user(auth_service)
        if not default_user_id:
            print("❌ Cannot proceed without default user")
            sys.exit(1)
        
        # Migrate each table
        print(f"\n🚀 Starting migration...")
        migration_success = True
        
        for table_name in tables_to_migrate:
            if not migrate_table_add_user_id(engine, table_name, default_user_id):
                migration_success = False
        
        # Verify migration
        print(f"\n🔍 Verifying migration...")
        if verify_migration(engine):
            print("✅ Migration completed successfully!")
            
            print(f"\n📋 Migration Summary:")
            print(f"✅ Migrated {len(tables_to_migrate)} tables")
            print(f"✅ Created default user (ID: {default_user_id})")
            print(f"✅ All existing data preserved")
            
            print(f"\n🎯 Next Steps:")
            print(f"1. 🔑 Login with username: default_user, password: changeme123")
            print(f"2. 🆕 Create new user accounts for other people")
            print(f"3. 📊 Check that your existing data appears under default_user")
            print(f"4. 🔒 Change the default user password in Settings")
            
        else:
            print("❌ Migration failed verification")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Migration failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 