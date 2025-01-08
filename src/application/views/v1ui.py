from flask import Blueprint, current_app
from application.modules import create, delete, get, query, update
from application.modules.utils import verify_bearer_token
import json

mod = Blueprint('v1ui', __name__, url_prefix='/v1/ui')

@mod.route('/', methods=['GET', 'POST'])
@verify_bearer_token()
def index(token):
    return json.dumps({'success': True}), 200, {'Content-Type':'application/json'}