"""
JWT Authentication Service
Handles token generation, validation, and user authentication.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_db
from app.models.user import User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class JWTService:
    """
    JWT token management and user authentication.
    """

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password."""
        async for db in get_db():
            try:
                query = select(User).where(User.username == username)
                result = await db.execute(query)
                user = result.scalar_one_or_none()

                if user and JWTService.verify_password(password, user.hashed_password):
                    return user
                return None
            except Exception as e:
                print(f"Authentication error: {str(e)}")
                return None

    @staticmethod
    async def get_current_user(token: str) -> Optional[User]:
        """Get current user from JWT token."""
        payload = JWTService.verify_token(token)
        if not payload:
            return None

        username = payload.get("sub")
        if not username:
            return None

        async for db in get_db():
            try:
                query = select(User).where(User.username == username)
                result = await db.execute(query)
                user = result.scalar_one_or_none()
                return user
            except Exception as e:
                print(f"User lookup error: {str(e)}")
                return None

    @staticmethod
    async def create_user(username: str, email: str, password: str, role: str = "user") -> Optional[User]:
        """Create a new user."""
        async for db in get_db():
            try:
                # Check if user exists
                existing = await db.execute(select(User).where(
                    (User.username == username) | (User.email == email)
                ))
                if existing.scalar_one_or_none():
                    return None

                hashed_password = JWTService.hash_password(password)
                user = User(
                    username=username,
                    email=email,
                    hashed_password=hashed_password,
                    role=role
                )

                db.add(user)
                await db.commit()
                await db.refresh(user)
                return user

            except Exception as e:
                await db.rollback()
                print(f"User creation error: {str(e)}")
                return None