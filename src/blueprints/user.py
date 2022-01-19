import bcrypt
from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list
from extensions import db


user = Blueprint('user', __name__)

user_schema = {
    "type" : "object",
    "properties" : {
        "rut" : {"type" : "number"},
        "password" : {"type" : "string"},
        "compania" : {"type" : "number"},
        "nombre" : {"type" : "string"},
        "apellido_paterno" : {"type" : "string"},
        "apellido_materno" : {"type" : "string"},
        "fecha_nacimiento": {
            "type": "string",
            "format": "date"
        },
        "correo" : {"type" : "string"},
        "telefono" : {"type" : "string"},
        "fecha_ingreso": {
            "type": "string",
            "format": "date"
        },
        "grupo_sanguineo" : {"type" : "number"},
        "activo" : {"type" : "boolean"},
    },
    "required": ["rut", "password", "compania", "nombre", "apellido_paterno", "apellido_materno",
                "fecha_nacimiento", "correo", "activo"]
}


@user.route('/api/users', methods=['POST'])
@token_required
def user_register():
    try:
        data = request.get_json()
        validate(instance=data, schema=user_schema)
        hashed_password = bcrypt.hashpw(data['password'].encode("utf-8"), bcrypt.gensalt())
        query = f"SELECT * FROM usuario where rut = {data['rut']}"
        cursor = db.connection.cursor()
        cursor.execute(query)
        user = cursor.fetchone()

        if user is None:
            query = f"""INSERT INTO usuario (rut, compania, rol, nombre, apellido_paterno, apellido_materno, fecha_nacimiento, correo, telefono,
                    fecha_ingreso, grupo_sanguineo, u_password, activo) VALUES ({data['rut']}, {data['compania']}, {data['rol']}, 
                    '{data['nombre']}', '{data['apellido_paterno']}', '{data['apellido_materno']}', date('{data['fecha_nacimiento']}'), 
                    '{data['correo']}', '{data['telefono']}',date('{data['fecha_ingreso']}'), {data['grupo_sanguineo']}, 
                    '{hashed_password.decode('utf-8')}', 1);"""
            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify({ 'status': 'Ok', 'message' : 'Usuario creado correctamente.' }), 200

        return jsonify({ 'status': 'Error', 'message' : 'Usuario ya existe.' }), 422
        
    except:
        return jsonify({ 'status': 'Error', 'message' : 'Error inesperado, verifique que la información cargada sea correcta.' }), 500


@user.route('/api/users', methods=['GET'])
@token_required
def obtener_usuarios():
    try:
        cursor = db.connection.cursor()
        query = f"""SELECT u.rut, c.nombre as compania, r.nombre as rol, u.nombre, u.apellido_paterno, u.apellido_materno, u.fecha_nacimiento, 
                u.correo, u.telefono, u.fecha_ingreso, gs.tipo as grupo_sanguineo, u.u_password, u.activo FROM usuario u INNER JOIN compania c 
                ON u.compania = c.numero INNER JOIN rol r ON r.id = u.rol INNER JOIN grupo_sanguineo gs ON gs.id = u.grupo_sanguineo ORDER BY c.numero"""
        cursor.execute(query)
        users_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify({ 'status': 'Ok', 'message' : 'Usuarios obtenidos correctamente.', 'data' : users_json }), 200

    except:       
        return jsonify({ 'status': 'Error', 'message' : 'Error inesperado.' }), 500


@user.route('/api/users/<rut_usuario>', methods=['PUT'])
@token_required
def actualizar_usuario(rut_usuario):
    try:
        cursor = db.connection.cursor()
        query = f"SELECT * FROM usuario WHERE rut = {rut_usuario}"
        cursor.execute(query)
        user = cursor.fetchone()
        cursor.close()

        if user:
            data = request.get_json()
            validate(instance=data, schema=user_schema)
            return jsonify({ 'status': 'Ok', 'message' : 'Usuario actualizado correctamente.'}), 200

        return jsonify({ 'status': 'Ok', 'message' : 'Usuario no existe.'}), 404
        

    except:
        return jsonify({ 'status': 'Error', 'message' : 'Error inesperado, verifique que la información cargada sea correcta.' }), 500