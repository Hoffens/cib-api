from flask import Blueprint, jsonify, request, make_response
from src.service.token_required import token_required

user = Blueprint('user', __name__)

@user.route('/api/user/register', methods=['POST'])
#@token_required
def user_register():
    print(request)
    # aca se debe debe de recibir un payload con el user y pass
    return 'registro usuario'