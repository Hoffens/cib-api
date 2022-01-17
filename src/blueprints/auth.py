import jwt
import datetime
from flask import Blueprint, jsonify, request, make_response
from extensions import db

auth = Blueprint('auth', __name__)

@auth.route('/api/login', methods=['POST'])
def login():
    # se recibe un payload con el user y password
    data = request.get_json()
    rutUsuario = data["user"]
    passwordUsuario = data["password"]  # aca se debe hashear la password

    try:
        # buscamos en la db si el usuario existe
        cursor = db.connection.cursor()
        query = f"SELECT * FROM usuario WHERE rut = {rutUsuario} and u_password = {passwordUsuario}"
        print(query)
        cursor.execute(query)
        datos = cursor.fetchall()
        if datos:
            # aca debemos retornar el token
            return jsonify({ 'status': 'Ok', 'message' : 'Autenticación exitosa.' }), 200

        return jsonify({ 'status': 'Error', 'message' : 'Usuario o contraseña incorrectos.' }), 400
    except:
        return jsonify({ 'status': 'Error', 'message' : 'No se proporcionó el usuario o contraseña.' }), 400