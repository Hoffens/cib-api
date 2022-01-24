from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db


carro = Blueprint('carro', __name__)

obt_carro_schema = {
    "type": "object",
    "properties": {
        "patente": {"type": "string"},
    },
    "required": ["patente"]
}

carro_schema = {
    "type": "object",
    "properties": {
        "patente": {"type": "string"},
        "compania": {"type": "number"},
        "modelo": {"type": "number"},
        "tipo": {"type": "number"},
        "siguiente_mantencion": {
            "type": "string",
            "format": "date"
        },
        "anio_fabricacion": {"type": "number"},
        "activo": {"type": "boolean"},
        "usuario_rut": {"type": "number"}
    },
    "required": ["patente", "compania", "modelo", "tipo", "siguiente_mantencion", "activo", "usuario_rut"]
}


@carro.route('/api/carro', methods=['POST'])
# @token_required
def crear_carro():
    try:
        data = request.get_json()
        validate(instance=data, schema=carro_schema)
        cursor = db.connection.cursor()
        query = f"select rol from usuario where rut = {data['usuario_rut']}"
        cursor.execute(query)
        rol = cursor.fetchone()[0]
        if rol != 4:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        query = f"""SELECT * FROM carro WHERE patente = '{data["patente"]}'"""
        cursor.execute(query)
        carro = cursor.fetchone()

        if carro is None:
            query = f"""INSERT INTO carro (patente, compania, modelo, tipo, siguiente_mantencion, anio_fabricacion, activo) values ('{data['patente']}', 
                    {data['compania']}, {data['modelo']}, {data['tipo']}, '{data['siguiente_mantencion']}', {data['anio_fabricacion']}, {data['activo']})"""
            cursor.execute(query)
            db.connection.commit()
            cursor.close()
            return jsonify({'status': 'Ok', 'message': 'Carro creado correctamente.'}), 200
        return jsonify({'status': 'Error', 'message': 'Ese carro ya existe.'}), 500

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500


@carro.route('/api/carros', methods=['GET'])
# @token_required
def listado_carro():
    try:
        cursor = db.connection.cursor()
        query = f"""SELECT ca.patente, c.nombre as compania, tc.descripcion as 'tipo_carro', mc2.nombre as marca, mc.nombre as modelo, 
                ca.anio_fabricacion, ca.siguiente_mantencion, ca.activo FROM carro ca INNER JOIN compania c ON ca.compania = c.numero 
                INNER JOIN modelo_carro mc ON ca.modelo = mc.id INNER JOIN tipo_carro tc ON ca.tipo = tc.id INNER JOIN marca_carro mc2 
                ON mc.marca_id = mc2.id ORDER BY c.numero"""
        cursor.execute(query)
        carros_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify({'status': 'Ok', 'message': 'carros obtenidos correctamente.', 'data': carros_json}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500


@carro.route('/api/carro', methods=['GET'])
def obtener_carro():
    try:
        data = request.get_json()
        validate(instance=data, schema=obt_carro_schema)
        cursor = db.connection.cursor()
        query = f"""SELECT ca.patente, c.nombre as compania, tc.descripcion as 'tipo_carro', mc2.nombre as marca, mc.nombre as modelo, 
                ca.anio_fabricacion, ca.siguiente_mantencion, ca.activo FROM carro ca INNER JOIN compania c ON ca.compania = c.numero 
                INNER JOIN modelo_carro mc ON ca.modelo = mc.id INNER JOIN tipo_carro tc ON ca.tipo = tc.id INNER JOIN marca_carro mc2 
                ON mc.marca_id = mc2.id WHERE ca.patente = '{data['patente']}'"""

        cursor.execute(query)
        carro = query_to_json(cursor)
        cursor.close()
        if carro is not None:
            return jsonify({'status': 'Ok', 'message': 'Carro obtenido correctamente.', 'data': carro}), 200
        return jsonify({'status': 'Error', 'message': 'El carro suministrado no existe.'}), 400

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500


@carro.route('/api/carro', methods=['PUT'])
#@token_required
def actualizar_carro():
    try:
        data = request.get_json()
        validate(instance=data, schema=carro_schema)
        cursor = db.connection.cursor()
        query = f"select rol from usuario where rut = {data['usuario_rut']}"
        cursor.execute(query)
        rol = cursor.fetchone()[0]
        if rol != 4:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        query = f"SELECT * FROM carro WHERE patente = \"{data['patente']}\""
        cursor.execute(query)
        carro = cursor.fetchone()

        if carro:
            query = f"""UPDATE carro SET patente = '{data['patente']}', compania = {data['compania']}, modelo = {data['modelo']},
                    tipo = {data['tipo']}, siguiente_mantencion = '{data['siguiente_mantencion']}', anio_fabricacion = {data['anio_fabricacion']}, activo = {data['activo']} WHERE patente = '{data['patente']}';"""

            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify(
                {'status': 'Ok', 'message': 'Carro actualizado correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'No existe carro con esa patente'}), 404

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500


@carro.route('/api/carro_compania', methods=['POST'])
# @token_required
def crear_carro_compania():
    try:
        data = request.get_json()
        validate(instance=data, schema=carro_schema)
        cursor = db.connection.cursor()
        query = f"select compania, rol from usuario where rut = {data['usuario_rut']}"
        cursor.execute(query)
        row = cursor.fetchone()
        compania = row[0]
        rol = row[1]

        if rol != 6:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        if compania != data['compania']:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Compañia invalida.'}), 500

        query = f"""SELECT * FROM carro WHERE patente = '{data["patente"]}'"""
        cursor.execute(query)
        carro = cursor.fetchone()

        if carro is None:
            query = f"""INSERT INTO carro (patente, compania, modelo, tipo, siguiente_mantencion, anio_fabricacion, activo) values ('{data['patente']}', 
                    {data['compania']}, {data['modelo']}, {data['tipo']}, '{data['siguiente_mantencion']}', {data['anio_fabricacion']}, {data['activo']})"""
            cursor.execute(query)
            db.connection.commit()
            cursor.close()
            return jsonify({'status': 'Ok', 'message': 'Carro creado correctamente.'}), 200
        return jsonify({'status': 'Ok', 'message': 'Ese carro ya existe.'}), 500

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500


@carro.route('/api/carro_compania', methods=['PUT'])
#@token_required
def actualizar_carro_compania():
    try:
        data = request.get_json()
        validate(instance=data, schema=carro_schema)
        cursor = db.connection.cursor()
        query = f"select compania, rol from usuario where rut = {data['usuario_rut']}"
        cursor.execute(query)
        row = cursor.fetchone()
        compania = row[0]
        rol = row[1]

        if rol != 6:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        if compania != data['compania']:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Compañia invalida.'}), 500

        query = f"SELECT * FROM carro WHERE patente = \"{data['patente']}\""

        cursor.execute(query)
        carro = cursor.fetchone()

        if carro:
            query = f"""UPDATE carro SET patente = '{data['patente']}', compania = {data['compania']}, modelo = {data['modelo']},
                    tipo = {data['tipo']}, siguiente_mantencion = '{data['siguiente_mantencion']}', anio_fabricacion = {data['anio_fabricacion']}, activo = {data['activo']} WHERE patente = '{data['patente']}';"""

            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify(
                {'status': 'Ok', 'message': 'Carro actualizado correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'No existe carro con esa patente'}), 404

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500
