from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.database import User as DBUser
from app.models.schemas import User, UserCreate, UserUpdate, Token, TokenData
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    verify_token
)
from app.core.config import settings

router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_user_by_email(db: Session, email: str) -> Optional[DBUser]:
    """Get user by email"""
    return db.query(DBUser).filter(DBUser.email == email).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[DBUser]:
    """Get user by ID"""
    return db.query(DBUser).filter(DBUser.id == user_id).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[DBUser]:
    """Authenticate user with email and password"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> DBUser:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_id = verify_token(token)
    if user_id is None:
        raise credentials_exception
    
    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(current_user: DBUser = Depends(get_current_user)) -> DBUser:
    """Get current active user"""
    if not current_user:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if user already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = DBUser(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return User(
        id=db_user.id,
        name=db_user.name,
        email=db_user.email,
        role=db_user.role,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at
    )


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login user and return access token"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get current user information"""
    return User(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: DBUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Handle password update separately
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Check if email is being updated and if it's already taken
    if "email" in update_data and update_data["email"] != current_user.email:
        existing_user = get_user_by_email(db, update_data["email"])
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Update user
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return User(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: DBUser = Depends(get_current_active_user)
):
    """Refresh access token"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=current_user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
