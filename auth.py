"""
Authentication module for user login, signup, and credential verification.
"""
import hashlib
import hmac
import secrets
from datetime import datetime
from database import get_db_connection, close_db_connection


def hash_password(password, salt=None):
    """
    Hash password with salt using PBKDF2.
    """
    if salt is None:
        salt = secrets.token_hex(32)
    
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    
    return f"{salt}${pwd_hash.hex()}"


def verify_password(stored_hash, provided_password):
    """
    Verify a provided password against a stored hash.
    """
    try:
        salt, pwd_hash = stored_hash.split('$')
        provided_hash = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return hmac.compare_digest(provided_hash.hex(), pwd_hash)
    except Exception:
        return False


def register_user(username, email, password):
    """
    Register a new user.
    Returns: (success: bool, user_id: int or None, message: str)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user already exists
        cursor.execute('SELECT user_id FROM users WHERE username = ? OR email = ?', 
                      (username, email))
        if cursor.fetchone():
            return False, None, "Username or email already exists"
        
        # Validate inputs
        if len(username) < 3:
            return False, None, "Username must be at least 3 characters"
        if len(password) < 6:
            return False, None, "Password must be at least 6 characters"
        if '@' not in email:
            return False, None, "Invalid email format"
        
        # Hash password and insert user
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (username, email, password_hash))
        
        conn.commit()
        return True, cursor.lastrowid, "User registered successfully"
        
    except Exception as e:
        return False, None, f"Registration error: {str(e)}"
    finally:
        close_db_connection(conn)


def login_user(username, password):
    """
    Login user and return user_id if successful.
    Returns: (success: bool, user_id: int or None, message: str)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT user_id, password_hash FROM users WHERE username = ?', 
                      (username,))
        user = cursor.fetchone()
        
        if not user:
            return False, None, "Username not found"
        
        user_id = user['user_id']
        stored_hash = user['password_hash']
        
        if not verify_password(stored_hash, password):
            return False, None, "Invalid password"
        
        # Update last login
        cursor.execute('UPDATE users SET last_login = ? WHERE user_id = ?',
                      (datetime.now(), user_id))
        conn.commit()
        
        return True, user_id, "Login successful"
        
    except Exception as e:
        return False, None, f"Login error: {str(e)}"
    finally:
        close_db_connection(conn)


def get_user_info(user_id):
    """Get user information."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT user_id, username, email, created_at, last_login FROM users WHERE user_id = ?',
                      (user_id,))
        user = cursor.fetchone()
        return dict(user) if user else None
    finally:
        close_db_connection(conn)


def user_exists(user_id):
    """Check if a user exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        return cursor.fetchone() is not None
    finally:
        close_db_connection(conn)
