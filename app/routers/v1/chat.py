from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from db.database import SessionLocal
from db.models import User, ChatHistory
from schemas.chat import ChatCreate
from utils.logger import logger
from utils.kafka import send_to_kafka
from dependencies import get_current_user

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/chat",
    response_model=dict,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Message stored successfully",
            "content": {
                "application/json": {
                    "example": {
                        "chat_id": 1,
                        "user_id": 1,
                        "username": "john_doe",
                        "full_name": "John Doe",
                        "message": "Hello, world!",
                        "timestamp": "2023-09-30T12:34:56.789Z"
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
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal server error"}
                }
            },
        },
    },
)
def create_chat_message(
    chat: ChatCreate, 
    current_user: dict = Depends(get_current_user),  # Validate JWT token and extract user info
    db: Session = Depends(get_db)
):
    try:
        # Ensure the username from JWT matches the user sending the message
        db_user = db.query(User).filter(User.id == chat.user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if db_user.username != current_user["username"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token username does not match the user"
            )

        # Create a new chat message
        new_chat = ChatHistory(
            user_id=chat.user_id,
            message=chat.message,
            timestamp=datetime.now(timezone.utc)  # Store the current time as UTC
        )

        # Add new chat message to the database and commit
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)

        logger.info(f"Message from user {chat.user_id} stored successfully.")

        # Prepare the response payload
        response_payload = {
            "chat_id": new_chat.id,
            "user_id": db_user.id,
            "username": db_user.username,
            "full_name": db_user.full_name,
            "message": new_chat.message,
            "timestamp": new_chat.timestamp.isoformat()
        }

        # Send the chat message to Kafka
        send_to_kafka("chatroom_topic", response_payload)

        return response_payload
    
    except HTTPException as e:
        # Handle HTTP exceptions explicitly
        raise e
    except Exception as e:
        # Log and raise internal server errors
        logger.error(f"Unexpected error while storing message or sending to Kafka: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
