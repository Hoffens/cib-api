import jwt
import datetime
import bcrypt
from flask import Blueprint, jsonify, request
from extensions import db
from config import config


auth = Blueprint('auth', __name__)

@auth.route('/api/login', methods=['POST'])
def login():
    # se recibe un payload con el user y password
    data = request.get_json()
    print(data)
    rutUsuario = data["user"]
    passwordUsuario = data["password"].encode('utf-8')

    try:
        #buscamos en la db si el usuario existe
        cursor = db.connection.cursor()
        query = f"SELECT * FROM usuario WHERE rut = {rutUsuario}"
        cursor.execute(query)
        datos = cursor.fetchone()
        
        if datos and bcrypt.checkpw(passwordUsuario, datos[11].encode('utf-8')):
            # le otorgamos un token al usuario y expira luego de 60 minutos
            payload = {
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
                            'iat': datetime.datetime.utcnow(),
                            'sub': rutUsuario
                        }
            token = jwt.encode(
                        payload,
                        config['development'].SECRET_KEY,
                        algorithm='HS256'
                )
            return jsonify({ 'status': 'Ok', 'message' : 'Autenticación exitosa.', 'token' : token }), 200

        return jsonify({ 'status': 'Error', 'message' : 'Usuario o contraseña incorrectos.' }), 400

    except:
       return jsonify({ 'status': 'Error', 'message' : 'No se proporcionó el usuario o contraseña.' }), 400