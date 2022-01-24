from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db


compania = Blueprint('compania', __name__)

crear_compania_schema = {
    "type": "object",
    "properties": {
        "nombre": {"type": "string"},
        "ubicacion": {"type": "string"},
        "telefono": {"type": "string"},
        "activo": {"type": "boolean"},
        "rut_cuenta": {"type": "number"}
    },
    "required": ["nombre", "ubicacion", "telefono", "activo"]
}

actualizar_compania_schema = {
    "type": "object",
    "properties": {
        "numero": {"type": "numero"},
        "nombre": {"type": "string"},
        "ubicacion": {"type": "string"},
        "telefono": {"type": "string"},
        "activo": {"type": "boolean"},
        "rut_cuenta" : {"type": "number"}
    },
    "required": ["numero", "nombre", "ubicacion", "telefono", "activo"]
}

obt_compania_schema = {
    "type": "object",
    "properties": {
            "numero": {"type": "number"}
    },
    "required": ["numero"]
}


@compania.route('/api/compania', methods=['POST'])
#@token_required
def crear_compania():
    try:
        data = request.get_json()
        validate(instance=data, schema=crear_compania_schema)

        query = f"select rol from usuario where rut = {data['rut_cuenta']}"
        cursor = db.connection.cursor()
        cursor.execute(query)
        rol = cursor.fetchone()[0]

        # No es intendente gral.
        if rol != 4:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        query = f"""INSERT INTO compania (nombre, ubicacion, telefono, activo) values ('{data['nombre']}', 
                '{data['ubicacion']}', '{data['telefono']}', {data['activo']})"""
        cursor.execute(query)
        db.connection.commit()
        cursor.close()

        return jsonify({'status': 'Ok', 'message': 'Compania creada correctamente.'}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500


@compania.route('/api/compania', methods=['PUT'])
#@token_required
def actualizar_compania():
    try:
        data = request.get_json()
        validate(instance=data, schema=actualizar_compania_schema)
        cursor = db.connection.cursor()

        query = f"select rol from usuario where rut = {data['rut_cuenta']}"
        cursor = db.connection.cursor()
        cursor.execute(query)
        rol = cursor.fetchone()[0]

        # No es intendente gral.
        if rol != 4:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        query = f"SELECT * FROM compania WHERE numero = \"{data['numero']}\""
        cursor.execute(query)
        carro = cursor.fetchone()

        if carro:
            query = f"""UPDATE compania SET numero = {data['numero']}, nombre = '{data['nombre']}', ubicacion = '{data['ubicacion']}',
                    telefono = '{data['tipo']}', activo = {data['activo']} WHERE numero = {data['numero']};"""

            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify(
                {'status': 'Ok', 'message': 'Compania creada correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'No existe compania con ese numero'}), 404

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500


@compania.route('/api/compania', methods=['GET'])
#@token_required
def obtener_compania():
    try:
        data = request.get_json()
        validate(instance=data, schema=obt_compania_schema)
        cursor = db.connection.cursor()

        query = f"select * from compania where {data['numero']} = numero"
        cursor.execute(query)
        compania_json = query_to_json(cursor)

        if compania_json is None:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Copania no existe.'}), 400

        return jsonify({'status': 'Ok', 'message': 'Compania obtenida correctamente.', 'data': compania_json}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500


@compania.route('/api/companias', methods=['GET'])
#@token_required
def listado_companias():
    try:
        cursor = db.connection.cursor()
        query = "SELECT * FROM compania"
        cursor.execute(query)
        companias_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify({'status': 'Ok', 'message': 'Companias obtenidas correctamente.', 'data': companias_json}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500


@compania.route('/api/compania_compania', methods=['POST'])
#@token_required
def crear_compania_compania():
    try:
        data = request.get_json()
        validate(instance=data, schema=crear_compania_schema)

        query = f"select rol, compania from usuario where rut = {data['rut_cuenta']}"
        cursor = db.connection.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        rol = row[0]
        compania = row[1]

        # No es intendente gral.
        if rol != 7:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        if compania != data['compania']:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Compañia invalida.'}), 500

        query = f"""INSERT INTO compania (nombre, ubicacion, telefono, activo) values ('{data['nombre']}', 
                '{data['ubicacion']}', '{data['telefono']}', {data['activo']})"""
        cursor.execute(query)
        db.connection.commit()
        cursor.close()

        return jsonify({'status': 'Ok', 'message': 'Compania creada correctamente.'}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500


@compania.route('/api/compania_compania', methods=['PUT'])
#@token_required
def actualizar_compania_compania():
    try:
        data = request.get_json()
        validate(instance=data, schema=actualizar_compania_schema)

        query = f"select rol, compania from usuario where rut = {data['rut_cuenta']}"
        cursor = db.connection.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        rol = row[0]
        compania = row[1]

        # No es intendente gral.
        if rol != 7:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        if compania != data['compania']:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Compañia invalida.'}), 500

        query = f"SELECT * FROM compania WHERE numero = \"{data['numero']}\""
        cursor.execute(query)
        carro = cursor.fetchone()

        if carro:
            query = f"""UPDATE compania SET numero = {data['numero']}, nombre = '{data['nombre']}', ubicacion = '{data['ubicacion']}',
                    telefono = '{data['tipo']}', activo = {data['activo']} WHERE numero = {data['numero']};"""

            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify(
                {'status': 'Ok', 'message': 'Compania creada correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'No existe compania con ese numero'}), 404

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500
