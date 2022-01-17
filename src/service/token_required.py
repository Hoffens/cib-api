import argparse
import jwt
import datetime
from functools import wraps
from flask import request, jsonify
from config import config


def token_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        print("TOKEN: ", token)
        try:
            data = jwt.decode(token, config['SECRET_KEY'])
        except:
            return jsonify({'message':'aa'})
    return wrapper