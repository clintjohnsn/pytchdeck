"""Simple utility functions."""

import hashlib
import json

from pydantic import BaseModel


def hash_object(obj: BaseModel) -> str:
    """Generate a deterministic ID from the entire pydantic object using SHA-256."""
    # Convert the request to a dictionary sorted by keys for consistent hashing
    json_str = json.dumps(obj.model_dump(mode='json'), sort_keys=True)
    return hashlib.md5(json_str.encode()).hexdigest()