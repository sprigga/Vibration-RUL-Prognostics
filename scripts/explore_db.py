#!/usr/bin/env python3
"""
Script to explore the SQLite database phm_data.db
Shows all tables and the first 10 records from each table
"""
import sqlite3
import os
from pathlib import Path

# Get the database path
db_path = Path(__file__).parent / "backend" / "phm_data.db"

print(f"Exploring database: {db_path}")
print("="*50)

if not os.path.exists(db_path):
    print(f"Database file does not exist: {db_path}")
    exit(1)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if not tables:
        print("No tables found in the database.")
    else:
        print(f"Found {len(tables)} table(s):\n")
        
        for i, (table_name,) in enumerate(tables):
            print(f"{'='*20} Table: {table_name} {'='*20}")
            
            # Get table info (column names and types)
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("\nColumns:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"  - {col_name} ({col_type}){' NOT NULL' if not_null else ''}{' PRIMARY KEY' if pk else ''}")
            
            # Get first 10 records
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 10;")
            records = cursor.fetchall()
            
            print(f"\nFirst 10 record(s):")
            if records:
                # Print column headers
                headers = [description[0] for description in cursor.description]
                print("  " + " | ".join(f"{h:15}" for h in headers))
                print("  " + "-" * (len(headers) * 17))
                
                # Print records
                for j, record in enumerate(records):
                    print(f"  " + " | ".join(f"{str(val):15}" for val in record))
            else:
                print("  No records found in this table.")
            
            if i < len(tables) - 1:  # Add extra space between tables (except for the last one)
                print("\n")
                
finally:
    conn.close()

print("\n" + "="*50)
print("Database exploration completed.")