from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError, OperationalError
from db.database import engine, Base
from db.models import ChatHistory, User
from utils.logger import logger


def create_schema_if_not_exists(schema_name="chatroom"):
    """
    Initialize the database by creating schema and tables.
    """
    with engine.connect() as connection:
        try:
            # Create schema if it does not exist
            logger.info(f"Attempting to create schema '{schema_name}'...")
            connection.execution_options(isolation_level="AUTOCOMMIT").execute(
                text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
            )
            logger.info(f"Schema '{schema_name}' created or already exists.")
        except ProgrammingError as e:
            logger.error(f"Error occurred while creating schema: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

def create_tables():
    """
    Create all tables based on the models defined.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("All tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")

def init_db():
    """
    Initialize the database by creating schema and tables.
    """
    schema_name = "chatroom"
    create_schema_if_not_exists(schema_name=schema_name)
    create_tables()
