
from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list
from extensions import db


carro = Blueprint('carro', __name__)
carro_schema = {
    "type": "object",
    "properties": {
        "patente": {"type": "string"},
        "compania": {"type": "number"},
        "modelo": {"type": "number"},
        "tipo": {"type": "number"},
        "siguiente_mantencion": {
            "type": "string",
            "format": "date"
        },
        "anio_fabricacion": {"type": "number"},
        "activo": {"type": "boolean"}
    },
    "required": ["patente", "compania", "modelo", "tipo", "siguiente_mantencion", "activo"]
}


@carro.route('/api/carros', methods=['POST'])
# @token_required
def carro_register():
    try:
        data = request.get_json()
        validate(instance=data, schema=carro_schema)
        cursor = db.connection.cursor()
        query = f"""SELECT * FROM carro WHERE patente = '{data["patente"]}'"""
        cursor.execute(query)
        carro = cursor.fetchone()

        if carro is None:
            query = f"""INSERT INTO carro (patente, compania, modelo, tipo, siguiente_mantencion, anio_fabricacion, activo) values ('{data['patente']}', 
                    {data['compania']}, {data['modelo']}, {data['tipo']}, '{data['siguiente_mantencion']}', {data['anio_fabricacion']}, {data['activo']})"""
            cursor.execute(query)
            db.connection.commit()
            cursor.close()

        return jsonify({'status': 'Ok', 'message': 'Carro creado correctamente.'}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500


@carro.route('/api/carros', methods=['GET'])
# @token_required
def obtener_carros():
    try:
        cursor = db.connection.cursor()
        query = "SELECT * FROM carro"
        cursor.execute(query)
        carros_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify({'status': 'Ok', 'message': 'carros obtenidos correctamente.', 'data': carros_json}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500


@carro.route('/api/carros', methods=['PUT'])
#@token_required
def actualizar_ads():
    try:
        data = request.get_json()
        validate(instance=data, schema=carro_schema)
        cursor = db.connection.cursor()
        query = f"SELECT * FROM carro WHERE patente = \"{data['patente']}\""
        cursor.execute(query)
        carro = cursor.fetchone()

        if carro:
            query = f"""UPDATE carro SET patente = '{data['patente']}', compania = {data['compania']}, modelo = {data['modelo']},
                    tipo = {data['tipo']}, siguiente_mantencion = '{data['siguiente_mantencion']}', anio_fabricacion = {data['anio_fabricacion']}, activo = {data['activo']} WHERE patente = '{data['patente']}';"""

            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify(
                {'status': 'Ok', 'message': 'Carro actualizado correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'No existe carro con esa patente'}), 404

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500
