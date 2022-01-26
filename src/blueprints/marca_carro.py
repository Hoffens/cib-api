from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db

marca_carro = Blueprint('marca_carro', __name__)
crear_marca_carro_schema = {
    "type": "object",
    "properties": {
        "nombre": {"type": "string"},
        "rut_usuario": {"type": "number"}
    },
    "required": ["nombre", "rut_usuario"]
}

actualizar_marca_carro_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "nombre": {"type": "string"},
        "rut_usuario": {"type": "number"}
    },
    "required": ["nombre", "rut_usuario"]
}


@marca_carro.route('/api/marca_carro', methods=['POST'])
#@token_required
def crear_marca_carro():
    try:
        data = request.get_json()
        validate(instance=data, schema=crear_marca_carro_schema)
        cursor = db.connection.cursor()
        query = f"select rol from usuario where rut = {data['rut_usuario']}"

        cursor.execute(query)
        # Si intendente gral.
        if cursor.fetchone()[0] != 4:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500


        query = f"""INSERT INTO marca_carro (nombre) VALUES ('{data['nombre']}');"""
        cursor.execute(query)
        db.connection.commit()
        cursor.close()

        return jsonify(
            {'status': 'Ok', 'message': 'Marca de carro creado correctamente.'}), 200

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500


@marca_carro.route('/api/marcas_carros', methods=['GET'])
#@token_required
def listado_marca_carro():
    try:
        cursor = db.connection.cursor()
        query = "SELECT id, nombre from marca_carro ORDER BY nombre"
        cursor.execute(query)
        marca_carro_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify(
            {'status': 'Ok', 'message': 'Marcas de carro obtenidos correctamente.', 'data': marca_carro_json}), 200

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado.'}), 500


@marca_carro.route('/api/marca_carro', methods=['PUT'])
#@token_required
def actualizar_marca_carro():
    try:
        data = request.get_json()
        validate(instance=data, schema=actualizar_marca_carro_schema)
        cursor = db.connection.cursor()
        query = f"select rol from usuario where rut = {data['rut_usuario']}"

        cursor.execute(query)

        if cursor.fetchone()[0] != 4:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        query = f"SELECT * FROM marca_carro WHERE id = {data['id']}"
        cursor.execute(query)
        marca_carro = cursor.fetchone()

        if marca_carro:
            query = f"""UPDATE marca_carro SET nombre = '{data['nombre']}' WHERE id = {data['id']};"""
            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify(
                {'status': 'Ok', 'message': 'Marca de carro actualizado correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'La marca de carro no existe.'}), 404

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500
