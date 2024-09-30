from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import User
from dependencies import get_current_user
from utils.jwt import create_access_token
from utils.password import verify_password
from schemas.user import UserCreate, UserResponse
from utils.password import hash_password
from utils.logger import logger

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/register",
    response_model=dict,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Username already exists"}
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal server error"}
                }
            },
        },
        status.HTTP_201_CREATED: {
            "description": "User Registered Successfully",
            "content": {
                "application/json": {
                    "example": {"message": "User registered successfully"}
                }
            },
        },
    },
)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Validate inputs
        if not user.username or not user.password or not user.full_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All fields are required: username, password, full_name."
            )
        
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Hash the password
        hashed_password = hash_password(user.password)

        # Create a new user instance
        new_user = User(username=user.username, hashed_password=hashed_password, full_name=user.full_name)

        # Add to the database and commit
        db.add(new_user)
        db.commit()
        # Optionally refresh if you need any auto-generated field values
        # db.refresh(new_user)

        logger.info(f"User {user.username} registered successfully.")
        return {"message": "User registered successfully"}
    except HTTPException as e:
        # Let FastAPI handle the HTTPExceptions directly
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during user registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post(
    "/login",
    response_model=dict,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect username or password"}
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal server error"}
                }
            },
        },
        status.HTTP_200_OK: {
            "description": "Login Successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "your-jwt-token",
                        "token_type": "bearer"
                    }
                }
            },
        },
    },
)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(),
               db: Session = Depends(get_db)):
    try:
        # Validate inputs
        if not form_data.username or not form_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and password are required."
            )
        
        # Check if user exists
        db_user = db.query(User).filter(User.username == form_data.username).first()
        if not db_user or not verify_password(form_data.password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect username or password"
            )

        # Create JWT token with username and full_name
        access_token = create_access_token(
            data={"username": db_user.username, "full_name": db_user.full_name}
        )

        logger.info(f"User {form_data.username} logged in successfully.")
        
        # Return token
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException as e:
        # Let FastAPI handle the HTTPExceptions directly
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during user login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get(
    "/user",
    response_model=UserResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "User Retrieved Successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "user_username",
                        "full_name": "user_full_name",
                        "last_read_chat_history_id": None
                    }
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal server error"}
                }
            },
        },
    },
)
def get_user_info(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Fetch the user from the database using username
        db_user = db.query(User).filter(User.username == current_user["username"]).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Build response with necessary fields
        return {
            "id": db_user.id,
            "username": db_user.username,
            "full_name": db_user.full_name,
            "last_read_chat_history_id": db_user.last_read_chat_history_id
        }
    except HTTPException as e:
        # Let FastAPI handle the HTTPExceptions directly
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during user retrieval: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
