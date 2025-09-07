from datetime import datetime
from utils.db_utils import get_logs_collection

def log_detection(plate: str, status: str, image_path: str = None):
    logs = get_logs_collection()
    logs.insert_one({
        "timestamp": datetime.now().isoformat(),
        "plate": plate,
        "status": status,
        "image_path": image_path
    })
