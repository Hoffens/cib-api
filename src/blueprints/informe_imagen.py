from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db


informe_imagen = Blueprint('imforme_imagen', __name__)

informe_imagen_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "id_informe": {"type": "string"},
        "ruta_imagen": {"type": "string"},
    },
    "required": ["id", "id_informe", "ruta_imagen"]
}


@informe_imagen.route('/api/informe_imagen', methods=['POST'])
#@token_required
def crear_informe_imagen():
    try:
        data = request.get_json()
        validate(instance=data, schema=informe_imagen_schema)

        cursor = db.connection.cursor()
        query = f"select * informe_imagen where id = {data['id']};"
        cursor.execute(query)
        informe_imagen = cursor.fetchone()
         
        if informe_imagen is None:
            query = f"""
                        INSERT INTO
                          informe_imagen(
                            id,
                            id_informe,
                            ruta_imagen
                          )
                        values
                          (
                            {data['id']},
                            '{data['id_informe']}',
                            '{data['ruta_imagen']}'
                          );
                    """
            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify({'status': 'Ok', 'message': 'Imagen de informe agregada correctamente.'}), 200
        return jsonify({'status': 'Error', 'message': 'Ya existe una imagen con ese identificador'}), 500

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500


@informe_imagen.route('/api/informe_imagen', methods=['GET'])
#@token_required
def listado_informe_imagen():
    try:
        cursor = db.connection.cursor()
        query = f"select id, id_informe, ruta_imagen from informe_imagen"
        cursor.execute(query)
        informe_imagen_json = query_to_json_list(cursor)
        return jsonify({'status': 'Ok', 'message': 'Imagenes de informe obtenidas correctamente.', 'data': informe_imagen_json}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500
