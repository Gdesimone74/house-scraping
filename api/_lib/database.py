import os
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Optional

_client: Optional[MongoClient] = None

def get_database():
    """Get MongoDB database connection (singleton pattern)"""
    global _client

    if _client is None:
        mongodb_uri = os.environ.get("MONGODB_URI")
        if not mongodb_uri:
            raise ValueError("MONGODB_URI environment variable is not set")
        _client = MongoClient(mongodb_uri)

    return _client.propiedades

def get_propiedades_collection() -> Collection:
    """Get the propiedades collection"""
    db = get_database()
    return db.propiedades

def ensure_indexes():
    """Create indexes for efficient queries"""
    collection = get_propiedades_collection()

    # Index for filtering and sorting
    collection.create_index("barrio")
    collection.create_index("precio")
    collection.create_index("tipo")
    collection.create_index("fechaPrimerVisto")
    collection.create_index("fuente")
    collection.create_index("activo")

    # Compound index for common queries
    collection.create_index([("activo", 1), ("fechaPrimerVisto", -1)])
    collection.create_index([("barrio", 1), ("precio", 1)])

    # Unique index to prevent duplicates
    collection.create_index([("externalId", 1), ("fuente", 1)], unique=True)
