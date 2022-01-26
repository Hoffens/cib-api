
import bcrypt
from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db

acto_estado = Blueprint('acto_estado', __name__)

@acto_estado.route('/api/acto_estado', methods=['GET'])
#@token_required
def listado_acto_estado():
    try:
        cursor = db.connection.cursor()
        query = f"""
                    SELECT
                      id,
                      nombre,
                      descripcion
                    FROM
                      acto_estado
                    ORDER BY
                      id
                """
        cursor.execute(query)
        acto_estado_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify({'status': 'Ok', 'message': 'Estados de actos de servicio obtenidos correctamente.', 'data': acto_estado_json}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500
