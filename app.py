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
    from src.blueprints.user import user
    from src.blueprints.compania import compania
    from src.blueprints.rol import rol

    app.register_blueprint(auth)    
    app.register_blueprint(user)
    app.register_blueprint(compania)    
    app.register_blueprint(rol)



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)     # cambiar True por False en produccion
