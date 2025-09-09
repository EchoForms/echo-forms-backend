#!/usr/bin/env python3
"""
Database migration script to add new columns for translation, categories, and sentiment.
Run this script to update the database schema.
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def run_migration():
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/echo_forms')
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("Starting database migration...")
        
        # Add new columns to form_response_fields table
        print("Adding columns to form_response_fields table...")
        cursor.execute("""
            ALTER TABLE form_response_fields 
            ADD COLUMN IF NOT EXISTS translated_text TEXT,
            ADD COLUMN IF NOT EXISTS categories JSON,
            ADD COLUMN IF NOT EXISTS sentiment VARCHAR(20) DEFAULT 'neutral';
        """)
        print("✓ Added translated_text, categories, and sentiment columns")
        
        # Add language column to form_responses table
        print("Adding language column to form_responses table...")
        cursor.execute("""
            ALTER TABLE form_responses 
            ADD COLUMN IF NOT EXISTS language VARCHAR(10) DEFAULT 'en';
        """)
        print("✓ Added language column")
        
        # Add comments for documentation
        print("Adding column comments...")
        cursor.execute("""
            COMMENT ON COLUMN form_response_fields.translated_text IS 'English translation of the response text if original was in another language';
            COMMENT ON COLUMN form_response_fields.categories IS 'JSON array of categories extracted from the response text';
            COMMENT ON COLUMN form_response_fields.sentiment IS 'Sentiment analysis result: positive, negative, or neutral';
            COMMENT ON COLUMN form_responses.language IS 'Language code of the response (e.g., en, es, fr, de)';
        """)
        print("✓ Added column comments")
        
        # Create index on language column for better query performance
        print("Creating index on language column...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_form_responses_language ON form_responses(language);
        """)
        print("✓ Created language index")
        
        # Update existing records to have default language as 'en'
        print("Updating existing records...")
        cursor.execute("""
            UPDATE form_responses 
            SET language = 'en' 
            WHERE language IS NULL;
        """)
        print("✓ Updated existing records")
        
        # Update existing records to have default sentiment as 'neutral'
        cursor.execute("""
            UPDATE form_response_fields 
            SET sentiment = 'neutral' 
            WHERE sentiment IS NULL;
        """)
        print("✓ Updated existing sentiment records")
        
        print("\n🎉 Database migration completed successfully!")
        print("New columns added:")
        print("  - form_response_fields.translated_text (TEXT)")
        print("  - form_response_fields.categories (JSON)")
        print("  - form_response_fields.sentiment (VARCHAR(20))")
        print("  - form_responses.language (VARCHAR(10))")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    return True

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
