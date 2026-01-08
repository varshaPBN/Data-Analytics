"""
SQLite database operations for storing datasets
"""

import sqlite3
import pandas as pd
import json
from typing import Dict, Any, Optional, List
import io
import os

# Ensure data directory exists
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "data_analytics.db")


def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data BLOB NOT NULL,
            schema_info TEXT NOT NULL,
            sample_data TEXT NOT NULL,
            row_count INTEGER NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()


async def save_dataset(filename: str, file_content: bytes, file_type: str) -> int:
    """
    Save uploaded dataset to database
    Returns dataset ID
    """
    # Read into pandas
    if file_type == 'csv':
        df = pd.read_csv(io.BytesIO(file_content))
    elif file_type in ['xlsx', 'xls']:
        df = pd.read_excel(io.BytesIO(file_content))
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    # Get schema information
    schema_info = {
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "shape": df.shape
    }
    
    # Get sample data (first 5 rows)
    sample_data = df.head(5).to_dict(orient='records')
    
    # Convert dataframe to JSON for storage
    data_json = df.to_json(orient='records')
    
    # Save to database
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO datasets (filename, data, schema_info, sample_data, row_count)
        VALUES (?, ?, ?, ?, ?)
    """, (
        filename,
        data_json,
        json.dumps(schema_info),
        json.dumps(sample_data),
        len(df)
    ))
    
    dataset_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return dataset_id


async def get_dataset(dataset_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve dataset from database
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        "id": row["id"],
        "filename": row["filename"],
        "data": row["data"],
        "schema_info": json.loads(row["schema_info"]),
        "sample_data": json.loads(row["sample_data"]),
        "row_count": row["row_count"]
    }


async def list_all_datasets() -> List[Dict[str, Any]]:
    """
    List all datasets
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, filename, uploaded_at, row_count FROM datasets ORDER BY uploaded_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row["id"],
            "filename": row["filename"],
            "uploaded_at": row["uploaded_at"],
            "row_count": row["row_count"]
        }
        for row in rows
    ]

