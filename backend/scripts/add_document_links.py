"""Add document_links column to applications table"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE applications ADD COLUMN document_links JSON"))
        conn.commit()
        print("✓ Added document_links column")
    except Exception as e:
        if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
            print("Column already exists, skipping")
        else:
            raise e
