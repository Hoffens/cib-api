from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db

apodo_herramienta = Blueprint('apodo_herramienta', __name__)
crear_apodo_herramienta_schema = {
    "type": "object",
    "properties": {
        "herramienta": {"type": "string"},
        "apodo": {"type": "string"},
        "rut_usuario": {"type": "number"}
    },
    "required": ["herramienta", "apodo", "rut_usuario"]
}

actualizar_apodo_herramienta_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "herramienta": {"type": "string"},
        "apodo": {"type": "string"},
        "rut_usuario": {"type": "number"}
    },
    "required": ["id", "herramienta", "apodo", "rut_usuario"]
}


@apodo_herramienta.route('/api/apodo_herramienta', methods=['POST'])
#@token_required
def crear_apodo_herramienta():
    try:
        data = request.get_json()
        validate(instance=data, schema=crear_apodo_herramienta_schema)
        cursor = db.connection.cursor()
        query = f"select rol from usuario where rut = {data['rut_usuario']}"

        cursor.execute(query)
        # Si intendente gral.
        if cursor.fetchone()[0] != 4:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500


        query = f"""INSERT INTO apodo_herramienta (herramienta, apodo) VALUES ('{data['herramienta']}', '{data['apodo']}');"""
        cursor.execute(query)
        db.connection.commit()
        cursor.close()

        return jsonify(
            {'status': 'Ok', 'message': 'Apodo de herramienta creada correctamente.'}), 200

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500


@apodo_herramienta.route('/api/apodos_de_herramientas', methods=['GET'])
#@token_required
def listado_apodo_herramienta():
    try:
        cursor = db.connection.cursor()
        query = "SELECT a.id, h.nombre, a.apodo from apodo_herramienta a inner join herramienta h on a.herramienta = h.serie"
        cursor.execute(query)
        apodo_herramienta_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify(
            {'status': 'Ok', 'message': 'Apodos de herramienta obtenidos correctamente.', 'data': apodo_herramienta_json}), 200

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado.'}), 500


@apodo_herramienta.route('/api/apodo_herramienta', methods=['PUT'])
#@token_required
def actualizar_apodo_herramienta():
    try:
        data = request.get_json()
        validate(instance=data, schema=actualizar_apodo_herramienta_schema)
        cursor = db.connection.cursor()
        query = f"select rol from usuario where rut = {data['rut_usuario']}"

        cursor.execute(query)

        if cursor.fetchone()[0] != 4:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        query = f"SELECT * FROM apodo_herramienta WHERE id = {data['id']}"
        cursor.execute(query)
        apodo_herramienta = cursor.fetchone()

        if apodo_herramienta:
            query = f"""UPDATE apodo_herramienta SET herramienta = '{data['herramienta']}, 'apodo = '{data['apodo']}' WHERE id = {data['id']};"""
            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify(
                {'status': 'Ok', 'message': 'Apodo de herramienta actualizado correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'El apodo de herramienta no existe.'}), 404

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500
