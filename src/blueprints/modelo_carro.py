from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db

modelo_carro = Blueprint('modelo_carro', __name__)
crear_modelo_carro_schema = {
    "type": "object",
    "properties": {
        "marca_id": {"type": "number"},
        "nombre": {"type": "string"},
        "anio": {"type": "number"},
        "rut_usuario": {"type": "number"}
    },
    "required": ["marca_id", "nombre", "anio", "rut_usuario"]
}

actualizar_modelo_carro_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "marca_id": {"type": "number"},
        "nombre": {"type": "string"},
        "anio": {"type": "number"},
        "rut_usuario": {"type": "number"}
    },
    "required": ["id", "marca_id", "nombre", "anio", "rut_usuario"]
}


@modelo_carro.route('/api/modelo_carro', methods=['POST'])
#@token_required
def crear_modelo_carro():
    try:
        data = request.get_json()
        validate(instance=data, schema=crear_modelo_carro_schema)
        cursor = db.connection.cursor()
        query = f"select rol from usuario where rut = {data['rut_usuario']}"

        cursor.execute(query)
        # Si intendente gral.
        if cursor.fetchone()[0] != 4:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500


        query = f"""INSERT INTO modelo_carro (marca_id, nombre, anio) VALUES ({data['marca_id']}, '{data['nombre']}', {data['anio']});"""
        cursor.execute(query)
        db.connection.commit()
        cursor.close()

        return jsonify(
            {'status': 'Ok', 'message': 'Modelo de carro creado correctamente.'}), 200

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500


@modelo_carro.route('/api/modelos_carros', methods=['GET'])
#@token_required
def listado_modelo_carro():
    try:
        cursor = db.connection.cursor()
        query = f"""SELECT mo.id ma.nombre, mo.nombre, mo.anio from modelo_carro mo inner join marca_carro ma on mo.marca_id = ma.id;"""
        cursor.execute(query)
        modelo_carro_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify(
            {'status': 'Ok', 'message': 'Modelos de carro obtenidos correctamente.', 'data': modelo_carro_json}), 200

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado.'}), 500


@modelo_carro.route('/api/modelo_carro', methods=['PUT'])
#@token_required
def actualizar_tipo_carro():
    try:
        data = request.get_json()
        validate(instance=data, schema=actualizar_modelo_carro_schema)
        cursor = db.connection.cursor()
        query = f"select rol from usuario where rut = {data['rut_usuario']}"

        cursor.execute(query)

        if cursor.fetchone()[0] != 4:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        query = f"SELECT * FROM modelo_carro WHERE id = {data['id']}"
        cursor.execute(query)
        modelo_carro = cursor.fetchone()

        if modelo_carro:
            query = f"""UPDATE modelo_carro SET marca_id = {data['marca_id']}, nombre = '{data['nombre']}', anio = {data['anio']} WHERE id = {data['id']};"""

            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify(
                {'status': 'Ok', 'message': 'Modelo de carro actualizado correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'El modelo de carro no existe.'}), 404

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500
