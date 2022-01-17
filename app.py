# https://www.youtube.com/watch?v=D6LZnrDbQPM
from flask import Flask
from flask_mysqldb import MySQL
from config import config

app = Flask(__name__)

connection = MySQL(app)

if __name__ == '__main__':
    app.config.from_object(config['development'])   
    app.run(debug=True)     # cambiar True por False en produccion
