from flask import Blueprint, jsonify, request
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list
from extensions import db


compania = Blueprint('compania', __name__)


@compania.route('/api/compania', methods=['POST'])
@token_required
def compania_register():
    return jsonify({ 'status': 'Ok', 'message' : 'Usuario creado correctamente.' }), 200

