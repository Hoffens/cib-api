import bcrypt
from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list
from extensions import db


ads = Blueprint('ads', __name__)
ads_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "clasificacion": {"type": "string"},
        "obac": {"type": "number"},
        "estado": {"type": "number"},
        "direccion": {"type": "string"},
        "fecha_hora": {
            "type": "string",
            "format": "date"
        },
        "activo": {"type": "boolean"},
    },
    "required": ["id", "clasificacion", "obac", "estado", "direccion", "fecha_hora", "activo"]
}

ads_delete_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "number"}
            },
        "required": ["id"]
}


@ads.route('/api/ads', methods=['POST'])
#@token_required
def ads_register():
    try:
        data = request.get_json()
        validate(instance=data, schema=ads_schema)
        query = f"SELECT * FROM acto_de_servicio where id = {data['id']}"
        cursor = db.connection.cursor()
        cursor.execute(query)
        ads = cursor.fetchone()

        if ads is None:
            query = f"""INSERT INTO acto_de_servicio (id, clasificacion, obac, estado, direccion, fecha_hora, activo) VALUES ({data['id']}, {data['clasificacion']}, {data['obac']}, '{data['estado']}', '{data['direccion']}', '{data['fecha_hora']}', 1);"""
            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify(
                {'status': 'Ok', 'message': 'Acto de servicio creado correctamente.'}), 200

        return jsonify(
            {'status': 'Error', 'message': 'El acto de servicio ya existe.'}), 422

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500


@ads.route('/api/ads', methods=['GET'])
#@token_required
def obtener_ads():
    try:
        cursor = db.connection.cursor()
        query = f"""SELECT ads.id, c.codigo as clasificacion, u.rut as obac, e.nombre as estado, ads.direccion, ads.fecha_hora FROM acto_de_servicio ads INNER JOIN clasificacion_acto c ON ads.clasificacion = c.codigo INNER JOIN usuario u ON ads.obac = u.rut INNER JOIN acto_estado e ON e.id = ads.estado;"""
        cursor.execute(query)
        ads_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify(
            {'status': 'Ok', 'message': 'Actos de servicio obtenidos correctamente.', 'data': ads_json}), 200

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado.'}), 500


# TODO: test me
@ads.route('/api/ads', methods=['PUT'])
#@token_required
def actualizar_ads():
    try:
        data = request.get_json()
        validate(instance=data, schema=ads_schema)
        cursor = db.connection.cursor()
        query = f"SELECT * FROM usuario WHERE rut = {data['id']}"
        cursor.execute(query)
        ads = cursor.fetchone()

        if ads:
            query = f"""UPDATE ads SET id = {data['id']}, clasificacion = {data['clasificacion']}, obac = '{data['obac']}',
                    estado = '{data['estado']}', direccion = '{data['direccion']}', fecha_hora = date('{data['fecha_hora']}') WHERE id = {data['id']};"""

            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify(
                {'status': 'Ok', 'message': 'Acto de servicio actualizado correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'El acto de servicio no existe.'}), 404

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500

@ads.route('/api/ads', methods=['PUT'])
#@token_required
def eliminar_ads():
    try:
        data = request.get_json()
        validate(instance=data, schema=ads_delete_schema)
        cursor = db.connection.cursor()
        query = f"SELECT * FROM usuario WHERE rut = {data['id']}"
        cursor.execute(query)
        ads = cursor.fetchone()

        if ads:
            query = f"""UPDATE acto_de_servicio SET activo = 0 WHERE id = {data['id']};"""
            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify(
                {'status': 'Ok', 'message': 'Acto de servicio eliminado correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'El acto de servicio no existe.'}), 404

    except BaseException:
        return jsonify(
            {'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500
