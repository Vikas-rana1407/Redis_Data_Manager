import threading
import time
import shutil
import os
import logging

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
INTERVAL_SECONDS = 24 * 60 * 60  # 1 day

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("data_cleanup")

def cleanup_data_folder():
    while True:
        try:
            if os.path.exists(DATA_DIR):
                shutil.rmtree(DATA_DIR)
                logger.info(f"Deleted {DATA_DIR}")
            else:
                logger.info(f"{DATA_DIR} does not exist.")
        except Exception as e:
            logger.error(f"Error deleting {DATA_DIR}: {e}")
        time.sleep(INTERVAL_SECONDS)

def start_cleanup_thread():
    t = threading.Thread(target=cleanup_data_folder, daemon=True)
    t.start()

# To use: call start_cleanup_thread() at app startup
