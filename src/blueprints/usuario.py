import bcrypt
from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db

usuario = Blueprint('usuario', __name__)
crear_usuario_schema = {
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
        "grupo_sanguineo": {"type": ["number", "string"]},
        "activo": {"type": "boolean"},
        "rut_cuenta": {"type": "number"}
    },
    "required": ["rut", "password", "compania", "nombre", "apellido_paterno", "apellido_materno",
                 "fecha_nacimiento", "correo", "activo", "rut_cuenta"]
}

actualizar_usuario_schema = {
    "type": "object",
    "required": ["rut", "rut_cuenta"],
    "anyOf": [
        {"required": ["password"]},
        {"required": ["compania"]},
        {"required": ["rol"]},
        {"required": ["nombre"]},
        {"required": ["apellido_paterno"]},
        {"required": ["apellido_materno"]},
        {"required": ["fecha_nacimiento"]},
        {"required": ["correo"]},
        {"required": ["telefono"]},
        {"required": ["grupo_sanguineo"]},
        {"required": ["activo"]}
    ],
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
        "grupo_sanguineo": {"type": ["number", "string"]},
        "activo": {"type": "boolean"},
        "rut_cuenta": {"type": "number"}
    }
}


@usuario.route('/api/usuario', methods=['POST'])
#@token_required
def crear_usuario():
    #try:
        data = request.get_json()
        validate(instance=data, schema=crear_usuario_schema)

        cursor = db.connection.cursor()
        # Solo el sec. gral puede operar
        query = f"select rol from usuario where rut = {data['rut_cuenta']}"
        cursor.execute(query)
        if(cursor.fetchone()[0] != 3):
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        hashed_password = bcrypt.hashpw(
            data['password'].encode("utf-8"), bcrypt.gensalt())
        query = f"SELECT * FROM usuario where rut = {data['rut']}"
        cursor.execute(query)
        user = cursor.fetchone()

        if user is None:
            if len(data['grupo_sanguineo']) == 0:
                data['grupo_sanguineo'] = 'null'
            query = f"""INSERT INTO usuario (rut, compania, rol, nombre, apellido_paterno, apellido_materno, fecha_nacimiento, correo,
                    fecha_ingreso, u_password, activo, grupo_sanguineo, telefono) VALUES ({data['rut']}, {data['compania']}, {data['rol']}, 
                    '{data['nombre']}', '{data['apellido_paterno']}', '{data['apellido_materno']}', date('{data['fecha_nacimiento']}'), 
                    '{data['correo']}', CURDATE(), '{hashed_password.decode('utf-8')}', 1, {data['grupo_sanguineo']}, '{data['telefono']}');"""
            print(query)
            cursor.execute(query)
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
        query = f"""SELECT u.rut, c.nombre as compania, r.nombre as rol, u.nombre, u.apellido_paterno, u.apellido_materno, u.fecha_nacimiento, 
                u.correo, u.telefono, u.fecha_ingreso, gs.tipo as grupo_sanguineo, u.activo FROM usuario u INNER JOIN compania c ON u.compania = 
                c.numero INNER JOIN rol r ON r.id = u.rol LEFT JOIN grupo_sanguineo gs ON gs.id = u.grupo_sanguineo ORDER BY c.numero"""
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
        validate(instance=data, schema=actualizar_usuario_schema)
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
            if 'password' in data:
                hashed_password = bcrypt.hashpw(
                    data['password'].encode("utf-8"), bcrypt.gensalt())
                query = f"update usuario set password = '{hashed_password.decode('utf-8')}' where rut = {data['rut']}"
                cursor.execute(query)
                db.connection.commit()

            if 'compania' in data:
                query = f"update usuario set compania = {data['compania']} where rut = {data['rut']}"
                cursor.execute(query)
                db.connection.commit()

            if 'rol' in data:
                query = f"update usuario set rol = {data['rol']} where rut = {data['rut']}"
                cursor.execute(query)
                db.connection.commit()

            if 'nombre' in data:
                query = f"update usuario set nombre = '{data['nombre']} where rut = {data['rut']}'"
                cursor.execute(query)
                db.connection.commit()

            if 'apellido_paterno' in data:
                query = f"update usuario set apellido_paterno = '{data['apellido_paterno']}' where rut = {data['rut']}"
                cursor.execute(query)
                db.connection.commit()

            if 'apellido_materno' in data:
                query = f"update usuario set apellido_materno = '{data['apellido_materno']}' where rut = {data['rut']}"
                cursor.execute(query)
                db.connection.commit()

            if 'fecha_nacimiento' in data:
                query = f"update usuario set fecha_nacimiento = '{data['fecha_nacimiento']}' where rut = {data['rut']}"
                cursor.execute(query)
                db.connection.commit()

            if 'correo' in data:
                query = f"update usuario set correo = '{data['correo']}' where rut = {data['rut']}"
                cursor.execute(query)
                db.connection.commit()

            if 'telefono' in data:
                query = f"update usuario set telefono = '{data['telefono']}' where rut = {data['rut']}"
                cursor.execute(query)
                db.connection.commit()

            if 'grupo_sanguineo' in data:
                query = f"update usuario set grupo_sanguineo = {data['grupo_sanguineo']} where rut = {data['rut']}"
                cursor.execute(query)
                db.connection.commit()

            if 'activo' in data:
                query = f"update usuario set activo = {data['activo']} where rut = {data['rut']}"
                cursor.execute(query)
                db.connection.commit()

            cursor.close()

            return jsonify({'status': 'Ok', 'message': 'Usuario actualizado correctamente.'}), 200

        return jsonify({'status': 'Ok', 'message': 'Usuario no existe.'}), 404

    except:
        return jsonify({'status': 'Error', 'message': 'Error inesperado, verifique que la información cargada sea correcta.'}), 500
