from flask import Blueprint, current_app, jsonify
from application.modules import delete
from application.modules.utils import verify_bearer_token, normalize_name
import json

mod = Blueprint('v1delete', __name__, url_prefix='/v1/delete')

@mod.route('/', methods=['GET', 'POST'])
@verify_bearer_token()
def index(token):
    return json.dumps({'success': True}), 200, {'Content-Type':'application/json'}

@mod.route('/api/<name>', methods=['DELETE'])
@verify_bearer_token()
def delete_by_name(token, name):
    """
    Delete all versions associated with the given API name.
    """
    redis_client = current_app.get_redis_client()
    
    name = normalize_name(name)

    try:
        # Check if the name exists
        if not redis_client.exists(name):
            return jsonify({"success": False, "error": f"API name '{name}' not found"}), 404

        # Retrieve all versions (UUIDs) associated with the name
        versions = redis_client.lrange(name, 0, -1)

        # Delete each version from Redis
        for version in versions:
            redis_client.delete(version)

        # Delete the name's list
        redis_client.delete(name)

        return jsonify({"success": True, "message": f"All versions for API name '{name}' deleted"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500



@mod.route('/version/<uuid>', methods=['DELETE'])
@verify_bearer_token()
def delete_by_version(token, uuid):
    """
    Delete a specific record by UUID and remove it from the corresponding name list.
    If the deleted version is active, mark the next version as active.
    """
    redis_client = current_app.get_redis_client()

    try:
        # Check if the UUID exists
        if not redis_client.exists(uuid):
            return jsonify({"success": False, "error": f"UUID '{uuid}' not found"}), 404

        # Retrieve the associated name to update the list
        record = redis_client.get(uuid)
        if not record:
            return jsonify({"success": False, "error": f"No associated record found for UUID '{uuid}'"}), 404

        record_data = json.loads(record)
        name = record_data.get('name')
        if not name:
            return jsonify({"success": False, "error": "Record does not have an associated name"}), 400

        # Check if deleting this UUID will leave the list empty
        versions = redis_client.lrange(name, 0, -1)
        if len(versions) == 1 and versions[0] == uuid:
            return jsonify({"success": False, "error": f"Cannot delete the last UUID for API name '{name}'"}), 400

        # Remove the UUID from the name's list
        redis_client.lrem(name, 0, uuid)

        # Check if the deleted version is active
        if record_data.get('active', False):
            # Get the next version (new first element in the list)
            next_uuid = redis_client.lindex(name, 0)
            if next_uuid:
                # Retrieve and update the next version to be active
                next_record = redis_client.get(next_uuid)
                if next_record:
                    next_record_data = json.loads(next_record)
                    next_record_data['active'] = True
                    redis_client.set(next_uuid, json.dumps(next_record_data))

        # Delete the UUID record
        redis_client.delete(uuid)

        return jsonify({"success": True, "message": f"Record with UUID '{uuid}' deleted"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500
