import bcrypt
from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db

clasificacion_acto = Blueprint('clasificacion_acto', __name__)

@clasificacion_acto.route('/api/clasificacion_acto', methods=['GET'])
#@token_required
def listado_clasificacion_acto():
    try:
        cursor = db.connection.cursor()
        query = f"""
                    SELECT
                      codigo,
                      descripcion
                    FROM
                      clasificacion_acto
                    ORDER BY
                      codigo
                """
        cursor.execute(query)
        clasificacion_acto_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify({'status': 'Ok', 'message': 'Clasificaciones de actos de servicio obtenidos correctamente.', 'data': clasificacion_acto_json}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500
