from flask import Blueprint, current_app, request, jsonify
from application.modules.utils import verify_bearer_token, normalize_name, validate_sql_and_parameters
import json
import uuid

mod = Blueprint('v1update', __name__, url_prefix='/v1/update')

@mod.route('/<name>', methods=['POST'])
@verify_bearer_token()
def update_by_name(token, name):
    """
    Update the name's version list, mark the old record inactive,
    and create a new active version.
    """
    redis_client = current_app.get_redis_client()
    name = normalize_name(name)

    # Validate the input payload
    data = request.get_json()
    try:
        sql = data['sql']
        parameters = data['parameters']
        # Validate SQL and parameters
        validate_sql_and_parameters(sql, parameters)
    except ValueError as e:
        return json.dumps({'success': False, "error": str(e)}), 400, {'Content-Type': 'application/json'}
    except KeyError as e:
        return jsonify({"success": False, "error": f"Missing key: {str(e)}"}), 400

    try:
        # Check if the name exists in Redis
        if not redis_client.exists(name):
            return jsonify({"success": False, "error": f"API name '{name}' not found"}), 404

        # Get the latest version's UUID
        latest_uuid = redis_client.lindex(name, 0)
        if not latest_uuid:
            return jsonify({"success": False, "error": f"No versions found for API name '{name}'"}), 404

        # Create a new record with a new UUID
        new_uuid = str(uuid.uuid4())
        new_record = {
            "name": name,
            "sql": sql,
            "parameters": parameters,
            "active": True
        }
        redis_client.set(new_uuid, json.dumps(new_record))
        
        # Mark the old record as inactive
        old_record = redis_client.get(latest_uuid)
        if old_record:
            old_record_data = json.loads(old_record)
            old_record_data['active'] = False
            redis_client.set(latest_uuid, json.dumps(old_record_data))

        # Update the name list with the new UUID as the latest version
        redis_client.lpush(name, new_uuid)

        # Return success response
        return jsonify({"success": True, "id": new_uuid}), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500
