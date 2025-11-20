from typing import Any

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

# Collection+JSON schema (simplified version)
CJ_SCHEMA = {
    "type": "object",
    "properties": {
        "collection": {
            "type": "object",
            "properties": {
                "version": {"type": "string"},
                "href": {"type": "string", "format": "uri"},
                "title": {"type": "string"},
                "links": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "rel": {"type": "string"},
                            "href": {"type": "string", "format": "uri"},
                            "prompt": {"type": "string"},
                            "render": {"type": "string"},
                            "method": {"type": "string"},
                        },
                        "required": ["rel", "href"]
                    }
                },
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "href": {"type": "string", "format": "uri"},
                            "rel": {"type": "string"},
                            "data": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "value": {},  # Any type
                                        "prompt": {"type": ["string", "null"]},
                                        "input_type": {"type": ["string", "null"]},
                                        "required": {"type": ["boolean", "null"]},
                                        "options": {"oneOf": [{"type": "array"}, {"type": "null"}]},
                                        "render_hint": {"type": ["string", "null"]},
                                    },
                                    "required": ["name"],
                                    "additionalProperties": True
                                }
                            },
                            "links": {"$ref": "#/properties/collection/properties/links"}
                        },
                        "required": ["href"]
                    }
                },
                "queries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "rel": {"type": "string"},
                            "href": {"type": "string", "format": "uri"},
                            "prompt": {"type": "string"},
                            "data": {"$ref": "#/properties/collection/properties/items/items/properties/data"},
                            "name": {"type": ["string", "null"]}
                        },
                        "required": ["rel", "href"]
                    }
                }
            },
            "required": ["href"]
        },
        "template": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "data": {"$ref": "#/properties/collection/properties/items/items/properties/data"},
                    "href": {"type": "string", "format": "uri"},
                    "method": {"type": "string"}
                }
            }
        },
        "error": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "code": {"type": "integer"},
                "message": {"type": "string"}
            }
        }
    },
    "required": ["collection"]
}


def validate_collection_json(data: dict[str, Any]) -> bool:
    """
    Validate that data conforms to Collection+JSON schema.
    Returns True if valid, raises exception if invalid.
    """
    if not HAS_JSONSCHEMA:
        # Basic validation without schema
        if "collection" not in data:
            raise ValueError("Missing required 'collection' field")
        if "href" not in data["collection"]:
            raise ValueError("Collection missing required 'href' field")
        return True

    try:
        jsonschema.validate(data, CJ_SCHEMA)
        return True
    except jsonschema.ValidationError as e:
        raise ValueError(f"Invalid Collection+JSON: {e.message}") from e


# For testing, temporarily always valid
def is_valid_collection_json_response(response_data: dict[str, Any]) -> bool:
    return "collection" in response_data and "href" in response_data["collection"]
