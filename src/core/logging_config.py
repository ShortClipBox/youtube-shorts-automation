import logging
import os
from . import config

def setup_logging():
    """
    Configures logging for the application.
    Logs to both a file and the console.
    (Currently a basic placeholder, as main.py uses basicConfig)
    """
    log_file = config.LOG_FILE
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logging.info("Logging configured.")

if __name__ == '__main__':
    setup_logging()
    logging.info("This is an info message.")
    logging.warning("This is a warning message.")
