#!/usr/bin/env python
"""
db_manager.py

A CLI tool to manage your PostgreSQL database.

Commands:
  create-db   - Create the database (if not exists) and then create all tables.
  clean-db    - Drop all tables in the database.
  reset-db    - Drop all tables and then recreate them.
  list-tables - List all existing tables.

Usage Examples:
  python db_manager.py create-db
  python db_manager.py list-tables
  python db_manager.py reset-db
"""

import argparse
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine.url import make_url
from app.config import Config
from app.models.base import Base
from app import create_app

def get_engine(use_default_db=False):
    url_obj = make_url(Config.SQLALCHEMY_DATABASE_URI)
    if use_default_db:
        url_obj = url_obj.set(database="postgres")
    engine = create_engine(url_obj, echo=True)
    return engine

def create_database():
    target_db = make_url(Config.SQLALCHEMY_DATABASE_URI).database
    engine_default = get_engine(use_default_db=True)
    with engine_default.connect() as conn:
        # Set autocommit for CREATE DATABASE
        conn = conn.execution_options(isolation_level="AUTOCOMMIT")
        result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname=:db"), {"db": target_db})
        exists = result.scalar() is not None
        if exists:
            print(f"[create-db] Database '{target_db}' already exists.")
        else:
            print(f"[create-db] Database '{target_db}' does not exist. Creating it now...")
            conn.execute(text(f'CREATE DATABASE "{target_db}"'))
            print(f"[create-db] Database '{target_db}' created successfully.")

def create_tables():
    engine = get_engine()
    print("[create-db] Creating tables ...")
    Base.metadata.create_all(engine)
    print("[create-db] Tables created successfully.")

def drop_tables():
    engine = get_engine()
    print("[clean-db] Dropping all tables ...")
    Base.metadata.drop_all(engine)
    print("[clean-db] All tables dropped successfully.")

def list_tables():
    engine = get_engine()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if tables:
        print("[list-tables] Existing tables:")
        for table in tables:
            print(f"  - {table}")
    else:
        print("[list-tables] No tables found in the database.")

def reset_database():
    print("[reset-db] Resetting the database...")
    drop_tables()
    create_tables()
    print("[reset-db] Reset complete.")

def main():
    parser = argparse.ArgumentParser(description="Manage PostgreSQL database operations.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.add_parser("create-db", help="Create the database (if missing) and all tables.")
    subparsers.add_parser("clean-db", help="Drop all tables in the database.")
    subparsers.add_parser("reset-db", help="Reset the database: drop and recreate tables.")
    subparsers.add_parser("list-tables", help="List all tables in the database.")
    args = parser.parse_args()

    # Disable the automatic table creation in create_app.
    Config.DISABLE_AUTO_DB_INIT = True

    app = create_app(Config)
    with app.app_context():
        if args.command == "create-db":
            create_database()
            create_tables()
        elif args.command == "clean-db":
            drop_tables()
        elif args.command == "reset-db":
            reset_database()
        elif args.command == "list-tables":
            list_tables()
        else:
            parser.print_help()
            sys.exit(1)

if __name__ == "__main__":
    main()