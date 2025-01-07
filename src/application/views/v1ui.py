from flask import Blueprint, current_app
from application.modules import create, delete, get, query, update
import json

mod = Blueprint('v1ui', __name__, url_prefix='/v1/ui')

@mod.route('/', methods=['GET', 'POST'])
def index():
    return json.dumps({'success': True}), 200, {'Content-Type':'application/json'}