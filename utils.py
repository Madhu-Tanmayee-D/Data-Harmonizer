"""
Utility functions for the application
"""
import os
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_file_hash(filepath):
    """Generate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_file_size(filepath):
    """Get file size in bytes"""
    return os.path.getsize(filepath)


def format_file_size(size_bytes):
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def clean_filename(filename):
    """Clean and sanitize filename"""
    # Remove special characters except dots and underscores
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-')
    cleaned = ''.join(c for c in filename if c in allowed_chars)
    return cleaned[:255]  # Limit to 255 characters


def ensure_directory(directory_path):
    """Ensure directory exists, create if needed"""
    Path(directory_path).mkdir(parents=True, exist_ok=True)
    logger.info(f"Directory ensured: {directory_path}")


def save_json(data, filepath):
    """Save data to JSON file"""
    try:
        ensure_directory(os.path.dirname(filepath))
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        logger.info(f"JSON saved: {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving JSON: {str(e)}")
        return False


def load_json(filepath):
    """Load data from JSON file"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        logger.info(f"JSON loaded: {filepath}")
        return data
    except Exception as e:
        logger.error(f"Error loading JSON: {str(e)}")
        return None


def get_timestamp():
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def get_formatted_timestamp():
    """Get formatted timestamp for display"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def truncate_string(text, max_length=50):
    """Truncate string to max length with ellipsis"""
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text


def bytes_to_megabytes(bytes_size):
    """Convert bytes to megabytes"""
    return round(bytes_size / (1024 * 1024), 2)


def get_file_extension(filename):
    """Get file extension"""
    return os.path.splitext(filename)[1].lower()


def remove_file_safely(filepath):
    """Safely remove a file"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"File removed: {filepath}")
            return True
    except Exception as e:
        logger.error(f"Error removing file: {str(e)}")
    return False


def remove_directory_safely(directory_path):
    """Safely remove a directory and its contents"""
    import shutil
    try:
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)
            logger.info(f"Directory removed: {directory_path}")
            return True
    except Exception as e:
        logger.error(f"Error removing directory: {str(e)}")
    return False


def log_error(error_message, exception=None):
    """Log error with optional exception details"""
    if exception:
        logger.error(f"{error_message}: {str(exception)}", exc_info=True)
    else:
        logger.error(error_message)


def log_info(message):
    """Log info message"""
    logger.info(message)


def log_warning(message):
    """Log warning message"""
    logger.warning(message)


class Timer:
    """Context manager for timing operations"""
    def __init__(self, name="Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        logger.info(f"{self.name} started")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        logger.info(f"{self.name} completed in {duration:.2f} seconds")

    def elapsed_seconds(self):
        """Get elapsed time in seconds"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
