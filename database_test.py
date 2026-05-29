import sqlite3
import pandas as pd

# Update this path with the exact DB filename from your database.py file
DB_FILE = "database.db" 

def view_tables():
    # Connect to the local SQLite database
    conn = sqlite3.connect(DB_FILE)
    
    # 1. First, let's see what tables exist in your database
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
    print("--- Existing Tables ---")
    print(tables, "\n")
    
    # 2. Let's look at the registered users (replace 'users' with your exact table name if different)
    try:
        users_df = pd.read_sql_query("SELECT * FROM users;", conn)
        print("--- Registered Users Table ---")
        print(users_df)
    except Exception as e:
        print(f"Could not read users table: {e}")
        
    conn.close()

if __name__ == "__main__":
    view_tables()