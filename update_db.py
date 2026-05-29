# import sqlite3

# conn = sqlite3.connect("app_database.db")
# cursor = conn.cursor()

# # Add the missing columns
# cursor.execute("ALTER TABLE processing_history ADD COLUMN harmonized_filename TEXT")
# cursor.execute("ALTER TABLE processing_history ADD COLUMN harmonized_path TEXT")
# cursor.execute("ALTER TABLE processing_history ADD COLUMN harmonized_size INTEGER")

# conn.commit()
# conn.close()
# print("Database updated successfully!")

import sqlite3
conn = sqlite3.connect("app_database.db")
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(processing_history)")
columns = [row[1] for row in cursor.fetchall()]
print(columns)
conn.close()