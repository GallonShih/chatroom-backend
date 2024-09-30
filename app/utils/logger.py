import logging
import os

# Get log level from environment variable, default to "INFO"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Create a logger object
logger = logging.getLogger("app_logger")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

# Prevent adding multiple handlers if the logger already has one
if not logger.handlers:
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # Define a log format with thread, file, and function information
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(filename)s - %(funcName)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Add the formatter to the console handler
    console_handler.setFormatter(formatter)

    # Add the console handler to the logger
    logger.addHandler(console_handler)
