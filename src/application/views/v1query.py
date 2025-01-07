from flask import Blueprint, current_app
from application.modules import query
import json

mod = Blueprint('v1query', __name__, url_prefix='/v1/query')

@mod.route('/', methods=['GET', 'POST'])
def index():
    return json.dumps({'success': True}), 200, {'Content-Type':'application/json'}
