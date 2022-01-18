import jwt
from functools import wraps
from flask import request, jsonify
from config import config
from extensions import db


def token_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        try:
            data = jwt.decode(token, config['development'].SECRET_KEY, algorithms=['HS256'])
        except:
            return jsonify({ 'status': 'Error', 'message' : 'Token inválido.' }), 400

        return function(*args, **kwargs)

    return wrapper