#!/usr/bin/env python3
"""
Database migration script to add transcribed_text column to form_response_fields table
Run this script to add the new column to your existing database
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Add transcribed_text column to form_response_fields table"""
    
    # Database connection parameters
    db_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'echo_forms'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password'),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'form_response_fields' 
            AND column_name = 'transcribed_text'
        """)
        
        if cursor.fetchone():
            print("Column 'transcribed_text' already exists in form_response_fields table")
        else:
            # Add the column
            cursor.execute("""
                ALTER TABLE form_response_fields 
                ADD COLUMN transcribed_text TEXT
            """)
            conn.commit()
            print("Successfully added 'transcribed_text' column to form_response_fields table")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error running migration: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("Running database migration...")
    success = run_migration()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
