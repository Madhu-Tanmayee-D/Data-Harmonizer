"""
Configuration management for the application
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Determine if running in production or development
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

# Database configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'app_database.db')

# Ollama configuration
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://127.0.0.1:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')
OLLAMA_TIMEOUT = int(os.getenv('OLLAMA_TIMEOUT', '30'))

# Streamlit configuration
STREAMLIT_PORT = int(os.getenv('STREAMLIT_SERVER_PORT', '8501'))
STREAMLIT_ADDRESS = os.getenv('STREAMLIT_SERVER_ADDRESS', 'localhost')

# File upload configuration
MAX_UPLOAD_SIZE_MB = int(os.getenv('MAX_UPLOAD_SIZE_MB', '100'))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_FILE_TYPES = os.getenv('ALLOWED_FILE_TYPES', 'csv').split(',')

# Security configuration
SESSION_TIMEOUT_MINUTES = int(os.getenv('SESSION_TIMEOUT_MINUTES', '60'))
PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', '6'))
USERNAME_MIN_LENGTH = int(os.getenv('USERNAME_MIN_LENGTH', '3'))

# Directories
BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / 'uploads'
OUTPUTS_DIR = BASE_DIR / 'user_outputs'
TEMPLATES_DIR = BASE_DIR / 'templates'

# Create directories if they don't exist
UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# API configuration
API_VERSION = 'v1'
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))

def get_config(key, default=None):
    """Get configuration value by key"""
    config_map = {
        'environment': ENVIRONMENT,
        'debug': DEBUG,
        'database_path': DATABASE_PATH,
        'ollama_host': OLLAMA_HOST,
        'ollama_model': OLLAMA_MODEL,
        'ollama_timeout': OLLAMA_TIMEOUT,
        'max_upload_size': MAX_UPLOAD_SIZE_BYTES,
        'allowed_file_types': ALLOWED_FILE_TYPES,
    }
    return config_map.get(key.lower(), default)

def is_production():
    """Check if running in production"""
    return ENVIRONMENT.lower() == 'production'

def is_development():
    """Check if running in development"""
    return ENVIRONMENT.lower() == 'development'

if __name__ == "__main__":
    print("Application Configuration")
    print("-" * 50)
    print(f"Environment: {ENVIRONMENT}")
    print(f"Debug Mode: {DEBUG}")
    print(f"Database: {DATABASE_PATH}")
    print(f"Ollama Host: {OLLAMA_HOST}")
    print(f"Max Upload Size: {MAX_UPLOAD_SIZE_MB}MB")
    print(f"Allowed Types: {', '.join(ALLOWED_FILE_TYPES)}")
