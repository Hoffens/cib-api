from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db


tipo_carro = Blueprint('tipo_carro', __name__)
crear_tipo_carro_schema = {
    "type": "object",
    "properties": {
        "abreviacion": {"type": "string"},
        "descripcion": {"type": "string"},
        "rut_usuario": {"type": "number"}
    },
    "required": ["abreviacion", "descripcion", "rut_usuario"]
}

actualizar_tipo_carro_schema = {
    "type": "object",
    "properties": {
        "id" : {"type": "number"},
        "abreviacion": {"type": "string"},
        "descripcion": {"type": "string"},
        "rut_usuario": {"type": "number"}
    },
    "required": ["abreviacion", "descripcion", "rut_usuario"]
}


@tipo_carro.route('/api/tipo_carro', methods=['POST'])
#@token_required
def crear_tipo_carro():
    try:
        data = request.get_json()
        validate(instance=data, schema=crear_tipo_carro)
        cursor = db.connection.cursor()
        query = f"select rol from usuario where rut = {data['rut_usuario']}"

        cursor.execute(query)
        # Si intendente gral.
        if cursor.fetchone()[0] != 4:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500


        query = f"""INSERT INTO tipo_caro (nombre, descripcion) VALUES ('{data['nombre']}', '{data['descripcion']}');"""
        cursor.execute(query)
        db.connection.commit()
        cursor.close()

        return jsonify(
            {'status': 'Ok', 'message': 'Tipo de carro creado correctamente.'}), 200

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500


@tipo_carro.route('/api/tipos_carro', methods=['GET'])
#@token_required
def listado_tipo_carro():
    try:
        cursor = db.connection.cursor()
        query = f"""SELECT id, nombre, descripcion from tipo_carro"""
        cursor.execute(query)
        tipo_carro_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify(
            {'status': 'Ok', 'message': 'Tipos de carro obtenidos correctamente.', 'data': tipo_carro_json}), 200

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado.'}), 500


@tipo_caro.route('/api/tipo_carro', methods=['PUT'])
#@token_required
def actualizar_tipo_carro():
    try:
        data = request.get_json()
        validate(instance=data, schema=actualizar_tipo_carro_schema)
        cursor = db.connection.cursor()
        query = f"select rol from usuario where rut = {data['rut_usuario']}"

        cursor.execute(query)

        if cursor.fetchone()[0] != 4:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        query = f"SELECT * FROM tipo_carro WHERE id = {data['id']}"
        cursor.execute(query)
        tipo_carro = cursor.fetchone()

        if tipo_carro:
            query = f"""UPDATE tipo_carro SET abreviacion = '{data['abreviacion']}', descripcion = '{data['descripcion']}' WHERE id = {data['id']};"""

            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify(
                {'status': 'Ok', 'message': 'Tipo de carro actualizado correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'El tipo de carro no existe.'}), 404

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500
