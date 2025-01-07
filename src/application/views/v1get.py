from flask import Blueprint, current_app
from application.modules import get
import json

mod = Blueprint('v1get', __name__, url_prefix='/v1/get')

@mod.route('/', methods=['GET', 'POST'])
def index():
    return json.dumps({'success': True}), 200, {'Content-Type':'application/json'}