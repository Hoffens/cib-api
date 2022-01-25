import bcrypt
from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db

perfil_usuario = Blueprint('perfil_usuario', __name__)

perfil_usuario_schema = {
    "type": "object",
    "required": ["rut"],
    "anyOf": [
        {"required": ["password"]},
        {"required": ["correo"]},
        {"required": ["telefono"]},
    ],
    "properties": {
        "password": {"type": "string"},
        "correo": {"type": "string"},
        "telefono": {"type": "string"},
    }
}

obtener_perfil_usuario_schema = {
    "type": "object",
    "properties": {
            "rut": {"type": "number"}
    },
    "required": ["rut"]
}


@perfil_usuario.route('/api/perfil_usuario', methods=['PUT'])
def actualizar_perfil_usuario():
    try:
        data = request.get_json()
        validate(instance=data, schema=perfil_usuario_schema)
        cursor = db.connection.cursor()

        if 'password' in data:
            hashed_password = bcrypt.hashpw(
                data['password'].encode("utf-8"), bcrypt.gensalt())
            query = f"update usuario set password = '{hashed_password.decode('utf-8')}' where rut = {data['rut']};"
            cursor.execute(query)
            cursor.commit()

        if 'correo' in data:
            query = f"update usuario set correo = '{data['correo']}' where rut = {data['rut']};"
            cursor.execute(query)
            cursor.commit()

        if 'telefono' in data:
            query = f"update usuario set telefono = '{data['telefono']}' where rut = {data['rut']};"
            cursor.execute(query)
            db.connection.commit()

        cursor.close()

        return jsonify({'status': 'Ok', 'message': 'Perfil de usuario actualizado correctamente.'}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500


@perfil_usuario.route('/api/perfil_usuario', methods=['GET'])
#@token_required
def obtener_perfil_usuario():
    try:
        data = request.get_json()
        validate(instance=data, schema=obtener_perfil_usuario_schema)
        cursor = db.connection.cursor()
        query = f"""select * from usuario where rut = {data['rut']}"""
        cursor.execute(query)
        usuario = query_to_json(cursor)

        if usuario is None:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Usuario no existe.'}), 400

        query = f"""SELECT u.rut, c.nombre as compania, r.nombre as rol, u.nombre, u.apellido_paterno, u.apellido_materno, u.fecha_nacimiento, 
                u.correo, u.telefono, u.fecha_ingreso, gs.tipo as grupo_sanguineo, u.activo FROM usuario u INNER JOIN compania c ON u.compania = 
                c.numero INNER JOIN rol r ON r.id = u.rol LEFT JOIN grupo_sanguineo gs ON gs.id = u.grupo_sanguineo WHERE u.rut = {data['rut']}"""
        cursor.execute(query)
        usuario = query_to_json(cursor)
        cursor.close()

        return jsonify({'status': 'Ok', 'message': 'Usuario obtenido correctamente.', 'data': usuario}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500
