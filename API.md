# 📚 API Documentation

Complete API documentation for the Dataset Harmonization Platform.

## Overview

The platform provides a set of Python modules that can be imported and used programmatically. This document describes all available functions and classes.

## Table of Contents

1. [Authentication Module](#authentication-module)
2. [Database Module](#database-module)
3. [Database Utilities](#database-utilities)
4. [Pipeline Module](#pipeline-module)
5. [Utilities Module](#utilities-module)
6. [Configuration Module](#configuration-module)

---

## Authentication Module

**Module**: `auth.py`

Functions for user authentication and credential management.

### `hash_password(password, salt=None)`

Hash a password using PBKDF2-SHA256.

**Parameters**:
- `password` (str): Password to hash
- `salt` (str, optional): Salt for hashing (auto-generated if None)

**Returns**: (str) Hashed password with salt

**Example**:
```python
from auth import hash_password

hashed = hash_password("my_password")
print(hashed)  # Output: salt$hash
```

---

### `verify_password(stored_hash, provided_password)`

Verify a provided password against a stored hash.

**Parameters**:
- `stored_hash` (str): Previously hashed password from database
- `provided_password` (str): Password provided by user

**Returns**: (bool) True if password matches, False otherwise

**Example**:
```python
from auth import verify_password

stored_hash = "salt$hash123..."
is_valid = verify_password(stored_hash, "user_password")
if is_valid:
    print("Password is correct!")
else:
    print("Password is incorrect!")
```

---

### `register_user(username, email, password)`

Register a new user in the system.

**Parameters**:
- `username` (str): Desired username (min 3 characters)
- `email` (str): User email address
- `password` (str): Password (min 6 characters)

**Returns**: (tuple) `(success: bool, message: str)`

**Example**:
```python
from auth import register_user

success, message = register_user(
    "john_doe",
    "john@example.com",
    "secure_password_123"
)

if success:
    print(message)  # "User registered successfully"
else:
    print(f"Error: {message}")
```

---

### `login_user(username, password)`

Authenticate user and return user_id.

**Parameters**:
- `username` (str): Username
- `password` (str): Password

**Returns**: (tuple) `(success: bool, user_id: int or None, message: str)`

**Example**:
```python
from auth import login_user

success, user_id, message = login_user("john_doe", "secure_password_123")

if success:
    print(f"Login successful! User ID: {user_id}")
else:
    print(f"Login failed: {message}")
```

---

### `get_user_info(user_id)`

Retrieve user information by user_id.

**Parameters**:
- `user_id` (int): User ID

**Returns**: (dict or None) User information including username, email, created_at, last_login

**Example**:
```python
from auth import get_user_info

user_info = get_user_info(1)
if user_info:
    print(f"Username: {user_info['username']}")
    print(f"Email: {user_info['email']}")
```

---

### `user_exists(user_id)`

Check if a user exists.

**Parameters**:
- `user_id` (int): User ID to check

**Returns**: (bool) True if user exists, False otherwise

**Example**:
```python
from auth import user_exists

if user_exists(1):
    print("User exists")
else:
    print("User not found")
```

---

## Database Module

**Module**: `database.py`

Database initialization and connection management.

### `init_database()`

Initialize SQLite database with all required tables.

**Returns**: None

**Side Effects**: Creates `app_database.db` file with tables: users, upload_history, processing_history, download_history

**Example**:
```python
from database import init_database

init_database()
print("Database initialized")
```

---

### `get_db_connection()`

Get a database connection.

**Returns**: (sqlite3.Connection) Database connection object

**Example**:
```python
from database import get_db_connection, close_db_connection

conn = get_db_connection()
cursor = conn.cursor()
# Use connection...
close_db_connection(conn)
```

---

### `close_db_connection(conn)`

Close a database connection.

**Parameters**:
- `conn` (sqlite3.Connection): Connection to close

**Returns**: None

**Example**:
```python
from database import get_db_connection, close_db_connection

conn = get_db_connection()
# Use connection...
close_db_connection(conn)
```

---

## Database Utilities

**Module**: `db_utils.py`

Functions for managing user history and processing records.

### `save_upload_record(user_id, filename, file_path, file_size, file_type='csv')`

Save a file upload record to database.

**Parameters**:
- `user_id` (int): ID of uploading user
- `filename` (str): Original filename
- `file_path` (str): Path where file is stored
- `file_size` (int): File size in bytes
- `file_type` (str): File type (default: 'csv')

**Returns**: (int) upload_id

**Example**:
```python
from db_utils import save_upload_record

upload_id = save_upload_record(
    user_id=1,
    filename="dataset.csv",
    file_path="/path/to/dataset.csv",
    file_size=5120,
    file_type="csv"
)
print(f"Saved upload with ID: {upload_id}")
```

---

### `get_user_uploads(user_id)`

Get all uploads by a specific user.

**Parameters**:
- `user_id` (int): User ID

**Returns**: (list) List of upload records

**Example**:
```python
from db_utils import get_user_uploads

uploads = get_user_uploads(1)
for upload in uploads:
    print(f"{upload['filename']} - {upload['file_size']} bytes")
```

---

### `save_processing_record(user_id, upload_id_1, upload_id_2)`

Save a processing/harmonization job record.

**Parameters**:
- `user_id` (int): User ID
- `upload_id_1` (int): First dataset upload ID
- `upload_id_2` (int): Second dataset upload ID

**Returns**: (int) process_id

**Example**:
```python
from db_utils import save_processing_record

process_id = save_processing_record(
    user_id=1,
    upload_id_1=10,
    upload_id_2=11
)
print(f"Processing job ID: {process_id}")
```

---

### `update_processing_status(process_id, status, error_message=None)`

Update the status of a processing job.

**Parameters**:
- `process_id` (int): Processing job ID
- `status` (str): Status ('processing', 'completed', 'failed')
- `error_message` (str, optional): Error message if status is 'failed'

**Returns**: None

**Example**:
```python
from db_utils import update_processing_status

# Mark as completed
update_processing_status(1, 'completed')

# Mark as failed with error
update_processing_status(2, 'failed', 'Out of memory error')
```

---

### `save_download_record(user_id, process_id, filename, file_path, file_size)`

Save a file download record.

**Parameters**:
- `user_id` (int): User ID
- `process_id` (int): Associated processing job ID
- `filename` (str): Output filename
- `file_path` (str): Path to output file
- `file_size` (int): File size in bytes

**Returns**: (int) download_id

**Example**:
```python
from db_utils import save_download_record

download_id = save_download_record(
    user_id=1,
    process_id=5,
    filename="harmonized_20240527.csv",
    file_path="/path/to/harmonized_20240527.csv",
    file_size=8192
)
```

---

### `get_user_processing_history(user_id)`

Get all processing jobs for a user.

**Parameters**:
- `user_id` (int): User ID

**Returns**: (list) List of processing records

**Example**:
```python
from db_utils import get_user_processing_history

history = get_user_processing_history(1)
for job in history:
    print(f"Job {job['process_id']}: {job['status']}")
```

---

### `get_user_download_history(user_id)`

Get all downloads by a user.

**Parameters**:
- `user_id` (int): User ID

**Returns**: (list) List of download records

**Example**:
```python
from db_utils import get_user_download_history

downloads = get_user_download_history(1)
for download in downloads:
    print(f"Downloaded: {download['filename']}")
```

---

## Pipeline Module

**Module**: `pipeline.py`

Core data processing pipeline.

### `run_pipeline(uploaded_files)`

Run the complete harmonization pipeline on uploaded files.

**Parameters**:
- `uploaded_files` (list): List of file paths to process

**Returns**: (dict) Dictionary of harmonized DataFrames {dataset_name: DataFrame}

**Example**:
```python
from pipeline import run_pipeline

files = ["/path/to/dataset1.csv", "/path/to/dataset2.csv"]
results = run_pipeline(files)

for name, df in results.items():
    print(f"{name}: {len(df)} rows")
    df.to_csv(f"harmonized_{name}.csv", index=False)
```

---

## Utilities Module

**Module**: `utils.py`

Helper functions for common operations.

### `clean_filename(filename)`

Clean and sanitize a filename.

**Parameters**:
- `filename` (str): Original filename

**Returns**: (str) Cleaned filename

**Example**:
```python
from utils import clean_filename

clean = clean_filename("my file@#$.csv")
print(clean)  # Output: "myfile.csv"
```

---

### `format_file_size(size_bytes)`

Format bytes to human-readable file size.

**Parameters**:
- `size_bytes` (int): Size in bytes

**Returns**: (str) Formatted size string

**Example**:
```python
from utils import format_file_size

print(format_file_size(1024))           # "1.00 KB"
print(format_file_size(1024 * 1024))    # "1.00 MB"
print(format_file_size(1024 * 1024 * 5))  # "5.00 MB"
```

---

### `validate_email(email)`

Validate email format.

**Parameters**:
- `email` (str): Email address to validate

**Returns**: (bool) True if valid, False otherwise

**Example**:
```python
from utils import validate_email

if validate_email("user@example.com"):
    print("Valid email")
else:
    print("Invalid email")
```

---

### `get_file_extension(filename)`

Get file extension.

**Parameters**:
- `filename` (str): Filename

**Returns**: (str) File extension with dot (e.g., ".csv")

**Example**:
```python
from utils import get_file_extension

ext = get_file_extension("document.xlsx")
print(ext)  # Output: ".xlsx"
```

---

### `truncate_string(text, max_length=50)`

Truncate string to maximum length with ellipsis.

**Parameters**:
- `text` (str): Text to truncate
- `max_length` (int): Maximum length (default: 50)

**Returns**: (str) Truncated string

**Example**:
```python
from utils import truncate_string

text = "This is a very long description"
short = truncate_string(text, 15)
print(short)  # Output: "This is a ve..."
```

---

### `Timer` Class

Context manager for timing operations.

**Example**:
```python
from utils import Timer

with Timer("Data Processing") as timer:
    # Do some work
    import time
    time.sleep(2)

print(f"Elapsed: {timer.elapsed_seconds()} seconds")
```

---

## Configuration Module

**Module**: `config.py`

Application configuration management.

### Configuration Variables

```python
from config import (
    ENVIRONMENT,
    DEBUG,
    DATABASE_PATH,
    OLLAMA_HOST,
    OLLAMA_MODEL,
    MAX_UPLOAD_SIZE_MB,
    ALLOWED_FILE_TYPES,
    SESSION_TIMEOUT_MINUTES
)

print(f"Environment: {ENVIRONMENT}")
print(f"Database: {DATABASE_PATH}")
print(f"Max upload: {MAX_UPLOAD_SIZE_MB}MB")
```

---

### `get_config(key, default=None)`

Get configuration value by key.

**Parameters**:
- `key` (str): Configuration key
- `default`: Default value if key not found

**Returns**: Configuration value

**Example**:
```python
from config import get_config

ollama_host = get_config('ollama_host')
max_size = get_config('max_upload_size')
```

---

### `is_production()`

Check if running in production environment.

**Returns**: (bool) True if production, False otherwise

**Example**:
```python
from config import is_production

if is_production():
    print("Running in production mode")
else:
    print("Running in development mode")
```

---

## Common Usage Patterns

### Complete Registration and Login Flow

```python
from auth import register_user, login_user, get_user_info

# Register new user
success, message = register_user("alice", "alice@example.com", "password123")
print(message)

# Login
success, user_id, message = login_user("alice", "password123")
if success:
    user_info = get_user_info(user_id)
    print(f"Welcome {user_info['username']}")
```

### Processing Dataset with History Tracking

```python
from pipeline import run_pipeline
from db_utils import (
    save_upload_record,
    save_processing_record,
    update_processing_status,
    save_download_record
)

user_id = 1
files = ["dataset1.csv", "dataset2.csv"]

# Record uploads
upload_id_1 = save_upload_record(user_id, "dataset1.csv", files[0], 1024)
upload_id_2 = save_upload_record(user_id, "dataset2.csv", files[1], 2048)

# Create processing record
process_id = save_processing_record(user_id, upload_id_1, upload_id_2)

try:
    # Run pipeline
    results = run_pipeline(files)
    
    # Save results
    for name, df in results.items():
        output_file = f"harmonized_{name}.csv"
        df.to_csv(output_file, index=False)
        
        # Record download
        save_download_record(
            user_id,
            process_id,
            output_file,
            output_file,
            1024  # file size
        )
    
    # Mark as completed
    update_processing_status(process_id, 'completed')
    
except Exception as e:
    # Mark as failed
    update_processing_status(process_id, 'failed', str(e))
```

---

## Error Handling

Most functions return status information. Example:

```python
from auth import register_user

success, message = register_user("user", "email@test.com", "pass")
if not success:
    print(f"Registration failed: {message}")
    # Handle error
else:
    print("Registration successful")
```

---

## Database Schema Reference

### Users Table
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP,
    last_login TIMESTAMP
)
```

### Upload History Table
```sql
CREATE TABLE upload_history (
    upload_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    upload_timestamp TIMESTAMP,
    file_size INTEGER,
    file_type TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
```

### Processing History Table
```sql
CREATE TABLE processing_history (
    process_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    upload_id_1 INTEGER,
    upload_id_2 INTEGER,
    status TEXT,
    process_timestamp TIMESTAMP,
    completion_timestamp TIMESTAMP,
    error_message TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
```

### Download History Table
```sql
CREATE TABLE download_history (
    download_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    process_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    download_timestamp TIMESTAMP,
    file_size INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (process_id) REFERENCES processing_history(process_id)
)
```

---

## Version History

- **v1.0.0** (May 27, 2026): Initial release

---

## Support

For API questions or issues:
1. Check this documentation
2. Review example code
3. Check application logs
4. Review unit tests in `test_app.py`
5. Contact support team

---

Last Updated: May 27, 2026
