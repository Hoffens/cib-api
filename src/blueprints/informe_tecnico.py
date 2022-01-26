import bcrypt
from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db

inf_tec = Blueprint('inf_tec', __name__)
inf_tec_schema = {
    "type": "object",
    "properties": {
        "codigo": {"type": "string"},
        "origen": {"type": "string"},
        "causa": {"type": "string"},
        "fecha": {
            "type": "string",
            "format": "date"
        },
        "descripcion": {"type": "string"},
        "inf_usuario": {"type": "number"},
        "victimas": {"type": "string"},
        "bienes_siniestrados": {"type": "string"},
        "seguro": {"type": "string"},
        "investigador": {"type": "number"},
        "compania": {"type": "number"},
        "rut_cuenta": {"type": "number"}
    },
    "required": ["codigo", "origen", "causa", "fecha", "descripcion", "inf_usuario", "victimas", "bienes_siniestrados", "seguro", "investigador", "rut_cuenta"]
}


@inf_tec.route('/api/inf_tec', methods=['POST'])
#@token_required
def crear_inf_tec():
    try:
        data = request.get_json()
        validate(instance=data, schema=inf_tec_schema)

        cursor = db.connection.cursor()
        # Solo el sec. gral puede operar

        query = f"SELECT * FROM informe_tecnico where codigo = {data['codigo']}"
        cursor.execute(query)
        inf_tec = cursor.fetchone()

        if inf_tec is None:
            query = f"""
                        INSERT INTO
                          informe_tecnico (
                            codigo,
                            origen,
                            causa,
                            fecha,
                            descripcion,
                            inf_usuario,
                            victimas,
                            bienes_siniestrados,
                            seguro,
                            investigador,
                            compania,
                          )
                        VALUES
                          (
                            '{data['codigo']}',
                            '{data['origen']}',
                            '{data['causa']}',
                            '{data['fecha']}',
                            '{data['descripcion']}',
                            {data['inf_usuario']},
                            '{data['victimas']}',
                            '{data['bienes_siniestrados']}',
                            '{data['seguro']}',
                            {data['investigador']},
                            {data['compania']}
                          );
                    """
            cursor.execute(query)
            db.connection.commit()
            cursor.close()
            return jsonify({'status': 'Ok', 'message': 'Informe tecnico creado correctamente.'}), 200

        return jsonify({'status': 'Error', 'message': 'Informe tecnico ya existe.'}), 422

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500


@inf_tec.route('/api/inf_tec', methods=['GET'])
#@token_required
def listado_inf_tec():
    try:
        cursor = db.connection.cursor()
        query = f"""
                    SELECT
                      i.codigo,
                      i.origen,
                      i.causa,
                      i.fecha,
                      i.descripcion,
                      i.inf_usuario,
                      i.victimas,
                      i.bienes_siniestrados,
                      i.seguro,
                      i.investigador,
                      c.nombre as compania
                    FROM
                      informe_tecnico i
                      INNER JOIN compania c ON i.compania = c.numero
                    ORDER BY
                      i.codigo
                """
        cursor.execute(query)
        inf_tec_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify({'status': 'Ok', 'message': 'Usuarios obtenidos correctamente.', 'data': inf_tec_json}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500


@inf_tec.route('/api/inf_tec', methods=['PUT'])
#@token_required
def actualizar_inf_tec():
    try:
        data = request.get_json()
        validate(instance=data, schema=inf_tec_schema)
        cursor = db.connection.cursor()

        query = f"SELECT * FROM informe_tecnico WHERE codigo = '{data['codigo']}'"
        cursor.execute(query)
        user = cursor.fetchone()

        if user:
            query = f"""
                        update
                          informe_tecnico
                        set
                          codigo = '{data['codigo']}',
                          origen = '{data['origen']}',
                          causa = '{data['causa']}',
                          fecha = '{data['fecha']}',
                          descripcion = '{data['descripcion']}',
                          inf_usuario = {data['inf_usuario']},
                          victimas = '{data['victimas']}',
                          bienes_siniestrados = '{data['bienes_siniestrados']}',
                          seguro = '{data['seguro']}',
                          investigador = {data['investigador']},
                          compania = {data['compania']},
                        where
                          codigo = '{data['codigo']}';
                    """
            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify({'status': 'Ok', 'message': 'Informe tecnico actualizado correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'Informe tecnico no existe.'}), 404

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500
