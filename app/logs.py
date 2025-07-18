import os
from functools import wraps
import time
import logging
from logging.handlers import RotatingFileHandler

app_logger = logging.getLogger('app')
app_logger.setLevel(logging.INFO)

log_file = os.path.join(os.getenv("LOG_DIR"), 'app.log')

formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(message)s')

handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5)

handler.setFormatter(formatter)
app_logger.addHandler(handler)

def log_runtime(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()

        try:
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            app_logger.info(f"{func.__name__}: Completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.perf_counter() - start
            app_logger.info(f"{func.__name__}: Failed in {duration:.3f}s - {e}")
            raise
    return wrapper