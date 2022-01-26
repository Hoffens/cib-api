# https://www.youtube.com/watch?v=D6LZnrDbQPM
from flask import Flask
from config import config

def create_app():
    app = Flask(__name__)
    app.config.from_object(config['development'])   

    register_extensions(app)
    register_blueprints(app)

    return app

def register_extensions(app):
    from extensions import db

    db.init_app(app)

def register_blueprints(app):
    from src.blueprints.auth import auth
    from src.blueprints.usuario import usuario
    from src.blueprints.usuario_compania import usuario_compania
    from src.blueprints.perfil_usuario import perfil_usuario
    from src.blueprints.compania import compania
    from src.blueprints.rol import rol
    from src.blueprints.acto import acto
    from src.blueprints.carro import carro
    from src.blueprints.herramienta import herramienta
    from src.blueprints.tipo_carro import tipo_carro
    from src.blueprints.modelo_carro import modelo_carro
    from src.blueprints.marca_carro import marca_carro
    from src.blueprints.tipo_herramienta import tipo_herramienta
    from src.blueprints.apodo_herramienta import apodo_herramienta
    from src.blueprints.grupo_sanguineo import grupo_sanguineo
    from src.blueprints.informe_tecnico import inf_tec
    from src.blueprints.asistencia_usuario import asistencia_usuario

    app.register_blueprint(auth)    
    app.register_blueprint(usuario)
    app.register_blueprint(usuario_compania)
    app.register_blueprint(perfil_usuario)
    app.register_blueprint(compania)    
    app.register_blueprint(rol)
    app.register_blueprint(acto)
    app.register_blueprint(carro)
    app.register_blueprint(herramienta)
    app.register_blueprint(tipo_carro)
    app.register_blueprint(modelo_carro)
    app.register_blueprint(marca_carro)
    app.register_blueprint(tipo_herramienta)
    app.register_blueprint(apodo_herramienta)
    app.register_blueprint(grupo_sanguineo)
    app.register_blueprint(inf_tec)
    app.register_blueprint(asistencia_usuario)


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)     # cambiar True por False en produccion
