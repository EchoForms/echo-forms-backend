#!/usr/bin/env python3
"""
Migration script to add total_responses column to form_analytics table
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_analytics():
    """Add total_responses column to form_analytics table"""
    
    # Get database URL
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Create database engine
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Check if column already exists
            check_column = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'form_analytics' 
                AND column_name = 'total_responses'
            """)
            
            result = conn.execute(check_column).fetchone()
            
            if result:
                print("✅ total_responses column already exists")
                return True
            
            # Add the column
            add_column = text("""
                ALTER TABLE form_analytics 
                ADD COLUMN total_responses INTEGER DEFAULT 0 NOT NULL
            """)
            
            conn.execute(add_column)
            conn.commit()
            
            print("✅ Successfully added total_responses column to form_analytics table")
            
            # Set default values for existing records
            update_responses = text("""
                UPDATE form_analytics 
                SET total_responses = 0 
                WHERE total_responses IS NULL
            """)
            
            conn.execute(update_responses)
            conn.commit()
            
            print("✅ Set default values for existing records")
            
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Running analytics migration...")
    success = migrate_analytics()
    
    if success:
        print("\n🎉 Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
