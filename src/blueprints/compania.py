from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list
from extensions import db


compania = Blueprint('compania', __name__)

compania_schema = {
    "type" : "object",
    "properties" : {
        "nombre" : {"type" : "string"},
        "ubicacion" : {"type" : "string"},
        "telefono" : {"type" : "string"},
        "activo" : {"type" : "boolean"}
    },
    "required": ["nombre", "ubicacion", "telefono", "activo"]
}


@compania.route('/api/companias', methods=['POST'])
#@token_required
def compania_register():
    #try:
        data = request.get_json()
        validate(instance=data, schema=compania_schema)
        cursor = db.connection.cursor()
        query = f"""INSERT INTO compania (nombre, ubicacion, telefono, activo) values ('{data['nombre']}', 
                '{data['ubicacion']}', '{data['telefono']}', {data['activo']})"""
        cursor.execute(query)
        db.connection.commit()
        cursor.close()

        return jsonify({ 'status': 'Ok', 'message' : 'Compania creada correctamente.' }), 200

    #except:
    #    return jsonify({ 'status': 'Error', 'message' : 'Error inesperado.' }), 500



@compania.route('/api/companias', methods=['GET'])
#@token_required
def obtener_companias():
    try:
        cursor = db.connection.cursor()
        query = "SELECT * FROM compania"
        cursor.execute(query)
        companias_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify({ 'status': 'Ok', 'message' : 'Companias obtenidas correctamente.', 'data' : companias_json }), 200

    except:       
        return jsonify({ 'status': 'Error', 'message' : 'Error inesperado.' }), 500

