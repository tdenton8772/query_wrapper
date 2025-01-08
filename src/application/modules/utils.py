import redis
from functools import wraps
from flask import request, jsonify
import re
import json

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


def get_sql_and_parameters(redis_client, identifier, is_name=True):
    """
    Helper function to fetch SQL and parameters based on the identifier.
    :param redis_client: Redis client instance.
    :param identifier: Name or UUID.
    :param is_name: True if identifier is a name, False if it's a UUID.
    :return: Tuple (SQL string, parameters dictionary, name or UUID).
    """
    if is_name:
        # Fetch the latest version for the name
        if not redis_client.exists(identifier):
            raise ValueError(f"API name '{identifier}' not found")
        latest_uuid = redis_client.lindex(identifier, 0)
        record = redis_client.get(latest_uuid)
        if not record:
            raise ValueError(f"No valid record found for API name '{identifier}'")
    else:
        # Fetch the record for the UUID
        if not redis_client.exists(identifier):
            raise ValueError(f"Version '{identifier}' not found")
        record = redis_client.get(identifier)
        if not record:
            raise ValueError(f"No valid record found for version '{identifier}'")
    
    record_data = json.loads(record)
    sql = record_data.get('sql')
    parameters = record_data.get('parameters', {})
    return sql, parameters, identifier

def format_parameter(value, param_type):
    """
    Format the parameter value based on its type.
    :param value: The value of the parameter.
    :param param_type: The type of the parameter (e.g., "column", "string").
    :return: Formatted parameter value as a string.
    """
    if param_type == "column":
        return f'"{value}"'  # Double quotes for column names
    elif param_type == "string":
        return f"'{value}'"  # Single quotes for strings
    elif param_type == "integer":
        return str(value)  # No quotes for integers
    elif param_type == "bool":
        return "TRUE" if value else "FALSE"  # Boolean values without quotes
    else:
        raise ValueError(f"Unsupported parameter type: {param_type}")

def replace_parameters_in_sql(sql, parameters, user_params):
    """
    Replace placeholders in the SQL query with actual parameter values.
    :param sql: SQL string with placeholders (e.g., %param1%).
    :param parameters: Dictionary of parameters with "default" and "type".
    :param user_params: User-provided parameter values from the request.
    :return: Processed SQL string with values replaced.
    """
    def replace_placeholder(match):
        placeholder = match.group(1)  # Extract the parameter name
        param_data = parameters.get(placeholder)
        if not param_data:
            raise ValueError(f"Parameter '{placeholder}' not found in defaults or provided data")
        
        # Get the value from user input or defaults
        value = user_params.get(placeholder, param_data["default"])
        param_type = param_data["type"]
        return format_parameter(value, param_type)

    # Use regex to find and replace %param% placeholders
    processed_sql = re.sub(r"%(\w+)%", replace_placeholder, sql)
    return processed_sql