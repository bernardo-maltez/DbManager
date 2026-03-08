import json
import hashlib

import sys
from pathlib import Path

# Add the parent directory (project root) to the Python path
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from core import schemas


def generate_hash(schema: dict) -> str:
    """
    Creates a SHA-256 hash of a dictionary.
    """

    schema_string = json.dumps(schema, sort_keys=True).encode('utf-8')
    return hashlib.sha256(schema_string)

def create_database(media_type) -> dict:
    """Generates the skeleton for a new JSON database file."""
    # Get base from your core/schemas.py
    
    json_schema = schemas.get_full_schema_for(media_type),
    json_hash = generate_hash(json_schema)

    base_structure = {
        "metadata": {
            "databaseType": media_type,
            "jsonSchema": json_schema, # Merged generic + specific
            "hash": json_hash,
            "showColumns": schemas.get_show_columns(media_type),
            "lastUpdated": ""
        },
        "items": []
    }
    return base_structure

def load_database():
    pass

def schema_extraction():
    pass