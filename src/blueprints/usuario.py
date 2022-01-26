import bcrypt
from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db

usuario = Blueprint('usuario', __name__)
usuario_schema = {
    "type": "object",
    "properties": {
        "rut": {"type": "number"},
        "password": {"type": "string"},
        "compania": {"type": "number"},
        "rol": {"type": "number"},
        "nombre": {"type": "string"},
        "apellido_paterno": {"type": "string"},
        "apellido_materno": {"type": "string"},
        "fecha_nacimiento": {
            "type": "string",
            "format": "date"
        },
        "correo": {"type": "string"},
        "telefono": {"type": "string"},
        "grupo_sanguineo": {"type": ["number", "null"]},
        "activo": {"type": "boolean"},
        "rut_cuenta": {"type": "number"}
    },
    "required": ["rut", "password", "compania", "nombre", "apellido_paterno", "apellido_materno",
                 "fecha_nacimiento", "correo", "activo", "rut_cuenta"]
}


@usuario.route('/api/usuario', methods=['POST'])
#@token_required
def crear_usuario():
    #try:
        data = request.get_json()
        validate(instance=data, schema=usuario_schema)

        cursor = db.connection.cursor()
        # Solo el sec. gral puede operar
        query = f"select rol from usuario where rut = {data['rut_cuenta']}"
        cursor.execute(query)
        if(cursor.fetchone()[0] != 3):
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        hashed_password = bcrypt.hashpw(data['password'].encode("utf-8"), bcrypt.gensalt())
        query = f"SELECT * FROM usuario where rut = {data['rut']}"
        cursor.execute(query)
        user = cursor.fetchone()

        if user is None:
            query = f"""
                        INSERT INTO
                          usuario (
                            rut,
                            compania,
                            rol,
                            nombre,
                            apellido_paterno,
                            apellido_materno,
                            fecha_nacimiento,
                            correo,
                            fecha_ingreso,
                            u_password,
                            activo,
                            grupo_sanguineo,
                            telefono
                          )
                        VALUES
                          (
                            {data['rut']},
                            {data['compania']},
                            {data['rol']},
                            '{data['nombre']}',
                            '{data['apellido_paterno']}',
                            '{data['apellido_materno']}',
                            date('{data['fecha_nacimiento']}'),
                            '{data['correo']}',
                            CURDATE(),
                            '{hashed_password.decode('utf-8')}',
                            1,
                            %s,
                            '{data['telefono']}'
                          );
                    """
            cursor.execute(query, (data['grupo_sanguineo'],))
            db.connection.commit()

            cursor.close()
            return jsonify({'status': 'Ok', 'message': 'Usuario creado correctamente.'}), 200

        return jsonify({'status': 'Error', 'message': 'Usuario ya existe.'}), 422

    #except:
    #    return jsonify({'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500


@usuario.route('/api/usuarios', methods=['GET'])
#@token_required
def listado_usuarios():
    try:
        cursor = db.connection.cursor()
        query = f"""
                    SELECT
                      u.rut,
                      c.nombre as compania,
                      r.nombre as rol,
                      u.nombre,
                      u.apellido_paterno,
                      u.apellido_materno,
                      u.fecha_nacimiento,
                      u.correo,
                      u.telefono,
                      u.fecha_ingreso,
                      gs.tipo as grupo_sanguineo,
                      u.activo
                    FROM
                      usuario u
                      INNER JOIN compania c ON u.compania = c.numero
                      INNER JOIN rol r ON r.id = u.rol
                      LEFT JOIN grupo_sanguineo gs ON gs.id = u.grupo_sanguineo
                    ORDER BY
                      c.numero
                """
        cursor.execute(query)
        users_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify({'status': 'Ok', 'message': 'Usuarios obtenidos correctamente.', 'data': users_json}), 200

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado.'}), 500


@usuario.route('/api/usuario', methods=['PUT'])
#@token_required
def actualizar_usuario():
    try:
        data = request.get_json()
        validate(instance=data, schema=usuario_schema)
        cursor = db.connection.cursor()

        # Solo el sec. gral puede operar
        query = f"select rol from usuario where rut = {data['rut_cuenta']}"
        cursor.execute(query)
        if(cursor.fetchone()[0] != 3):
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        query = f"SELECT * FROM usuario WHERE rut = {data['rut']}"
        cursor.execute(query)
        user = cursor.fetchone()

        if user:

            hashed_password = bcrypt.hashpw(data['password'].encode("utf-8"), bcrypt.gensalt())
            query = f"""
                        update
                          usuario
                        set
                          rut = {data['rut']},
                          u_password = '{hashed_password.decode('utf-8')}',
                          compania = {data['compania']},
                          rol = {data['rol']},
                          nombre = '{data['nombre']}',
                          apellido_paterno = '{data['apellido_paterno']}',
                          apellido_materno = '{data['apellido_materno']}',
                          fecha_nacimiento = '{data['fecha_nacimiento']}',
                          correo = '{data['correo']}',
                          telefono = '{data['telefono']}',
                          grupo_sanguineo = %s,
                          activo = {data['activo']}
                        where
                          rut = {data['rut']};
                    """
            cursor.execute(query, (data['grupo_sanguineo'], ))
            db.connection.commit()
            cursor.close()

            return jsonify({'status': 'Ok', 'message': 'Usuario actualizado correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'Usuario no existe.'}), 404

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500
