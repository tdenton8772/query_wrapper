from flask import Blueprint, current_app
from application.modules import delete
import json

mod = Blueprint('v1delete', __name__, url_prefix='/v1/delete')

@mod.route('/', methods=['GET', 'POST'])
def index():
    return json.dumps({'success': True}), 200, {'Content-Type':'application/json'}