import os
import json
from aiokafka import AIOKafkaConsumer
from aiokafka.structs import TopicPartition
from confluent_kafka import Producer, Consumer
import asyncio
from utils.logger import logger


# Kafka producer configuration
KAFKA_PRODUCER_CONFIG = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
    'acks': os.getenv('KAFKA_ACKS', 'all'),
    'retries': int(os.getenv('KAFKA_RETRIES', 5)),
    'linger.ms': int(os.getenv('KAFKA_LINGER_MS', 5)),
    'batch.size': int(os.getenv('KAFKA_BATCH_SIZE', 16384)),
    'compression.type': os.getenv('KAFKA_COMPRESSION_TYPE', 'gzip'),
    'enable.idempotence': os.getenv('KAFKA_ENABLE_IDEMPOTENCE', 'False').lower() == 'true'
}

# Kafka consumer configuration
KAFKA_CONSUMER_CONFIG = {
    'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
    'auto_offset_reset': 'earliest',
}

# Kafka topic
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'chatroom_topic')
# Offset adjustment (default to 30 if not set in environment)
OFFSET_ADJUSTMENT = int(os.getenv('KAFKA_OFFSET_ADJUSTMENT', 30))

# Create Kafka producer
producer = Producer(KAFKA_PRODUCER_CONFIG)

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def send_to_kafka(topic: str, message: dict):
    try:
        message_value = json.dumps(message)
        producer.produce(topic, message_value, callback=delivery_report)
        producer.poll(0)  # Non-blocking to trigger delivery reports
        logger.info(f"Message sent to Kafka topic {topic}: {message}")
    except Exception as e:
        logger.error(f"Failed to send message to Kafka: {e}")


async def create_aiokafka_consumer(group_id: str):
    # Create Kafka consumer
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        group_id=group_id,
        **KAFKA_CONSUMER_CONFIG
    )
    await consumer.start()
    logger.info(f"AIOKafka consumer created with group_id '{group_id}' subscribed to topic '{KAFKA_TOPIC}'")

    # Get the partition information for the topic (remove await)
    partitions = consumer.partitions_for_topic(KAFKA_TOPIC)
    if partitions:
        for partition in partitions:
            tp = TopicPartition(KAFKA_TOPIC, partition)

            # Get the current latest offset for the partition
            end_offset = await consumer.end_offsets([tp])
            latest_offset = end_offset[tp]
            logger.info(f"Latest offset for partition {partition}: {latest_offset}")

            # Calculate the -30 offset, starting from the earliest offset if insufficient
            seek_offset = max(latest_offset - OFFSET_ADJUSTMENT, 0)
            logger.info(f"Seeking to offset {seek_offset} for partition {partition}")

            # Seek to the calculated offset for the partition (remove await)
            consumer.seek(tp, seek_offset)
            current_offset = await consumer.position(tp)
            logger.info(f"Current offset for partition {partition}: {current_offset}")

    return consumer