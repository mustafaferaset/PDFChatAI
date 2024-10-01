import logging
import os
from logging.handlers import RotatingFileHandler
from app.core.config import settings


# Setup logging
def setup_logger(name, log_file, level=logging.INFO):
    """Function to setup as many loggers as you want"""

    # Create logs directory if it doesn't exist
    LOG_DIR = settings.LOG_DIR
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    

    # Setup the formatter
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

    # Setup the handler to write to a file, with a max of 10MB and 5 backups
    handler = RotatingFileHandler(os.path.join(LOG_DIR, log_file), maxBytes=10000000, backupCount=5)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# Setup loggers
data_logger = setup_logger('data_utils', 'data_utils.log')
main_logger = setup_logger('main', 'main.log')
pdf_logger = setup_logger('pdf_utils', 'pdf_utils.log')
gemini_logger = setup_logger('gemini_utils', 'gemini_utils.log')
mongodb_logger = setup_logger('mongodb', 'mongodb.log')