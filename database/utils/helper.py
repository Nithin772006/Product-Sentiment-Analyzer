import json
from datetime import datetime
from bson import ObjectId
from typing import Any, Dict, List, Union


class MongoJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to support MongoDB BSON types like ObjectId and datetime."""

    def default(self, o: Any) -> Any:
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


def serialize_doc(doc: Union[Dict[str, Any], None]) -> Union[Dict[str, Any], None]:
    """Recursively serializes MongoDB BSON types (like ObjectId and datetime) to standard Python types/strings."""
    if doc is None:
        return None

    serialized = {}
    for key, val in doc.items():
        if isinstance(val, ObjectId):
            serialized[key] = str(val)
        elif isinstance(val, datetime):
            serialized[key] = val.isoformat()
        elif isinstance(val, dict):
            serialized[key] = serialize_doc(val)
        elif isinstance(val, list):
            serialized[key] = [
                serialize_doc(item) if isinstance(item, dict) else (str(item) if isinstance(item, ObjectId) else item)
                for item in val
            ]
        else:
            serialized[key] = val
    return serialized


def parse_date(date_val: Any) -> Union[datetime, None]:
    """Converts a value (datetime or string) to a datetime object. Returns None if invalid or None."""
    if isinstance(date_val, datetime):
        return date_val
    if isinstance(date_val, str):
        try:
            # Try parsing ISO format
            # Strips Z if present for compatibility
            normalized = date_val.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized)
        except ValueError:
            # Fallback patterns
            for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%m/%d/%Y"):
                try:
                    return datetime.strptime(date_val, fmt)
                except ValueError:
                    continue
    return None
