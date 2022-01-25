from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db


grupo_sanguineo = Blueprint('grupo_sanguineo', __name__)
crear_grupo_sanguineo_schema = {
    "type": "object",
    "properties": {
        "tipo": {"type": "string"},
        "rut_usuario": {"type": "number"}
    },
    "required": ["tipo", "rut_usuario"]
}

actualizar_grupo_sanguineo_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "tipo": {"type": "string"},
        "rut_usuario": {"type": "number"}
    },
    "required": ["id", "tipo", "rut_usuario"]
}


@grupo_sanguineo.route('/api/grupo_sanguineo', methods=['POST'])
#@token_required
def crear_grupo_sanguineo():
    try:
        data = request.get_json()
        validate(instance=data, schema=crear_grupo_sanguineo)
        cursor = db.connection.cursor()
        query = f"select rol from usuario where rut = {data['rut_usuario']}"

        cursor.execute(query)
        # Si no es administrador.
        if cursor.fetchone()[0] != 1:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500


        query = f"""INSERT INTO grupo_sanguineo (tipo) VALUES ('{data['tipo']}');"""
        cursor.execute(query)
        db.connection.commit()
        cursor.close()

        return jsonify(
            {'status': 'Ok', 'message': 'Grupo sanguineo creado correctamente.'}), 200

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500


@grupo_sanguineo.route('/api/grupos_sanguineos', methods=['GET'])
#@token_required
def listado_grupo_sanguineo():
    try:
        cursor = db.connection.cursor()
        query = f"""SELECT id, tipo from grupo_sanguineo"""
        cursor.execute(query)
        grupo_sanguineo_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify(
            {'status': 'Ok', 'message': 'Grupos sanguineos obtenidos correctamente.', 'data': grupo_sanguineo_json}), 200

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado.'}), 500


@grupo_sanguineo.route('/api/grupo_sanguineo', methods=['PUT'])
#@token_required
def actualizar_grupo_sanguineo():
    try:
        data = request.get_json()
        validate(instance=data, schema=actualizar_grupo_sanguineo_schema)
        cursor = db.connection.cursor()
        query = f"select rol from usuario where rut = {data['rut_usuario']}"

        cursor.execute(query)

        if cursor.fetchone()[0] != 1:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        query = f"SELECT * FROM grupo_sanguineo WHERE id = {data['id']}"
        cursor.execute(query)
        grupo_sanguineo = cursor.fetchone()

        if grupo_sanguineo:
            query = f"""UPDATE grupo_sanguineo SET tipo = '{data['tipo']}' WHERE id = {data['id']};"""

            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify(
                {'status': 'Ok', 'message': 'Grupo sanguineo actualizado correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'El grupo sanguineo no existe.'}), 404

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500
