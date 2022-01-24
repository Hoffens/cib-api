from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db


herramienta = Blueprint('herramienta', __name__)

herramienta_schema = {
    "type": "object",
    "properties": {
        "serie": {"type": "string"},
        "nombre": {"type": "string"},
        "descripcion": {"type": "string"},
        "carro": {"type": "string"},
        "compania": {"type": "number"},
        "tipo": {"type": "number"},
        "activo": {"type": "boolean"},
        "rut_cuenta": {"type": "number"}
    },
    "required": ["serie", "nombre", "descripcion", "carro", "compania", "tipo", "activo", "rut_cuenta"]
}

obt_herramienta_schema = {
    "type": "object",
    "properties": {
            "serie": {"type": "string"}
    },
    "required": ["serie"]
}


@herramienta.route('/api/herramienta', methods=['POST'])
#@token_required
def crear_herramienta():
    try:
        data = request.get_json()
        validate(instance=data, schema=herramienta_schema)

        query = f"select rol from usuario where rut = {data['rut_cuenta']}"
        cursor = db.connection.cursor()
        cursor.execute(query)
        rol = cursor.fetchone()[0]

        # No es intendente gral.
        if rol != 4:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        query = f"""INSERT INTO herramienta (serie, nombre, descripcion, carro, compania, tipo, activo) values ('{data['serie']}', 
                '{data['nombre']}', '{data['descripcion']}', '{data['carro']}', {data['compania']}, {data['tipo']}, {data['activo']});"""
        cursor.execute(query)
        db.connection.commit()
        cursor.close()

        return jsonify({'status': 'Ok', 'message': 'herramienta creada correctamente.'}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500


@herramienta.route('/api/herramienta', methods=['PUT'])
#@token_required
def actualizar_herramienta():
    try:
        data = request.get_json()
        validate(instance=data, schema=herramienta_schema)
        cursor = db.connection.cursor()

        query = f"select rol from usuario where rut = {data['rut_cuenta']}"
        cursor = db.connection.cursor()
        cursor.execute(query)
        rol = cursor.fetchone()[0]

        # No es intendente gral.
        if rol != 4:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        query = f"SELECT * FROM herramienta WHERE serie = \"{data['serie']}\""
        cursor.execute(query)
        herramienta = cursor.fetchone()

        if herramienta:
            query = f"""UPDATE herramienta SET serie = '{data['serie']}', nombre = '{data['nombre']}', descripcion = '{data['descripcion']}',
                    carro = '{data['carro']}', compania = {data['compania']}, tipo = {data['tipo']}, activo = {data['activo']} WHERE serie = '{data['serie']}';"""

            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify(
                {'status': 'Ok', 'message': 'Herramienta actualizada correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'No existe herramienta con ese numero de serie'}), 404

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500


@herramienta.route('/api/herramienta', methods=['GET'])
#@token_required
def obtener_herramienta():
    try:
        data = request.get_json()
        validate(instance=data, schema=obt_herramienta_schema)
        cursor = db.connection.cursor()

        query = f"select h.serie, h.nombre, h.descripcion, h.carro, c.nombre as compania, t.nombre as tipo from herramienta h inner join compania c on c.numero = h.compania inner join tipo_herramienta t on t.id = h.tipo where '{data['serie']}' = h.serie"
        cursor.execute(query)
        herramienta_json = query_to_json(cursor)

        if herramienta_json is None:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Herramienta no existe.'}), 400

        return jsonify({'status': 'Ok', 'message': 'Herramienta obtenida correctamente.', 'data': herramienta_json}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500


@herramienta.route('/api/herramientas', methods=['GET'])
#@token_required
def listado_herramientas():
    try:
        cursor = db.connection.cursor()
        query = f"select h.serie, h.nombre, h.descripcion, h.carro, c.nombre as compania, t.nombre as tipo from herramienta h inner join compania c on c.numero = h.compania inner join tipo_herramienta t on t.id = h.tipo"
        cursor.execute(query)
        herramientas_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify({'status': 'Ok', 'message': 'herramientas obtenidas correctamente.', 'data': herramientas_json}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500


@herramienta.route('/api/herramienta_compania', methods=['POST'])
#@token_required
def crear_herramienta_compania():
    try:
        data = request.get_json()
        validate(instance=data, schema=herramienta_schema)

        query = f"select rol, compania from usuario where rut = {data['rut_cuenta']}"
        cursor = db.connection.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        rol = row[0]
        compania = row[1]

        # No es intendente.
        if rol != 6:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        if compania != data['compania']:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Compañia invalida.'}), 500

        query = f"""INSERT INTO herramienta (serie, nombre, descripcion, carro, compania, tipo, activo) values ('{data['serie']}', 
                '{data['nombre']}', '{data['descripcion']}', '{data['carro']}', {data['compania']}, {data['tipo']}, {data['activo']})"""
        cursor.execute(query)
        db.connection.commit()
        cursor.close()

        return jsonify({'status': 'Ok', 'message': 'Herramienta creada correctamente.'}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500


@herramienta.route('/api/herramienta_compania', methods=['PUT'])
#@token_required
def actualizar_herramienta_compania():
    try:
        data = request.get_json()
        validate(instance=data, schema=herramienta_schema)

        query = f"select rol, compania from usuario where rut = {data['rut_cuenta']}"
        cursor = db.connection.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        rol = row[0]
        compania = row[1]

        # No es intendente gral.
        if rol != 6:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        if compania != data['compania']:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Compañia invalida.'}), 500

        query = f"SELECT * FROM herramienta WHERE serie = '{data['serie']}'"
        cursor.execute(query)
        herramienta = cursor.fetchone()

        if herramienta:
            query = f"""UPDATE herramienta SET serie = '{data['serie']}', nombre = '{data['nombre']}', descripcion = '{data['descripcion']}',
                    carro = '{data['carro']}', compania = {data['compania']}, tipo = {data['tipo']}, activo = {data['activo']} WHERE serie = '{data['serie']}';"""

            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify(
                {'status': 'Ok', 'message': 'Herramienta actualizada correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'No existe compania con ese numero'}), 404

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500
