from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db


asistencia_usuario = Blueprint('asistencia_usuario', __name__)

asistencia_usuario_schema = {
    "type": "object",
    "properties": {
        "rut": {"type": "number"},
        "acto_de_servicio": {"type": "number"},
    },
    "required": ["rut", "acto_de_servicio"]
}

obtener_asistencia_usuario_schema = {
    "type": "object",
    "properties": {
            "rut": {"type": "number"}
    },
    "required": ["rut"]
}


@asistencia_usuario.route('/api/asistencia_usuario', methods=['POST'])
#@token_required
def crear_asistencia_usuario():
    try:
        data = request.get_json()
        validate(instance=data, schema=asistencia_usuario_schema)

        cursor = db.connection.cursor()
        query = f"select * from acto_de_servicio_usuario where rut = {data['rut']} and acto_de_servicio = {data['acto_de_servicio']}"
        cursor.execute(query)
        asistencia_usuario = cursor.fetchone()
         
        if asistencia_usuario is None:
            query = f"""
                        INSERT INTO
                          acto_de_servicio_usuario (
                            rut,
                            acto_de_servicio
                          )
                        values
                          (
                            {data['rut']},
                            {data['acto_de_servicio']}
                          );
                    """
            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify({'status': 'Ok', 'message': 'Asistencia de usuario registrada correctamente.'}), 200
        return jsonify({'status': 'Error', 'message': 'Ya un existe un registro de asistencia para ese acto'}), 500

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500


@asistencia_usuario.route('/api/asistencia_usuario/<rut>', methods=['GET'])
#@token_required
def obtener_asistencia_usuario(rut):
    try:
        #data = request.get_json()
        #validate(instance=data, schema=obtener_asistencia_usuario_schema)
        cursor = db.connection.cursor()

        query = f"select rut, acto_de_servicio from acto_de_servicio_usuario where rut = {rut}"
        cursor.execute(query)
        asistencia_usuario_json = query_to_json_list(cursor)

        if asistencia_usuario_json is None:
            cursor.close()
            return jsonify({'status': 'Error', 'message': 'No hay asistencias para ese usuario.'}), 400

        return jsonify({'status': 'Ok', 'message': 'Asistencias de usuario obtenida correctamente.', 'data': asistencia_usuario_json}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500
