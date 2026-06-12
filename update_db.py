import sqlite3

conn = sqlite3.connect("app_database.db")
cursor = conn.cursor()

try:
    cursor.execute(
        "ALTER TABLE processing_history ADD COLUMN report_filename TEXT"
    )
except:
    pass

try:
    cursor.execute(
        "ALTER TABLE processing_history ADD COLUMN report_path TEXT"
    )
except:
    pass

conn.commit()
conn.close()

print("Database updated successfully!")