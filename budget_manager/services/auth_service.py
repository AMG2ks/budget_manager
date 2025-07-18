"""
Authentication service for user management.
Handles user registration, login, and session management.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..core.database import DatabaseManager
from ..core.models import User, UserCreate, UserLogin, UserProfile


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass


class AuthService:
    """Service for handling user authentication and management."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize authentication service.
        
        Args:
            db_manager: Database manager instance. If None, creates a new one.
        """
        self.db_manager = db_manager or DatabaseManager()
    
    def register_user(self, user_data: UserCreate) -> UserProfile:
        """
        Register a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            UserProfile: Created user profile
            
        Raises:
            AuthenticationError: If username or email already exists
        """
        with self.db_manager.get_session() as session:
            try:
                # Check if username or email already exists
                existing_user = session.query(User).filter(
                    (User.username == user_data.username) | 
                    (User.email == user_data.email)
                ).first()
                
                if existing_user:
                    if existing_user.username == user_data.username:
                        raise AuthenticationError("Username already exists")
                    else:
                        raise AuthenticationError("Email already exists")
                
                # Create new user
                db_user = User(
                    username=user_data.username,
                    email=user_data.email,
                    full_name=user_data.full_name
                )
                
                # Set password (this will hash it)
                db_user.set_password(user_data.password)
                
                session.add(db_user)
                session.commit()
                session.refresh(db_user)
                
                return UserProfile.from_orm(db_user)
                
            except IntegrityError:
                session.rollback()
                raise AuthenticationError("Username or email already exists")
    
    def login_user(self, login_data: UserLogin) -> UserProfile:
        """
        Authenticate and login a user.
        
        Args:
            login_data: User login credentials
            
        Returns:
            UserProfile: User profile if authentication successful
            
        Raises:
            AuthenticationError: If credentials are invalid
        """
        with self.db_manager.get_session() as session:
            # Find user by username
            user = session.query(User).filter(
                User.username == login_data.username,
                User.is_active == True
            ).first()
            
            if not user:
                raise AuthenticationError("Invalid username or password")
            
            # Check password
            if not user.check_password(login_data.password):
                raise AuthenticationError("Invalid username or password")
            
            # Update last login
            user.update_last_login()
            session.commit()
            
            return UserProfile.from_orm(user)
    
    def get_user_by_id(self, user_id: int) -> Optional[UserProfile]:
        """
        Get user profile by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            UserProfile or None if not found
        """
        with self.db_manager.get_session() as session:
            user = session.query(User).filter(
                User.id == user_id,
                User.is_active == True
            ).first()
            
            if user:
                return UserProfile.from_orm(user)
            return None
    
    def get_user_by_username(self, username: str) -> Optional[UserProfile]:
        """
        Get user profile by username.
        
        Args:
            username: Username
            
        Returns:
            UserProfile or None if not found
        """
        with self.db_manager.get_session() as session:
            user = session.query(User).filter(
                User.username == username,
                User.is_active == True
            ).first()
            
            if user:
                return UserProfile.from_orm(user)
            return None
    
    def update_user_profile(self, user_id: int, updates: Dict[str, Any]) -> Optional[UserProfile]:
        """
        Update user profile information.
        
        Args:
            user_id: User ID
            updates: Dictionary of fields to update
            
        Returns:
            Updated UserProfile or None if user not found
        """
        with self.db_manager.get_session() as session:
            user = session.query(User).filter(
                User.id == user_id,
                User.is_active == True
            ).first()
            
            if not user:
                return None
            
            # Update allowed fields
            allowed_fields = {'full_name', 'email'}
            for field, value in updates.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, value)
            
            session.commit()
            session.refresh(user)
            
            return UserProfile.from_orm(user)
    
    def reset_password(self, username: str, email: str, new_password: str) -> bool:
        """
        Reset user password using username and email verification.
        
        Args:
            username: Username
            email: Email for verification
            new_password: New password
            
        Returns:
            True if password reset successfully
            
        Raises:
            AuthenticationError: If username/email combination is invalid
        """
        with self.db_manager.get_session() as session:
            user = session.query(User).filter(
                User.username == username,
                User.email == email,
                User.is_active == True
            ).first()
            
            if not user:
                raise AuthenticationError("Invalid username or email combination")
            
            # Set new password
            user.set_password(new_password)
            session.commit()
            
            return True

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User ID
            current_password: Current password for verification
            new_password: New password
            
        Returns:
            True if password changed successfully
            
        Raises:
            AuthenticationError: If current password is incorrect
        """
        with self.db_manager.get_session() as session:
            user = session.query(User).filter(
                User.id == user_id,
                User.is_active == True
            ).first()
            
            if not user:
                raise AuthenticationError("User not found")
            
            # Verify current password
            if not user.check_password(current_password):
                raise AuthenticationError("Current password is incorrect")
            
            # Set new password
            user.set_password(new_password)
            session.commit()
            
            return True
    
    def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            True if user was deactivated
        """
        with self.db_manager.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False
            
            user.is_active = False
            session.commit()
            
            return True
    
    def get_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user statistics.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user statistics or None if user not found
        """
        with self.db_manager.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return None
            
            return {
                'income_entries': len(user.income_entries),
                'total_expenses': len(user.expenses),
                'savings_goals': len(user.savings_goals),
                'days_since_registration': (datetime.utcnow() - user.created_at).days,
                'last_login': user.last_login
            }
    
    def get_all_users(self) -> list[UserProfile]:
        """
        Get all active users.
        
        Returns:
            List of all active user profiles
        """
        with self.db_manager.get_session() as session:
            users = session.query(User).filter(User.is_active == True).all()
            return [UserProfile.from_orm(user) for user in users]
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system-wide statistics.
        
        Returns:
            Dictionary with system statistics
        """
        with self.db_manager.get_session() as session:
            total_users = session.query(User).filter(User.is_active == True).count()
            total_income_entries = session.query(User).join(User.income_entries).count()
            total_expenses = session.query(User).join(User.expenses).count()
            total_savings_goals = session.query(User).join(User.savings_goals).count()
            
            return {
                'total_users': total_users,
                'total_income_entries': total_income_entries,
                'total_expenses': total_expenses,
                'total_savings_goals': total_savings_goals
            } 