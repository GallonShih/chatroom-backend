from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from db.database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "chatroom"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_read_chat_history_id = Column(Integer, ForeignKey('chatroom.chat_history.id'), nullable=True)

    # One-to-many relationship with chat history
    chat_histories = relationship(
        'ChatHistory',
        back_populates='user',
        foreign_keys='ChatHistory.user_id'  # Specify the foreign key for the relationship
    )

    # Optional: Relationship to access the last read chat history object
    last_read_chat_history = relationship(
        'ChatHistory',
        foreign_keys=[last_read_chat_history_id]
    )

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    __table_args__ = {"schema": "chatroom"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('chatroom.users.id'), nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))

    # Many-to-one relationship with user
    user = relationship(
        'User',
        back_populates='chat_histories',
        foreign_keys=[user_id]  # Specify the foreign key for the relationship
    )