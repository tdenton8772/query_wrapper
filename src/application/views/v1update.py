from flask import Blueprint, current_app
from application.modules import update
import json

mod = Blueprint('v1update', __name__, url_prefix='/v1/update')

@mod.route('/', methods=['GET', 'POST'])
def index():
    return json.dumps({'success': True}), 200, {'Content-Type':'application/json'}
