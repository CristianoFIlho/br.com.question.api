#!/usr/bin/env python3
"""
Migration script for Salesforce Quiz API
This script handles database migrations using Alembic
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
sys.path.append(os.path.dirname(__file__))

from app.core.config import settings
from app.models.database import Base


def create_migration_table():
    """Create alembic_version table if it doesn't exist"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if alembic_version table exists
        result = conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='alembic_version'
        """))
        
        if not result.fetchone():
            # Create alembic_version table
            conn.execute(text("""
                CREATE TABLE alembic_version (
                    version_num VARCHAR(32) NOT NULL, 
                    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                )
            """))
            conn.commit()
            print("✅ Created alembic_version table")


def run_migration():
    """Run the initial migration"""
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Created all database tables")
    
    # Mark migration as applied
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT OR REPLACE INTO alembic_version (version_num) 
            VALUES ('0001')
        """))
        conn.commit()
        print("✅ Marked migration 0001 as applied")


def check_migration_status():
    """Check current migration status"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.fetchone()
            if version:
                print(f"📊 Current migration version: {version[0]}")
            else:
                print("📊 No migrations applied yet")
        except Exception as e:
            print(f"📊 Migration table not found: {e}")


if __name__ == "__main__":
    print("🚀 Running Salesforce Quiz API Migration")
    print("=" * 50)
    
    # Check current status
    check_migration_status()
    
    # Create migration table
    create_migration_table()
    
    # Run migration
    run_migration()
    
    print("=" * 50)
    print("✅ Migration completed successfully!")
    print("📚 Database is ready for use")
