import redis
from functools import wraps
from flask import request, jsonify
import re

def normalize_name(name):
    """
    Normalize the API name:
    - Convert to lowercase.
    - Replace spaces with underscores.
    - Remove non-URL-safe characters.
    """
    name = name.lower()
    name = name.replace(" ", "_")  # Replace spaces with underscores
    name = re.sub(r"[^a-z0-9_\-]", "", name)  # Remove invalid characters
    return name

def is_token_valid(token):
    """
    Function to validate the bearer token.
    Replace this with your actual token validation logic.
    """
    # Example: Validate against a hardcoded token for demonstration purposes
    return token == "valid_token"

def verify_bearer_token():
    """
    Decorator to verify the bearer token from the Authorization header.
    Uses the `is_token_valid` function for validation.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract the Authorization header
            auth_header = request.headers.get('Authorization')

            if not auth_header:
                return jsonify({"error": "Authorization header missing"}), 401

            # Check if the header starts with "Bearer "
            if not auth_header.startswith("Bearer "):
                return jsonify({"error": "Invalid Authorization header format"}), 401

            # Extract the token
            bearer_token = auth_header.split(" ", 1)[1]

            # Validate the token
            if not is_token_valid(bearer_token):
                return jsonify({"error": "Invalid or expired token"}), 401

            # Pass the token to the view function
            return func(bearer_token, *args, **kwargs)

        return wrapper
    return decorator

def create_redis_client():
    """Initialize and return a Redis client."""
    return redis.StrictRedis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )