#!/usr/bin/env python3
"""
Add YouTube support columns to transcriptions table
"""
import os
import sys
from sqlalchemy import text

# Add the project root to Python path
sys.path.insert(0, '/app')

from apps.backend.core.db import SessionLocal

def migrate():
    db = SessionLocal()
    try:
        # Add youtube_url column
        db.execute(text("ALTER TABLE transcriptions ADD COLUMN IF NOT EXISTS youtube_url VARCHAR"))
        # Add title column  
        db.execute(text("ALTER TABLE transcriptions ADD COLUMN IF NOT EXISTS title VARCHAR"))
        db.commit()
        print("✅ Migration completed successfully")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()