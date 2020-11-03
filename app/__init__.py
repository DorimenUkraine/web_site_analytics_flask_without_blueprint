from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Command, Shell
from flask_login import LoginManager
import os, config
from .extensions import geo_ip

# создание экземпляра приложения
app = Flask(__name__, template_folder="templates/app", static_folder="static")
app.config.from_object(os.environ.get('FLASK_ENV') or 'config.DevelopmentConfig')
# app.config.from_object('config.DevelopmentConfig')

# инициализирует расширения
db = SQLAlchemy(app)
geo = geo_ip.Geo(app.config.get('GEOIP2_DATABASE_NAME', ''))
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# import views
from . import views