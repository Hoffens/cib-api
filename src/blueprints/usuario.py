import bcrypt
from flask import Blueprint, jsonify, request
from jsonschema import validate
from src.service.token_required import token_required
from src.service.to_json import query_to_json_list, query_to_json
from extensions import db


usuario = Blueprint('usuario', __name__)
usuario_schema = {
    "type" : "object",
    "properties" : {
        "rut" : {"type" : "number"},
        "password" : {"type" : "string"},
        "compania" : {"type" : "number"},
        "nombre" : {"type" : "string"},
        "apellido_paterno" : {"type" : "string"},
        "apellido_materno" : {"type" : "string"},
        "fecha_nacimiento": {
            "type": "string",
            "format": "date"
        },
        "correo" : {"type" : "string"},
        "telefono" : {"type" : "string"},
        "fecha_ingreso": {
            "type": "string",
            "format": "date"
        },
        "grupo_sanguineo" : {"type" : "number"},
        "activo" : {"type" : "boolean"},
        "rut_cuenta": {"type": "number"}
    },
    "required": ["rut", "password", "compania", "nombre", "apellido_paterno", "apellido_materno",
                "fecha_nacimiento", "correo", "activo", "rut_cuenta"]
}

usuario_compania_schema = {
    "type" : "object",
    "properties" : {
        "rut" : {"type" : "number"},
        "password" : {"type" : "string"},
        "compania" : {"type" : "number"},
        "nombre" : {"type" : "string"},
        "apellido_paterno" : {"type" : "string"},
        "apellido_materno" : {"type" : "string"},
        "fecha_nacimiento": {
            "type": "string",
            "format": "date"
        },
        "correo" : {"type" : "string"},
        "telefono" : {"type" : "string"},
        "fecha_ingreso": {
            "type": "string",
            "format": "date"
        },
        "grupo_sanguineo" : {"type" : "number"},
        "activo" : {"type" : "boolean"},
        "rut_cuenta": {"type" : "number"}
    },
    "required": ["rut", "password", "compania", "nombre", "apellido_paterno", "apellido_materno",
                "fecha_nacimiento", "correo", "activo"]
}

obt_usuario_schema = {
        "type" : "object",
        "properties" : {
            "rut" : {"type" : "number"}
        },
        "required": ["rut"]
}


@usuario.route('/api/usuario', methods=['POST'])
#@token_required
def crear_usuario():
    try:
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
            query = f"""INSERT INTO usuario (rut, compania, rol, nombre, apellido_paterno, apellido_materno, fecha_nacimiento, correo, telefono,
                    fecha_ingreso, grupo_sanguineo, u_password, activo) VALUES ({data['rut']}, {data['compania']}, {data['rol']}, 
                    '{data['nombre']}', '{data['apellido_paterno']}', '{data['apellido_materno']}', date('{data['fecha_nacimiento']}'), 
                    '{data['correo']}', '{data['telefono']}', date('{data['fecha_ingreso']}'), {data['grupo_sanguineo']}, 
                    '{hashed_password.decode('utf-8')}', 1);"""
            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify({ 'status': 'Ok', 'message' : 'Usuario creado correctamente.' }), 200

        return jsonify({ 'status': 'Error', 'message' : 'Usuario ya existe.' }), 422
        
    except:
        return jsonify({ 'status': 'Error', 'message' : 'Error inesperado, verifique que la información cargada sea correcta.' }), 500


@usuario.route('/api/usuario', methods=['GET'])
#@token_required
def obtener_usuario():
    try:
        data = request.get_json()
        validate(instance=data, schema=obt_usuario_schema)
        cursor = db.connection.cursor()
        query = f"""select * from usuario where rut = {data['rut']}"""
        cursor.execute(query)
        usuario = query_to_json(cursor)

        if usuario is None:
            cursor.close()
            return jsonify({ 'status': 'Error', 'message' : 'Usuario no existe.' }), 400

        query = f"""SELECT u.rut, c.nombre as compania, r.nombre as rol, u.nombre, u.apellido_paterno, u.apellido_materno, u.fecha_nacimiento, 
                u.correo, u.telefono, u.fecha_ingreso, gs.tipo as grupo_sanguineo, u.activo FROM usuario u INNER JOIN compania c ON u.compania = 
                c.numero INNER JOIN rol r ON r.id = u.rol INNER JOIN grupo_sanguineo gs ON gs.id = u.grupo_sanguineo WHERE u.rut = {data['rut']}"""
        cursor.execute(query)
        usuario = query_to_json(cursor)
        cursor.close()

        return jsonify({ 'status': 'Ok', 'message' : 'Usuario obtenido correctamente.', 'data' : usuario }), 200

    except:       
        return jsonify({ 'status': 'Error', 'message' : 'Error inesperado.' }), 500


@usuario.route('/api/usuarios', methods=['GET'])
#@token_required
def listado_usuarios():
    try:
        cursor = db.connection.cursor()
        query = f"""SELECT u.rut, c.nombre as compania, r.nombre as rol, u.nombre, u.apellido_paterno, u.apellido_materno, u.fecha_nacimiento, 
                u.correo, u.telefono, u.fecha_ingreso, gs.tipo as grupo_sanguineo, u.activo FROM usuario u INNER JOIN compania c ON u.compania = 
                c.numero INNER JOIN rol r ON r.id = u.rol INNER JOIN grupo_sanguineo gs ON gs.id = u.grupo_sanguineo ORDER BY c.numero"""
        cursor.execute(query)
        users_json = query_to_json_list(cursor)
        cursor.close()

        return jsonify({ 'status': 'Ok', 'message' : 'Usuarios obtenidos correctamente.', 'data' : users_json }), 200

    except:       
        return jsonify({ 'status': 'Error', 'message' : 'Error inesperado.' }), 500


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
            data = request.get_json()        
            validate(instance=data, schema=usuario_schema)
            hashed_password = bcrypt.hashpw(data['password'].encode("utf-8"), bcrypt.gensalt())
            
            query = f"""UPDATE usuario SET compania = {data['compania']}, rol = {data['rol']}, nombre = '{data['nombre']}', 
                    apellido_paterno = '{data['apellido_paterno']}', apellido_materno = '{data['apellido_materno']}', 
                    fecha_nacimiento = date('{data['fecha_nacimiento']}'), correo = '{data['correo']}', telefono = '{data['telefono']}', 
                    fecha_ingreso = date('{data['fecha_ingreso']}'), grupo_sanguineo = {data['grupo_sanguineo']}, u_password = 
                    '{hashed_password.decode('utf-8')}', activo = {data['activo']} WHERE rut = {data['rut']}"""

            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify({ 'status': 'Ok', 'message' : 'Usuario actualizado correctamente.'}), 200

        return jsonify({ 'status': 'Ok', 'message' : 'Usuario no existe.'}), 404

    except:
        return jsonify({ 'status': 'Error', 'message' : 'Error inesperado, verifique que la información cargada sea correcta.' }), 500


@usuario.route('/api/usuario_compania', methods=['POST'])
#@token_required
def crear_usuario_compania():
    try:
        data = request.get_json()
        validate(instance=data, schema=usuario_compania_schema)
        query = f"select compania, rol from usuario where rut = {data['rut_cuenta']}"
        cursor = db.connection.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        compania = row[0]
        rol = row[1]

        # No es secretario ni secretario gral.
        if rol not in 7:
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        # No corresponde la compania
        if compania != data['compania']:
            return jsonify({'status': 'Error', 'message': 'Compañia invalida.'}), 500

        hashed_password = bcrypt.hashpw(data['password'].encode("utf-8"), bcrypt.gensalt())
        query = f"""SELECT * FROM usuario where rut = {data['rut']}"""
        cursor.execute(query)
        user = cursor.fetchone()

        if user is None:
            query = f"""INSERT INTO usuario (rut, compania, rol, nombre, apellido_paterno, apellido_materno, fecha_nacimiento, correo, telefono,
                    fecha_ingreso, grupo_sanguineo, u_password, activo) VALUES ({data['rut']}, {data['compania']}, {data['rol']}, 
                    '{data['nombre']}', '{data['apellido_paterno']}', '{data['apellido_materno']}', date('{data['fecha_nacimiento']}'), 
                    '{data['correo']}', '{data['telefono']}', date('{data['fecha_ingreso']}'), {data['grupo_sanguineo']}, 
                    '{hashed_password.decode('utf-8')}', 1);"""
            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify({ 'status': 'Ok', 'message' : 'Usuario creado correctamente.' }), 200

        return jsonify({ 'status': 'Error', 'message' : 'Usuario ya existe.' }), 422
        
    except:
        return jsonify({ 'status': 'Error', 'message' : 'Error inesperado, verifique que la información cargada sea correcta.' }), 500


@usuario.route('/api/usuario_compania', methods=['PUT'])
#@token_required
def actualizar_usuario_compania():
    try:
        data = request.get_json()        
        validate(instance=data, schema=usuario_schema)

        query = f"select compania from usuario where rut = {data['rut_cuenta']}"
        cursor = db.connection.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        compania = row[0]
        rol = row[1]
        # No es secretario ni secretario gral.
        if rol != 7:
            return jsonify({'status': 'Error', 'message': 'Permisos insuficientes.'}), 500

        if compania != data['compania']:
            return jsonify({'status': 'Error', 'message': 'Compañia invalida.'}), 500

        query = f"SELECT * FROM usuario WHERE rut = {data['rut']}"
        cursor.execute(query)
        user = cursor.fetchone()

        if user:
            data = request.get_json()        
            validate(instance=data, schema=usuario_schema)
            hashed_password = bcrypt.hashpw(data['password'].encode("utf-8"), bcrypt.gensalt())
            
            query = f"""UPDATE usuario SET compania = {data['compania']}, rol = {data['rol']}, nombre = '{data['nombre']}', 
                    apellido_paterno = '{data['apellido_paterno']}', apellido_materno = '{data['apellido_materno']}', 
                    fecha_nacimiento = date('{data['fecha_nacimiento']}'), correo = '{data['correo']}', telefono = '{data['telefono']}', 
                    fecha_ingreso = date('{data['fecha_ingreso']}'), grupo_sanguineo = {data['grupo_sanguineo']}, u_password = 
                    '{hashed_password.decode('utf-8')}', activo = {data['activo']} WHERE rut = {data['rut']}"""

            cursor.execute(query)
            db.connection.commit()
            cursor.close()

            return jsonify({ 'status': 'Ok', 'message' : 'Usuario actualizado correctamente.'}), 200

        return jsonify({ 'status': 'Ok', 'message' : 'Usuario no existe.'}), 404

    except:
        return jsonify({ 'status': 'Error', 'message' : 'Error inesperado, verifique que la información cargada sea correcta.' }), 500
