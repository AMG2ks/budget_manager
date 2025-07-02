"""
Database management for the budget management application.
Enhanced with PostgreSQL support for persistent cloud storage.
"""

import os
from pathlib import Path
from typing import Optional, List, Type, TypeVar
from contextlib import contextmanager
import time

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.pool import QueuePool

from .models import Base, IncomeEntryDB, ExpenseDB, SavingsGoalDB, User

T = TypeVar('T')


class DatabaseManager:
    """Manages database connections and operations with PostgreSQL and SQLite support."""
    
    def __init__(self, db_url: Optional[str] = None):
        """
        Initialize database manager with support for PostgreSQL and SQLite.
        
        Args:
            db_url: Custom database URL. If None, auto-detects from environment.
        """
        self.db_url = db_url or self._get_database_url()
        self.is_postgres = self.db_url.startswith('postgresql')
        
        # Create engine with appropriate configuration
        if self.is_postgres:
            self.engine = create_engine(
                self.db_url,
                echo=False,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=300,
                connect_args={
                    "connect_timeout": 10,
                    "application_name": "budget_manager"
                }
            )
        else:
            # SQLite configuration
            self.engine = create_engine(
                self.db_url, 
                echo=False,
                connect_args={"check_same_thread": False} if "sqlite" in self.db_url else {}
            )
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables if they don't exist
        self._create_tables_with_retry()
    
    def _get_database_url(self) -> str:
        """
        Get database URL from environment or default to SQLite.
        
        Returns:
            Database URL string
        """
        # Check for PostgreSQL URL first (for cloud deployment)
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            # Fix Heroku/Render PostgreSQL URL format if needed
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            return database_url
        
        # Fall back to SQLite for local development
        return self._get_sqlite_url()
    
    def _get_sqlite_url(self) -> str:
        """Get SQLite database URL based on environment."""
        try:
            if os.environ.get('STREAMLIT_CLOUD_DEPLOYMENT'):
                # For Streamlit Cloud deployment, use current directory
                data_dir = Path("./data")
            else:
                # For local development, use home directory
                data_dir = Path.home() / ".budget_manager"
            
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / "budget.db"
            return f"sqlite:///{db_path}"
        except (PermissionError, OSError):
            # Fallback to current directory if home directory isn't accessible
            data_dir = Path("./data")
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / "budget.db"
            return f"sqlite:///{db_path}"
    
    def _create_tables_with_retry(self, max_retries: int = 3) -> None:
        """Create database tables with retry logic for cloud databases."""
        for attempt in range(max_retries):
            try:
                Base.metadata.create_all(bind=self.engine)
                return
            except OperationalError as e:
                if attempt < max_retries - 1 and self.is_postgres:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise DatabaseError(f"Failed to create database tables after {max_retries} attempts: {e}")
            except SQLAlchemyError as e:
                raise DatabaseError(f"Failed to create database tables: {e}")
    
    def get_connection_info(self) -> dict:
        """
        Get information about the current database connection.
        
        Returns:
            Dictionary with connection details
        """
        return {
            'database_type': 'PostgreSQL' if self.is_postgres else 'SQLite',
            'is_persistent': self.is_postgres,
            'url_masked': self._mask_db_url(self.db_url),
            'cloud_ready': self.is_postgres
        }
    
    def _mask_db_url(self, url: str) -> str:
        """Mask sensitive parts of database URL for logging."""
        if '://' not in url:
            return url
        
        protocol, rest = url.split('://', 1)
        if '@' in rest:
            credentials, host_part = rest.split('@', 1)
            return f"{protocol}://***:***@{host_part}"
        return f"{protocol}://{rest}"
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    @contextmanager
    def get_session(self):
        """
        Get a database session with automatic cleanup.
        
        Yields:
            Session: SQLAlchemy session object
            
        Raises:
            DatabaseError: If session creation or operation fails
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            session.close()
    
    def create(self, obj: Base) -> dict:
        """
        Create a new record in the database.
        
        Args:
            obj: Database model instance to create
            
        Returns:
            Dictionary with the created object data
            
        Raises:
            DatabaseError: If creation fails
        """
        with self.get_session() as session:
            session.add(obj)
            session.flush()  # Get the ID without committing
            session.refresh(obj)
            
            # Extract all attributes while session is active
            result = {}
            for column in obj.__table__.columns:
                result[column.name] = getattr(obj, column.name)
            
            return result
    
    def get_by_id(self, model: Type[T], obj_id: int) -> Optional[T]:
        """
        Get a record by ID.
        
        Args:
            model: Database model class
            obj_id: Record ID
            
        Returns:
            Model instance or None if not found
        """
        with self.get_session() as session:
            return session.query(model).filter(model.id == obj_id).first()
    
    def get_all(self, model: Type[T], limit: Optional[int] = None) -> List[dict]:
        """
        Get all records of a model type.
        
        Args:
            model: Database model class
            limit: Maximum number of records to return
            
        Returns:
            List of dictionaries with model data
        """
        with self.get_session() as session:
            query = session.query(model)
            if limit:
                query = query.limit(limit)
            objects = query.all()
            
            # Convert to dictionaries while session is active
            results = []
            for obj in objects:
                result = {}
                for column in obj.__table__.columns:
                    result[column.name] = getattr(obj, column.name)
                results.append(result)
            
            return results
    
    def filter_by(self, model: Type[T], **filters) -> List[dict]:
        """
        Filter records by given criteria.
        
        Args:
            model: Database model class
            **filters: Filter criteria as keyword arguments
            
        Returns:
            List of dictionaries with model data
        """
        with self.get_session() as session:
            objects = session.query(model).filter_by(**filters).all()
            
            # Convert to dictionaries while session is active
            results = []
            for obj in objects:
                result = {}
                for column in obj.__table__.columns:
                    result[column.name] = getattr(obj, column.name)
                results.append(result)
            
            return results
    
    def update(self, model: Type[T], obj_id: int, **updates) -> Optional[dict]:
        """
        Update a record by ID.
        
        Args:
            model: Database model class
            obj_id: Record ID
            **updates: Fields to update as keyword arguments
            
        Returns:
            Updated model data as dictionary or None if not found
        """
        with self.get_session() as session:
            obj = session.query(model).filter(model.id == obj_id).first()
            if obj:
                for key, value in updates.items():
                    if hasattr(obj, key):
                        setattr(obj, key, value)
                session.flush()
                session.refresh(obj)
                
                # Convert to dictionary while session is active
                result = {}
                for column in obj.__table__.columns:
                    result[column.name] = getattr(obj, column.name)
                
                return result
            return None
    
    def delete(self, model: Type[T], obj_id: int) -> bool:
        """
        Delete a record by ID.
        
        Args:
            model: Database model class
            obj_id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        with self.get_session() as session:
            obj = session.query(model).filter(model.id == obj_id).first()
            if obj:
                session.delete(obj)
                return True
            return False
    
    def execute_query(self, query_func, *args, **kwargs):
        """
        Execute a custom query function.
        
        Args:
            query_func: Function that takes a session and returns results
            *args, **kwargs: Arguments to pass to query_func
            
        Returns:
            Query results
        """
        with self.get_session() as session:
            return query_func(session, *args, **kwargs)


class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass 