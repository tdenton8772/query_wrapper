from flask import Blueprint, current_app
from application.modules import query
from application.modules.utils import verify_bearer_token
import json

mod = Blueprint('v1execute', __name__, url_prefix='/v1/execute')

@mod.route('/', methods=['GET', 'POST'])
@verify_bearer_token()
def index():
    return json.dumps({'success': True}), 200, {'Content-Type':'application/json'}
