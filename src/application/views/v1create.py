from flask import Blueprint, current_app
from application.modules import create
import json

mod = Blueprint('v1create', __name__, url_prefix='/v1/create')

@mod.route('/', methods=['POST'])
def index():
    return json.dumps({'success': True}), 200, {'Content-Type':'application/json'}

