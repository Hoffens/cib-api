import bcrypt
from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db


usuario_compania = Blueprint('usuario_compania', __name__)

crear_usuario_compania_schema = {
    "type" : "object",
    "properties" : {
        "rut" : {"type" : "number"},
        "password" : {"type" : "string"},
        "rol": {"type" : "number"},
        "nombre" : {"type" : "string"},
        "apellido_paterno" : {"type" : "string"},
        "apellido_materno" : {"type" : "string"},
        "fecha_nacimiento": {
            "type": "string",
            "format": "date"
        },
        "correo" : {"type" : "string"},
        "telefono" : {"type" : "string"},
        "grupo_sanguineo" : {"type" : "number"},
        "activo" : {"type" : "boolean"},
        "rut_cuenta": {"type": "number"}
    },
    "required": ["rut", "password", "nombre", "apellido_paterno", "apellido_materno",
                "fecha_nacimiento", "correo", "activo", "rut_cuenta"]
}

actualizar_usuario_compania_schema = {
    "type" : "object",
    "required": ["rut", "rut_cuenta"],
    "anyOf": [
        {"required": ["password"]},
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
    "properties" : {
        "rut" : {"type" : "number"},
        "password" : {"type" : "string"},
        "rol": {"type" : "number"},
        "nombre" : {"type" : "string"},
        "apellido_paterno" : {"type" : "string"},
        "apellido_materno" : {"type" : "string"},
        "fecha_nacimiento": {
            "type": "string",
            "format": "date"
        },
        "correo" : {"type" : "string"},
        "telefono" : {"type" : "string"},
        "grupo_sanguineo" : {"type" : "number"},
        "activo" : {"type" : "boolean"},
        "rut_cuenta": {"type": "number"}
    }
}


@usuario_compania.route('/api/usuario_compania', methods=['POST'])
#@token_required
def crear_usuario_compania():
    try:
        data = request.get_json()
        validate(instance=data, schema=crear_usuario_compania_schema)
        query = f"select compania, rol from usuario_compania where rut = {data['rut_cuenta']}"
        cursor = db.connection.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        compania = row[0]
        rol = row[1]

        # No es secretario ni secretario gral.
        if rol != 7:
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        query = f"""SELECT * FROM usuario_compania where rut = {data['rut']}"""
        cursor.execute(query)
        user = cursor.fetchone()

        if user is None:
            hashed_password = bcrypt.hashpw(data['password'].encode("utf-8"), bcrypt.gensalt())
            # Se ingresa la informacion obligatoria
            query = f"""INSERT INTO usuario_compania (rut, compania, rol, nombre, apellido_paterno, apellido_materno, fecha_nacimiento, correo,
                    fecha_ingreso, u_password, activo) VALUES ({data['rut']}, '{compania}', {data['rol']}, 
                    '{data['nombre']}', '{data['apellido_paterno']}', '{data['apellido_materno']}', date('{data['fecha_nacimiento']}'), 
                    '{data['correo']}', CURDATE(), '{hashed_password.decode('utf-8')}', 1);"""
            cursor.execute(query)
            db.connection.commit()

            if "telefono" in data:
                query = f"insert into usuario (telefono) values ('{data['telefono']}');"
                cursor.execute(query)
                db.connection.commit()

            if "grupo_sanguineo" in data:
                query = f"insert into usuario (grupo_sanguineo) values ({data['grupo_sanguineo']});"
                cursor.execute(query)
                db.connection.commit()

            cursor.close()
            return jsonify({ 'status': 'Ok', 'message' : 'usuario_compania creado correctamente.' }), 200

        return jsonify({ 'status': 'Error', 'message' : 'usuario_compania ya existe.' }), 422
        
    except:
        return jsonify({ 'status': 'Error', 'message' : 'Error inesperado, verifique que la información cargada sea correcta.' }), 500


@usuario_compania.route('/api/usuario_compania', methods=['PUT'])
#@token_required
def actualizar_usuario_compania_compania():
    try:
        data = request.get_json()        
        validate(instance=data, schema=actualizar_usuario_compania_schema)

        query = f"select compania, rol from usuario_compania where rut = {data['rut_cuenta']}"
        cursor = db.connection.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        compania = row[0]
        rol = row[1]
        # No es secretario ni secretario gral.
        if rol != 7:
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        query = f"SELECT * FROM usuario_compania WHERE rut = {data['rut']}"
        cursor.execute(query)
        user = cursor.fetchone()

        if user:
            if 'password' in data:
                hashed_password = bcrypt.hashpw(
                    data['password'].encode("utf-8"), bcrypt.gensalt())
                query = f"update usuario set password = '{hashed_password.decode('utf-8')}'"
                cursor.execute(query)
                db.connection.commit()

            if 'rol' in data:
                query = f"update usuario set rol = {data['rol']}"
                cursor.execute(query)
                db.connection.commit()

            if 'nombre' in data:
                query = f"update usuario set nombre = '{data['nombre']}'"
                cursor.execute(query)
                db.connection.commit()

            if 'apellido_paterno' in data:
                query = f"update usuario set apellido_paterno = '{data['apellido_paterno']}'"
                cursor.execute(query)
                db.connection.commit()

            if 'apellido_materno' in data:
                query = f"update usuario set apellido_materno = '{data['apellido_materno']}'"
                cursor.execute(query)
                db.connection.commit()

            if 'fecha_nacimiento' in data:
                query = f"update usuario set fecha_nacimiento = '{data['fecha_nacimiento']}'"
                cursor.execute(query)
                db.connection.commit()

            if 'correo' in data:
                query = f"update usuario set correo = '{data['correo']}'"
                cursor.execute(query)
                db.connection.commit()

            if 'telefono' in data:
                query = f"update usuario set telefono = '{data['telefono']}'"
                cursor.execute(query)
                db.connection.commit()

            if 'grupo_sanguineo' in data:
                query = f"update usuario set grupo_sanguineo = {data['grupo_sanguineo']}"
                cursor.execute(query)
                db.connection.commit()

            if 'activo' in data:
                query = f"update usuario set activo = {data['activo']}"
                cursor.execute(query)
                db.connection.commit()

            cursor.close()

            return jsonify({ 'status': 'Ok', 'message' : 'usuario_compania actualizado correctamente.'}), 200

        return jsonify({ 'status': 'Ok', 'message' : 'usuario_compania no existe.'}), 404

    except:
        return jsonify({ 'status': 'Error', 'message' : 'Error inesperado, verifique que la información cargada sea correcta.' }), 500
