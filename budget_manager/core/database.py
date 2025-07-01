"""
Database management for the budget management application.
"""

import os
from pathlib import Path
from typing import Optional, List, Type, TypeVar
from contextlib import contextmanager

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .models import Base, IncomeEntryDB, ExpenseDB, SavingsGoalDB, User

T = TypeVar('T')


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Custom database path. If None, uses default location.
        """
        if db_path is None:
            # Try to use user's home directory, fall back to current directory for deployment
            try:
                import os
                if os.environ.get('STREAMLIT_CLOUD_DEPLOYMENT'):
                    # For Streamlit Cloud deployment, use current directory
                    data_dir = Path("./data")
                else:
                    # For local development, use home directory
                    data_dir = Path.home() / ".budget_manager"
                
                data_dir.mkdir(exist_ok=True)
                db_path = str(data_dir / "budget.db")
            except (PermissionError, OSError):
                # Fallback to current directory if home directory isn't accessible
                data_dir = Path("./data")
                data_dir.mkdir(exist_ok=True)
                db_path = str(data_dir / "budget.db")
        
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables if they don't exist
        self.create_tables()
    
    def create_tables(self) -> None:
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to create database tables: {e}")
    
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