"""
Database utilities for managing upload, processing, and download history.
"""
import os
from datetime import datetime
from database import get_db_connection, close_db_connection


def save_upload_record(user_id, filename, file_path, file_size, file_type='csv'):
    """
    Save file upload record to database.
    Returns: upload_id
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO upload_history (user_id, filename, file_path, file_size, file_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, filename, file_path, file_size, file_type))
        
        conn.commit()
        return cursor.lastrowid
    finally:
        close_db_connection(conn)


def get_user_uploads(user_id):
    """Get all uploads by a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT upload_id, filename, file_size, file_type, upload_timestamp
            FROM upload_history
            WHERE user_id = ?
            ORDER BY upload_timestamp DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        close_db_connection(conn)


def save_processing_record(user_id, upload_id_1, upload_id_2):
    """
    Save processing record.
    Returns: process_id
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO processing_history (user_id, upload_id_1, upload_id_2, status)
            VALUES (?, ?, ?, 'processing')
        ''', (user_id, upload_id_1, upload_id_2))
        
        conn.commit()
        return cursor.lastrowid
    finally:
        close_db_connection(conn)


def update_processing_status(process_id, status, error_message=None, harmonized_data=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if harmonized_data:
            cursor.execute('''
                UPDATE processing_history
                SET status = ?, completion_timestamp = ?, error_message = ?,
                    harmonized_filename = ?, harmonized_path = ?, harmonized_size = ?
                WHERE process_id = ?
            ''', (status, datetime.now(), error_message, 
                  harmonized_data['name'], harmonized_data['path'], harmonized_data['size'], 
                  process_id))
        else:
            # Fallback for standard updates
            cursor.execute('''
                UPDATE processing_history
                SET status = ?, completion_timestamp = ?, error_message = ?
                WHERE process_id = ?
            ''', (status, datetime.now() if status in ['completed', 'failed'] else None, 
                  error_message, process_id))
        conn.commit()
    finally:
        close_db_connection(conn)


def save_download_record(user_id, process_id, filename, file_path, file_size):
    """
    Save file download record.
    Returns: download_id
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO download_history (user_id, process_id, filename, file_path, file_size)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, process_id, filename, file_path, file_size))
        
        conn.commit()
        return cursor.lastrowid
    finally:
        close_db_connection(conn)


def get_user_processing_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT 
                ph.process_id, ph.status, ph.process_timestamp, ph.completion_timestamp,
                uh1.filename as dataset1, uh1.file_size as size1, uh1.file_path as path1,
                uh2.filename as dataset2, uh2.file_size as size2, uh2.file_path as path2,
                ph.harmonized_filename, ph.harmonized_path, ph.harmonized_size
            FROM processing_history ph
            LEFT JOIN upload_history uh1 ON ph.upload_id_1 = uh1.upload_id
            LEFT JOIN upload_history uh2 ON ph.upload_id_2 = uh2.upload_id
            WHERE ph.user_id = ?
            ORDER BY ph.process_timestamp DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        close_db_connection(conn)

def get_user_info(user_id):
    """Retrieve user profile information from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT email, created_at 
            FROM users 
            WHERE user_id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return None
    finally:
        close_db_connection(conn)
        
def get_user_download_history(user_id):
    """Get all downloads by a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT 
                dh.download_id,
                dh.filename,
                dh.file_size,
                dh.download_timestamp,
                dh.process_id
            FROM download_history dh
            WHERE dh.user_id = ?
            ORDER BY dh.download_timestamp DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        close_db_connection(conn)


def get_processing_details(process_id):
    """Get details of a specific processing job."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT 
                process_id,
                status,
                process_timestamp,
                completion_timestamp,
                error_message
            FROM processing_history
            WHERE process_id = ?
        ''', (process_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        close_db_connection(conn)


def get_download_file_path(download_id):
    """Get file path for a download."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT file_path FROM download_history WHERE download_id = ?',
                      (download_id,))
        row = cursor.fetchone()
        return row['file_path'] if row else None
    finally:
        close_db_connection(conn)

import hashlib
import os
from auth import hash_password

def update_user_info(user_id, new_username=None, new_email=None, new_password=None):
    """Updates user profile information, including optional password, in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Update Username
        if new_username:
            cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (new_username, user_id))
        
        # Update Email
        if new_email:
            cursor.execute("UPDATE users SET email = ? WHERE user_id = ?", (new_email, user_id))
        
        # Update Password (if provided)
        # Update Password (if provided)
        if new_password:
            # This calls the SAME function used by register_user
            hashed_password = hash_password(new_password)
            
            # This saves it in the exact same format (salt$hash) that login expects
            cursor.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (hashed_password, user_id))
            
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating profile: {e}")
        return False
    finally:
        close_db_connection(conn)

def delete_user_account(user_id):
    """Deletes a user, their database records, and their physical files."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Get file paths to delete from disk
        cursor.execute("SELECT file_path FROM upload_history WHERE user_id = ?", (user_id,))
        upload_files = cursor.fetchall()
        cursor.execute("SELECT harmonized_path FROM processing_history WHERE user_id = ? AND harmonized_path IS NOT NULL", (user_id,))
        process_files = cursor.fetchall()
        
        # 2. Delete physical files from server
        for row in upload_files + process_files:
            path = row[0]
            if path and os.path.exists(path):
                os.remove(path)
        
        # 3. Delete database records (Must delete history before user)
        cursor.execute("DELETE FROM download_history WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM processing_history WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM upload_history WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error during deletion: {e}")
        return False
    finally:
        close_db_connection(conn)