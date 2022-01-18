import bcrypt
from flask import Blueprint, jsonify, request
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list
from extensions import db


user = Blueprint('user', __name__)


@user.route('/api/users/register', methods=['POST'])
#@token_required
def user_register():
    try:
        data = request.get_json()
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
        return jsonify({ 'status': 'Error', 'message' : 'Error inesperado.' }), 500


@user.route('/api/users', methods=['GET'])
@token_required
def obtener_usuarios():
    try:
        cursor = db.connection.cursor()
        query = f"SELECT * FROM usuario ORDER BY compania"
        cursor.execute(query)
        users_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify({ 'status': 'Ok', 'message' : 'Usuarios obtenidos correctamente.', 'data' : users_json }), 200

    except:       
        return jsonify({ 'status': 'Error', 'message' : 'Error inesperado.' }), 500


@user.route('/api/users/<rut_usuario>', methods=['PUT'])
@token_required
def actualizar_usuario(rut_usuario):
    return jsonify({ 'status': 'Error', 'message' : 'No implementado.' }), 500


@user.route('/api/users/des/<rut_usuario>', methods=['PUT'])
@token_required
def desactivar_usuario(rut_usuario):
    return jsonify({ 'status': 'Error', 'message' : 'No implementado.' }), 500