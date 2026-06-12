"""
Test suite for Dataset Harmonization Platform
Run with: python -m pytest test_app.py -v
"""
import pytest
import os
import tempfile
from pathlib import Path

# Test imports
from auth import register_user, login_user, verify_password, hash_password
from database import init_database, DB_PATH, get_db_connection, close_db_connection
from db_utils import (
    save_upload_record, get_user_uploads, save_processing_record,
    get_user_processing_history
)
from utils import (
    clean_filename, format_file_size, validate_email,
    get_file_extension, truncate_string
)


class TestAuthentication:
    """Test authentication functionality"""

    def setup_method(self):
        """Setup for each test"""
        # Use temporary database
        import database
        database.DB_PATH = ":memory:"
        init_database()

    def test_password_hashing(self):
        """Test password hashing"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert "$" in hashed
        assert verify_password(hashed, password)

    def test_wrong_password(self):
        """Test wrong password verification"""
        password = "correct_password"
        hashed = hash_password(password)
        
        assert not verify_password(hashed, "wrong_password")

    def test_user_registration(self):
        """Test user registration"""
        success, message = register_user(
            "testuser",
            "test@example.com",
            "password123"
        )
        
        assert success
        assert "registered" in message.lower()

    def test_duplicate_username(self):
        """Test duplicate username registration"""
        register_user("testuser", "test@example.com", "password123")
        success, message = register_user(
            "testuser",
            "other@example.com",
            "password123"
        )
        
        assert not success
        assert "exists" in message.lower()

    def test_login_success(self):
        """Test successful login"""
        register_user("testuser", "test@example.com", "password123")
        success, user_id, message = login_user("testuser", "password123")
        
        assert success
        assert user_id is not None
        assert user_id > 0

    def test_login_wrong_password(self):
        """Test login with wrong password"""
        register_user("testuser", "test@example.com", "password123")
        success, user_id, message = login_user("testuser", "wrongpassword")
        
        assert not success
        assert user_id is None

    def test_short_password(self):
        """Test short password validation"""
        success, message = register_user(
            "testuser",
            "test@example.com",
            "short"
        )
        
        assert not success
        assert "password" in message.lower() or "characters" in message.lower()

    def test_short_username(self):
        """Test short username validation"""
        success, message = register_user(
            "ab",
            "test@example.com",
            "password123"
        )
        
        assert not success


class TestDatabase:
    """Test database operations"""

    def setup_method(self):
        """Setup for each test"""
        import database
        database.DB_PATH = ":memory:"
        init_database()

    def test_database_initialization(self):
        """Test database initialization"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = cursor.fetchall()
        
        table_names = [table[0] for table in tables]
        assert "users" in table_names
        assert "upload_history" in table_names
        assert "processing_history" in table_names
        assert "download_history" in table_names
        
        close_db_connection(conn)

    def test_save_upload_record(self):
        """Test saving upload record"""
        # Create user first
        register_user("testuser", "test@example.com", "password123")
        _, user_id, _ = login_user("testuser", "password123")
        
        upload_id = save_upload_record(
            user_id,
            "test.csv",
            "/path/to/test.csv",
            1024,
            "csv"
        )
        
        assert upload_id is not None
        assert upload_id > 0

    def test_get_user_uploads(self):
        """Test retrieving user uploads"""
        register_user("testuser", "test@example.com", "password123")
        _, user_id, _ = login_user("testuser", "password123")
        
        save_upload_record(user_id, "test1.csv", "/path/1", 1024, "csv")
        save_upload_record(user_id, "test2.csv", "/path/2", 2048, "csv")
        
        uploads = get_user_uploads(user_id)
        assert len(uploads) == 2


class TestUtilities:
    """Test utility functions"""

    def test_clean_filename(self):
        """Test filename cleaning"""
        assert clean_filename("my file.csv") == "myfile.csv"
        assert clean_filename("test@#$.csv") == "test.csv"
        assert "." in clean_filename("document.xlsx")

    def test_format_file_size(self):
        """Test file size formatting"""
        assert "B" in format_file_size(100)
        assert "KB" in format_file_size(1024 * 10)
        assert "MB" in format_file_size(1024 * 1024 * 10)

    def test_validate_email(self):
        """Test email validation"""
        assert validate_email("test@example.com")
        assert validate_email("user.name@domain.co.uk")
        assert not validate_email("invalid-email")
        assert not validate_email("@example.com")

    def test_get_file_extension(self):
        """Test file extension extraction"""
        assert get_file_extension("document.csv") == ".csv"
        assert get_file_extension("image.PNG") == ".png"
        assert get_file_extension("file.tar.gz") == ".gz"

    def test_truncate_string(self):
        """Test string truncation"""
        long_string = "a" * 100
        truncated = truncate_string(long_string, 50)
        
        assert len(truncated) <= 53  # 50 + "..."
        assert "..." in truncated


class TestDataProcessing:
    """Test data processing functionality"""

    def test_upload_flow(self):
        """Test complete upload flow"""
        # Register user
        register_user("testuser", "test@example.com", "password123")
        _, user_id, _ = login_user("testuser", "password123")
        
        # Save upload
        upload_id = save_upload_record(
            user_id,
            "dataset.csv",
            "/path/to/dataset.csv",
            5120,
            "csv"
        )
        
        # Create processing record
        upload_id_2 = save_upload_record(
            user_id,
            "dataset2.csv",
            "/path/to/dataset2.csv",
            4096,
            "csv"
        )
        
        process_id = save_processing_record(user_id, upload_id, upload_id_2)
        
        assert process_id is not None
        assert process_id > 0
        
        # Check history
        history = get_user_processing_history(user_id)
        assert len(history) == 1


def run_all_tests():
    """Run all tests"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_all_tests()
