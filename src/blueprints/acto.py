import bcrypt
from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db


acto = Blueprint('acto', __name__)
crear_acto_schema = {
    "type": "object",
    "properties": {
        "clasificacion": {"type": "string"},
        "obac": {"type": "number"},
        "estado": {"type": "number"},
        "direccion": {"type": "string"},
        "fecha_hora": {
            "type": "string",
            "format": "date"
        },
        "activo": {"type": "boolean"},
        "rut_usuario": {"type": "number"}
    },
    "required": ["clasificacion", "obac", "estado", "direccion", "fecha_hora", "activo", "rut_usuario"]
}

actualizar_acto_schema = {
    "type": "object",
    "properties": {
        "id" : {"type": "number"},
        "clasificacion": {"type": "string"},
        "obac": {"type": "number"},
        "estado": {"type": "number"},
        "direccion": {"type": "string"},
        "fecha_hora": {
            "type": "string",
            "format": "date"
        },
        "activo": {"type": "boolean"},
        "rut_usuario": {"type": "number"}
    },
    "required": ["id", "clasificacion", "obac", "estado", "direccion", "fecha_hora", "activo", "rut_usuario"]
}

obt_acto_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"}
    },
    "required": ["id"]
}


@acto.route('/api/acto', methods=['POST'])
#@token_required
def crear_acto():
    try:
        data = request.get_json()
        validate(instance=data, schema=crear_acto_schema)
        cursor = db.connection.cursor()
        query = f"select rol from usuario where rut = {data['rut_usuario']}"

        cursor.execute(query)
        # Si no es secretario u oficial
        if cursor.fetchone()[0] not in [2, 3, 7]:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500


        query = f"""INSERT INTO acto_de_servicio (clasificacion, obac, estado, direccion, fecha_hora, activo) VALUES ('{data['clasificacion']}', {data['obac']}, {data['estado']}, '{data['direccion']}', '{data['fecha_hora']}', 1);"""
        cursor.execute(query)
        db.connection.commit()
        cursor.close()

        return jsonify(
            {'status': 'Ok', 'message': 'Acto de servicio creado correctamente.'}), 200

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500


@acto.route('/api/actos', methods=['GET'])
#@token_required
def listado_actos():
    try:
        cursor = db.connection.cursor()
        query = f"""SELECT ads.id, c.codigo as clasificacion, c.descripcion as descripcion, u.rut as OBAC_rut, e.nombre as estado, ads.direccion, ads.fecha_hora FROM acto_de_servicio ads INNER JOIN clasificacion_acto c ON ads.clasificacion = c.codigo INNER JOIN usuario u ON ads.obac = u.rut INNER JOIN acto_estado e ON e.id = ads.estado;"""
        cursor.execute(query)
        ads_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify(
            {'status': 'Ok', 'message': 'Actos de servicio obtenidos correctamente.', 'data': ads_json}), 200

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado.'}), 500


@acto.route('/api/acto', methods=['PUT'])
#@token_required
def actualizar_acto():
    try:
        data = request.get_json()
        validate(instance=data, schema=actualizar_acto_schema)
        cursor = db.connection.cursor()
        query = f"select rol from usuario where rut = {data['rut_usuario']}"

        cursor.execute(query)

        # Si no es secretario u oficial
        if cursor.fetchone()[0] not in [2, 3, 7]:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        query = f"SELECT * FROM acto_de_servicio WHERE id = {data['id']}"
        cursor.execute(query)
        ads = cursor.fetchone()

        if ads:
            query = f"""UPDATE acto_de_servicio SET id = {data['id']}, clasificacion = '{data['clasificacion']}', obac = {data['obac']},
                    estado = {data['estado']}, direccion = '{data['direccion']}', fecha_hora = '{data['fecha_hora']}', activo = {data['activo']} WHERE id = {data['id']};"""

            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify(
                {'status': 'Ok', 'message': 'Acto de servicio actualizado correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'El acto de servicio no existe.'}), 404

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500


@acto.route('/api/acto', methods=['GET'])
#@token_required
def obtener_acto():
    try:
        data = request.get_json()
        validate(instance=data, schema=obt_acto_schema)
        cursor = db.connection.cursor()

        query = f"""SELECT ads.id, c.codigo as clasificacion, u.rut as obac, e.nombre as estado, ads.direccion, ads.fecha_hora FROM acto_de_servicio ads INNER JOIN clasificacion_acto c ON ads.clasificacion = c.codigo INNER JOIN usuario u ON ads.obac = u.rut INNER JOIN acto_estado e ON e.id = ads.estado where ads.id = {data['id']};"""
        cursor.execute(query)
        acto_json = query_to_json(cursor)

        if acto_json is None:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'El acto de servicio suministrado no existe.'}), 400

        return jsonify({'status': 'Ok', 'message': 'Acto de servicio obtenido correctamente.', 'data': acto_json}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500
