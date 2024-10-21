import uuid
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from confluent_kafka import KafkaException, KafkaError
from db.database import SessionLocal
from db.models import User
from utils.logger import logger
# from utils.kafka import create_kafka_consumer
from utils.kafka import create_aiokafka_consumer

import json

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.websocket("/ws/chat/{username}")
async def websocket_endpoint(
    websocket: WebSocket, 
    username: str,
    db: Session = Depends(get_db)
):
    # Check if user exists in the database
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.error(f"User {username} not found in database, closing connection.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Accept WebSocket connection
    await websocket.accept()
    logger.info(f"WebSocket connection established for user {username}")

    # Generate a unique group_id for each connection
    group_id = f"{username}-{uuid.uuid4()}"
    
    # Create AIOKafka consumer for chatroom_topic using unique group_id
    consumer = await create_aiokafka_consumer(group_id)

    last_read_id = None  # Track the last message ID received

    try:
        # Start a task to consume messages from Kafka and send to WebSocket
        async def consume_kafka_messages():
            nonlocal last_read_id  # Ensure we modify the outer scope variable
            async for msg in consumer:
                message = msg.value.decode('utf-8')
                message_data = json.loads(message)
                last_read_id = message_data.get("chat_id")
                logger.info(f"Message data: {message_data}")

                # Send Kafka message to WebSocket client
                await websocket.send_text(message)

        # Start the Kafka consuming task
        kafka_task = asyncio.create_task(consume_kafka_messages())

        # Continuously receive messages from the WebSocket client
        while True:
            # Wait for a message from the WebSocket client
            client_message = await websocket.receive_text()
            logger.info(f"Received message from client {username}: {client_message}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {username}")

    except Exception as e:
        logger.error(f"Unexpected error in WebSocket: {e}")

    finally:
        # Update the user's last read message ID in the database
        if last_read_id:
            try:
                db_user.last_read_chat_history_id = max(last_read_id, db_user.last_read_chat_history_id or 0)
                db.commit()
                logger.info(f"Updated last_read_chat_history_id to {last_read_id} for user {username}")
            except SQLAlchemyError as db_error:
                logger.error(f"Database error while updating last read message ID: {db_error}")
            except Exception as e:
                logger.error(f"Unexpected error while updating last read message ID: {e}")
        # Close Kafka consumer and Kafka task
        await consumer.stop()
        kafka_task.cancel()  # Cancel the Kafka consuming task
        logger.info(f"Kafka consumer stopped for user {username}")
