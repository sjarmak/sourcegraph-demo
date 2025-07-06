#!/usr/bin/env python3
"""
Database migration script to add matched_keywords and source_type columns.
"""
import sqlite3
import sys
from pathlib import Path

def migrate_database():
    """Add new columns to the insights table."""
    db_path = Path(__file__).parent / "insights.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(insights)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Current columns: {column_names}")
        
        # Add matched_keywords column if it doesn't exist
        if 'matched_keywords' not in column_names:
            print("Adding matched_keywords column...")
            cursor.execute("ALTER TABLE insights ADD COLUMN matched_keywords JSON")
            print("✅ Added matched_keywords column")
        else:
            print("⏭️  matched_keywords column already exists")
        
        # Add source_type column if it doesn't exist
        if 'source_type' not in column_names:
            print("Adding source_type column...")
            cursor.execute("ALTER TABLE insights ADD COLUMN source_type VARCHAR")
            print("✅ Added source_type column")
        else:
            print("⏭️  source_type column already exists")
        
        # Create index on (tool, link) for uniqueness if it doesn't exist
        try:
            cursor.execute("CREATE UNIQUE INDEX ix_insights_tool_link ON insights (tool, link)")
            print("✅ Created unique index on (tool, link)")
        except sqlite3.OperationalError as e:
            if "already exists" in str(e):
                print("⏭️  Unique index on (tool, link) already exists")
            else:
                print(f"⚠️  Could not create unique index: {e}")
        
        conn.commit()
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(insights)")
        new_columns = cursor.fetchall()
        new_column_names = [col[1] for col in new_columns]
        
        print(f"Updated columns: {new_column_names}")
        
        conn.close()
        print("✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
