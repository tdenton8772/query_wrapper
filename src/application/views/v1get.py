from flask import Blueprint, current_app, jsonify
from application.modules.utils import verify_bearer_token, normalize_name
import json

mod = Blueprint('v1get', __name__, url_prefix='/v1/get')

@mod.route('/list', methods=['GET'])
@verify_bearer_token()
def list_apis(token):
    """
    List all API names stored in Redis.
    """
    redis_client = current_app.get_redis_client()

    try:
        # Use SCAN to fetch keys with a specific pattern
        cursor = 0
        keys = []
        pattern = "*"
        while True:
            cursor, partial_keys = redis_client.scan(cursor, match=pattern, count=100)
            keys.extend(partial_keys)
            if cursor == 0:
                break

        # Filter the keys to include only API names (e.g., exclude UUIDs)
        # Assuming API names are stored as lists (e.g., LPUSH "api_name" "uuid")
        api_names = [key for key in keys if redis_client.type(key) == "list"]

        return jsonify({"success": True, "apis": api_names}), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500


@mod.route('/api/<name>', methods=['GET'])
@verify_bearer_token()
def get_by_name(token, name):
    """
    Fetch the latest version and the list of versions for the given API name.
    """
    redis_client = current_app.get_redis_client()

    name = normalize_name(name)
    try:
        # Check if the name exists in Redis
        if not redis_client.exists(name):
            return jsonify({"success": False, "error": f"API name '{name}' not found"}), 404

        # Fetch the list of versions (UUIDs)
        versions = redis_client.lrange(name, 0, -1)
        if not versions:
            return jsonify({"success": False, "error": f"No versions found for API name '{name}'"}), 404

        # Fetch the latest version (first in the list)
        latest_version = redis_client.get(versions[0])
        if not latest_version:
            return jsonify({"success": False, "error": f"Failed to fetch latest version for API name '{name}'"}), 500

        # Deserialize the latest version's data
        latest_version_data = json.loads(latest_version)

        return jsonify({
            "success": True,
            "latest_version": latest_version_data,
            "versions": versions
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500


@mod.route('/version/<version>', methods=['GET'])
@verify_bearer_token()
def get_by_version(token, version):
    """
    Fetch the specific record for the given UUID.
    """
    redis_client = current_app.get_redis_client()
    try:
        # Check if the version (UUID) exists in Redis
        if not redis_client.exists(version):
            return jsonify({"success": False, "error": f"Version '{version}' not found"}), 404

        # Fetch the record for the UUID
        record = redis_client.get(version)
        if not record:
            return jsonify({"success": False, "error": f"Failed to fetch version '{version}'"}), 500

        # Deserialize the record's data
        record_data = json.loads(record)

        return jsonify({"success": True, "record": record_data}), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500
