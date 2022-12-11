from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mysqldb import MySQL
import pymysql



def create_app():
    conn = pymysql.connect(
        user="root",
        password="", #GANTI PASSWORDNYA
        host="127.0.0.1",
        port=3306,
        database="tubestst",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'aduhAPIpanas'

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


