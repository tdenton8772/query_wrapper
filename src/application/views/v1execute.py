from flask import Blueprint, current_app, request, jsonify
from application.modules.utils import verify_bearer_token, get_sql_and_parameters, replace_parameters_in_sql
import json
import requests

mod = Blueprint('v1execute', __name__, url_prefix='/v1/execute')

@mod.route('/api/<name>', methods=['POST'])
@verify_bearer_token()
def execute_by_name(token, name):
    # Retrieve the Pinot configuration from the app config
    pinot_broker_url = "{}".format(current_app.config.get("PINOT_CONFIG")['broker'])
    if not pinot_broker_url:
        return jsonify({"success": False, "error": "Pinot broker URL is not configured"}), 500
    
    # Execute SQL for the given API name using parameters from the request body or defaults.
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

    try:
        # Send the query to the Pinot broker
        response = requests.post(
            f"{pinot_broker_url}/query/sql",
            json={"sql": processed_sql},
            headers={"Content-Type": "application/json", 
                     "Authorization": f"Bearer {token}"}
        )

        # Handle Pinot's response
        if response.status_code != 200:
            return jsonify({"success": False, "error": "Failed to query Pinot", "details": response.text}), 500

        pinot_response = response.json()

        # Return the Pinot response to the client
        return jsonify({"success": True, "data": pinot_response}), 200

    except requests.RequestException as e:
        return jsonify({"success": False, "error": "An error occurred while querying Pinot", "details": str(e)}), 500

@mod.route('/version/<uuid>', methods=['POST'])
@verify_bearer_token()
def execute_by_version(token, uuid):
    # Retrieve the Pinot configuration from the app config
    pinot_broker_url = "{}".format(current_app.config.get("PINOT_CONFIG")['broker'])
    if not pinot_broker_url:
        return jsonify({"success": False, "error": "Pinot broker URL is not configured"}), 500
    
    # Execute SQL for the given version (UUID) using parameters from the request body or defaults.
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

    try:
        # Send the query to the Pinot broker
        response = requests.post(
            f"{pinot_broker_url}/query/sql",
            json={"sql": processed_sql},
            headers={"Content-Type": "application/json", 
                     "Authorization": f"Bearer {token}"}
        )

        # Handle Pinot's response
        if response.status_code != 200:
            return jsonify({"success": False, "error": "Failed to query Pinot", "details": response.text}), 500

        pinot_response = response.json()

        # Return the Pinot response to the client
        return jsonify({"success": True, "data": pinot_response}), 200

    except requests.RequestException as e:
        return jsonify({"success": False, "error": "An error occurred while querying Pinot", "details": str(e)}), 500
