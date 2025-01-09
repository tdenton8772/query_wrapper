from flask import Blueprint, current_app, request, jsonify
from application.modules.utils import verify_bearer_token, normalize_name, validate_sql_and_parameters
import json
import uuid

mod = Blueprint('v1create', __name__, url_prefix='/v1/create')

@mod.route('/', methods=['POST'])
@verify_bearer_token()
def index(token):
    processed_request = {}
    data = request.get_json()

    # Validate keys are in request
    try:
        processed_request['name'] = normalize_name((data['name']))
        processed_request['sql'] = data['sql']
        processed_request['parameters'] = data['parameters']
        processed_request['active'] = True

        # Validate SQL and parameters
        validate_sql_and_parameters(processed_request['sql'], processed_request['parameters'])

    except KeyError as e:
        return json.dumps({'success': False, "error": f"Missing key: {str(e)}"}), 401, {'Content-Type': 'application/json'}
    except ValueError as e:
        return json.dumps({'success': False, "error": str(e)}), 400, {'Content-Type': 'application/json'}

    # Generate a UUID for the request
    request_id = str(uuid.uuid4())

    # Store the processed_request in Redis
    redis_client = current_app.get_redis_client()
    try:
        # Check if the key already exists
        if redis_client.exists(processed_request['name']):
            return json.dumps({'success': False, "error": f"Key '{processed_request['name']}' already exists"}), 409, {'Content-Type': 'application/json'}

        redis_client.set(request_id, json.dumps(processed_request))
        redis_client.lpush(processed_request['name'], request_id)
    except Exception as e:
        return json.dumps({'success': False, "error": "Failed to store request in Redis", "details": str(e)}), 500, {'Content-Type': 'application/json'}

    # Return success response with the generated UUID
    return json.dumps({'success': True, "id": request_id}), 200, {'Content-Type': 'application/json'}