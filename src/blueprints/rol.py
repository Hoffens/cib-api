import bcrypt
from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list
from extensions import db


rol = Blueprint('rol', __name__)
rol_schema = {
    "type" : "object",
    "properties" : {
        "id" : {"type" : "number"},
        "nombre" : {"type" : "string"},
        "descripcion" : {"type" : "string"},
        "activo" : {"type" : "boolean"},
    },
    "required": ["id", "nombre","descripcion", "activo"]
}


@rol.route('/api/roles', methods=['GET'])
# @token_required
def obtener_roles():
    try:
        cursor = db.connection.cursor()
        query = f""" SELECT * FROM rol"""
        cursor.execute(query)
        users_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify({ 'status': 'Ok', 'message' : 'Usuarios obtenidos correctamente.', 'data' : users_json }), 200

    except:       
        return jsonify({ 'status': 'Error', 'message' : 'Error inesperado.' }), 500
