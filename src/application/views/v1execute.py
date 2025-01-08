from flask import Blueprint, current_app, request, jsonify
from application.modules.utils import verify_bearer_token, get_sql_and_parameters, replace_parameters_in_sql
import json

mod = Blueprint('v1execute', __name__, url_prefix='/v1/execute')

@mod.route('/api/<name>', methods=['POST'])
@verify_bearer_token()
def execute_by_name(token, name):
    """
    Execute SQL for the given API name using parameters from the request body or defaults.
    """
    redis_client = current_app.get_redis_client()
    name = name.lower().replace(" ", "_")  # Normalize the name

    try:
        sql, default_parameters, identifier = get_sql_and_parameters(redis_client, name, is_name=True)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 404

    # Merge request parameters with defaults
    user_params = (request.get_json() or {}).get('parameters', {})

    # Replace parameters in the SQL query
    processed_sql = replace_parameters_in_sql(sql, default_parameters, user_params)

    # Print the final SQL query
    print(f"Executing SQL for API name '{name}':")
    print(f"SQL: {processed_sql}")

    return jsonify({"success": True, "sql": processed_sql}), 200

@mod.route('/version/<uuid>', methods=['POST'])
@verify_bearer_token()
def execute_by_version(token, uuid):
    """
    Execute SQL for the given version (UUID) using parameters from the request body or defaults.
    """
    redis_client = current_app.get_redis_client()

    try:
        sql, default_parameters, identifier = get_sql_and_parameters(redis_client, uuid, is_name=False)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 404

    # Merge request parameters with defaults
    user_params = (request.get_json() or {}).get('parameters', {})

    # Replace parameters in the SQL query
    processed_sql = replace_parameters_in_sql(sql, default_parameters, user_params)

    # Print the final SQL query
    print(f"Executing SQL for version '{uuid}':")
    print(f"SQL: {processed_sql}")

    return jsonify({"success": True, "sql": processed_sql}), 200
