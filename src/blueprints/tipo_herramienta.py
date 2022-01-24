from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db

tipo_herramienta = Blueprint('tipo_herramienta', __name__)
crear_tipo_herramienta_schema = {
    "type": "object",
    "properties": {
        "nombre": {"type": "string"},
        "rut_usuario": {"type": "number"}
    },
    "required": ["nombre", "rut_usuario"]
}

actualizar_tipo_herramienta_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "nombre": {"type": "string"},
        "rut_usuario": {"type": "number"}
    },
    "required": ["id", "nombre", "rut_usuario"]
}


@tipo_herramienta.route('/api/tipo_herramienta', methods=['POST'])
#@token_required
def crear_tipo_herramienta():
    try:
        data = request.get_json()
        validate(instance=data, schema=crear_tipo_herramienta_schema)
        cursor = db.connection.cursor()
        query = f"select rol from usuario where rut = {data['rut_usuario']}"

        cursor.execute(query)
        # Si intendente gral.
        if cursor.fetchone()[0] != 4:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500


        query = f"""INSERT INTO tipo_herramienta (nombre) VALUES ('{data['nombre']}');"""
        cursor.execute(query)
        db.connection.commit()
        cursor.close()

        return jsonify(
            {'status': 'Ok', 'message': 'Tipo de herramienta creada correctamente.'}), 200

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500


@tipo_herramienta.route('/api/tipos_de_herramientas', methods=['GET'])
#@token_required
def listado_tipo_herramienta():
    try:
        cursor = db.connection.cursor()
        query = "SELECT id, nombre from tipo_herramienta"
        cursor.execute(query)
        tipo_herramienta_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify(
            {'status': 'Ok', 'message': 'Tipos de herramienta obtenidos correctamente.', 'data': tipo_herramienta_json}), 200

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado.'}), 500


@tipo_herramienta.route('/api/tipo_herramienta', methods=['PUT'])
#@token_required
def actualizar_tipo_herramienta():
    try:
        data = request.get_json()
        validate(instance=data, schema=actualizar_tipo_herramienta_schema)
        cursor = db.connection.cursor()
        query = f"select rol from usuario where rut = {data['rut_usuario']}"

        cursor.execute(query)

        if cursor.fetchone()[0] != 4:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        query = f"SELECT * FROM tipo_herramienta WHERE id = {data['id']}"
        cursor.execute(query)
        tipo_herramienta = cursor.fetchone()

        if tipo_herramienta:
            query = f"""UPDATE tipo_herramienta SET nombre = '{data['nombre']}' WHERE id = {data['id']};"""
            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify(
                {'status': 'Ok', 'message': 'Tipo de herramienta actualizado correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'El tipo de herramienta no existe.'}), 404

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500
