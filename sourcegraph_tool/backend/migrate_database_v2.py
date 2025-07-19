#!/usr/bin/env python3
"""
Database migration script for separating source vs mentioned tools.

This script adds new columns and migrates existing data:
- Adds 'source' column (populated from existing 'tool' column)
- Adds 'mentioned_tools' JSON column
- Adds 'mentioned_concepts' JSON column
- Migrates existing data to new schema
"""

import sys
import json
import logging
from pathlib import Path
from sqlalchemy import create_engine, MetaData, Table, Column, String, JSON, Index, text
from sqlalchemy.orm import sessionmaker

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.db.database import DATABASE_URL
from app.core.tool_detector import ToolDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_database():
    """Perform database migration to new schema."""
    
    # Get database URL
    database_url = DATABASE_URL
    engine = create_engine(database_url)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        logger.info("Starting database migration...")
        
        # Check existing columns using raw SQL
        result = session.execute(text('PRAGMA table_info(insights)'))
        existing_columns = [row[1] for row in result.fetchall()]
        logger.info(f"Existing columns: {existing_columns}")
        
        # Add new columns if they don't exist
        if 'source' not in existing_columns:
            logger.info("Adding 'source' column...")
            session.execute(text('ALTER TABLE insights ADD COLUMN source TEXT'))
            session.commit()
        
        if 'mentioned_tools' not in existing_columns:
            logger.info("Adding 'mentioned_tools' column...")
            session.execute(text('ALTER TABLE insights ADD COLUMN mentioned_tools TEXT'))  # SQLite doesn't have JSON type
            session.commit()
        
        if 'mentioned_concepts' not in existing_columns:
            logger.info("Adding 'mentioned_concepts' column...")
            session.execute(text('ALTER TABLE insights ADD COLUMN mentioned_concepts TEXT'))  # SQLite doesn't have JSON type
            session.commit()
        
        # Migrate existing data
        logger.info("Migrating existing data...")
        
        # Initialize tool detector for processing existing records
        tool_detector = ToolDetector()
        
        # Get all existing records
        result = session.execute(text('SELECT id, tool, matched_keywords FROM insights WHERE source IS NULL'))
        records_to_update = result.fetchall()
        
        logger.info(f"Found {len(records_to_update)} records to migrate")
        
        # Process each record
        updated_count = 0
        for record in records_to_update:
            record_id, tool_value, matched_keywords_json = record
            
            # Set source from existing tool field
            source = tool_value or "unknown"
            
            # Extract mentioned tools and concepts from matched keywords
            mentioned_tools = []
            mentioned_concepts = []
            
            if matched_keywords_json:
                try:
                    if isinstance(matched_keywords_json, str):
                        matched_keywords = json.loads(matched_keywords_json)
                    else:
                        matched_keywords = matched_keywords_json or []
                    
                    mentioned_tools = tool_detector.detect_tools(matched_keywords)
                    mentioned_concepts = tool_detector.detect_concepts(matched_keywords)
                    
                except Exception as e:
                    logger.warning(f"Error processing matched_keywords for record {record_id}: {e}")
                    matched_keywords = []
            
            # Update record
            session.execute(text('''
                UPDATE insights 
                SET source = :source, 
                    mentioned_tools = :mentioned_tools, 
                    mentioned_concepts = :mentioned_concepts
                WHERE id = :record_id
            '''), {
                'source': source,
                'mentioned_tools': json.dumps(mentioned_tools),
                'mentioned_concepts': json.dumps(mentioned_concepts),
                'record_id': record_id
            })
            
            updated_count += 1
            
            if updated_count % 100 == 0:
                logger.info(f"Migrated {updated_count} records...")
                session.commit()
        
        # Final commit
        session.commit()
        logger.info(f"Migration completed. Updated {updated_count} records.")
        
        # Create new index for source + link uniqueness
        try:
            logger.info("Creating new index for source + link uniqueness...")
            session.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS ix_insights_source_link ON insights (source, link)'))
            session.commit()
            logger.info("New index created successfully.")
        except Exception as e:
            logger.warning(f"Index creation failed (may already exist): {e}")
        
        # SQLite doesn't support ALTER COLUMN SET NOT NULL directly, so we'll skip this step
        logger.info("Note: Skipping NOT NULL constraint for SQLite compatibility")
        
        logger.info("Database migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        session.rollback()
        return False
    
    finally:
        session.close()


if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
