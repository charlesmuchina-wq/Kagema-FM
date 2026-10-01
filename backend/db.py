"""
Shared MongoDB client and database accessors.

Previously ~45 modules each constructed their own ``AsyncIOMotorClient`` at import
or object-construction time, so a single process opened dozens of independent
connection pools against the same MongoDB. This module centralizes one shared,
pooled client for the whole process.

The client is created lazily (on first use) rather than at import time, so it
binds to the running asyncio event loop instead of whatever loop happens to exist
at import. Call ``close_client()`` on application shutdown.
"""
import os

from motor.motor_asyncio import AsyncIOMotorClient

DEFAULT_MONGO_URL = "mongodb://localhost:27017"
DEFAULT_DB_NAME = "kagema_fm_db"

# Process-wide singleton. Created on first get_client() call.
_client = None


def get_client():
    """Return the process-wide Motor client, creating it on first use."""
    global _client
    if _client is None:
        mongo_url = os.getenv("MONGO_URL", DEFAULT_MONGO_URL)
        _client = AsyncIOMotorClient(mongo_url, maxPoolSize=50)
    return _client


def get_db(name=None):
    """Return a database handle from the shared client.

    ``name`` defaults to the ``DB_NAME`` environment variable.
    """
    return get_client()[name or os.getenv("DB_NAME", DEFAULT_DB_NAME)]


def close_client():
    """Close the shared client and reset it. Safe to call more than once."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
