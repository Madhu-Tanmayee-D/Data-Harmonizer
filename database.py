"""
Database initialization and management for user authentication and history tracking.
"""
import sqlite3
import os
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "app_database.db"


def init_database():
    """Initialize SQLite database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Upload history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS upload_history (
            upload_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_size INTEGER,
            file_type TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')
    
    # Processing history table
    # MODIFIED: Added harmonized_filename, harmonized_path, and harmonized_size
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processing_history (
            process_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            upload_id_1 INTEGER,
            upload_id_2 INTEGER,
            status TEXT DEFAULT 'pending',
            process_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completion_timestamp TIMESTAMP,
            error_message TEXT,
            harmonized_filename TEXT,
            harmonized_path TEXT,
            harmonized_size INTEGER,
            report_filename TEXT,
            report_path TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (upload_id_1) REFERENCES upload_history(upload_id),
            FOREIGN KEY (upload_id_2) REFERENCES upload_history(upload_id)
        )
    ''')
    
    # Download history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS download_history (
            download_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            process_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            download_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_size INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (process_id) REFERENCES processing_history(process_id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()


def get_db_connection():
    """Get a connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def close_db_connection(conn):
    """Close database connection."""
    if conn:
        conn.close()


if __name__ == "__main__":
    init_database()
    print(f"Database initialized at {DB_PATH}")