from flask import Blueprint, jsonify, request, make_response
from src.service.token_required import token_required


user = Blueprint('user', __name__)

@user.route('/api/user/register', methods=['POST'])
@token_required
def user_register():
    token = request.headers.get('Authorization')

    if token:
        data = request.get_json()
        return jsonify({ 'status': 'Ok', 'message' : 'Usuario creado correctamente.' }), 200
    
    return jsonify({ 'status': 'Error', 'message' : 'Ha ocurrido un error.' }), 400
