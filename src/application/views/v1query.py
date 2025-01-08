from flask import Blueprint, current_app, request, jsonify
from application.modules.utils import verify_bearer_token
import requests
import json

mod = Blueprint('v1query', __name__, url_prefix='/v1/query')

@mod.route('/', methods=['POST'])
@verify_bearer_token()
def passthrough_query(token):
    """
    Passes the query directly to Pinot and returns the response.
    """
    # Retrieve the Pinot configuration from the app config
    pinot_broker_url = "{}:{}".format(current_app.config.get("PINOT_CONFIG")['broker'], 
                                      current_app.config.get("PINOT_CONFIG")['port'])
    if not pinot_broker_url:
        return jsonify({"success": False, "error": "Pinot broker URL is not configured"}), 500

    # Retrieve the query from the request body
    query = request.get_json()
    if not query or "sql" not in query:
        return jsonify({"success": False, "error": "Query must include an 'sql' field"}), 400

    try:
        # Send the query to the Pinot broker
        response = requests.post(
            f"{pinot_broker_url}/query/sql",
            json={"sql": query["sql"]},
            headers={"Content-Type": "application/json", 
                     "Authorization": "Bearer {token}"}
        )

        # Handle Pinot's response
        if response.status_code != 200:
            return jsonify({"success": False, "error": "Failed to query Pinot", "details": response.text}), 500

        pinot_response = response.json()

        # Return the Pinot response to the client
        return jsonify({"success": True, "data": pinot_response}), 200

    except requests.RequestException as e:
        return jsonify({"success": False, "error": "An error occurred while querying Pinot", "details": str(e)}), 500
