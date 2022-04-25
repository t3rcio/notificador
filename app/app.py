# coding: utf-8

from logging import FileHandler
from datetime import datetime

from flask import Flask

from app.config import app_config, app_active, BASE_DIR
from app.routes import routes


config = app_config[app_active]

def create_app(config_name):
    app = Flask(__name__)
    app.secret_key = config.SECRET
    app.config.from_pyfile('config.py')

    for r in routes:
        app.add_url_rule(r.url, view_func=r.view, methods=['GET'])

    log_file_name = 'logs/{}.log'.format(datetime.now().strftime('%Y_%m_%d'))
    LogHandler = FileHandler(filename=log_file_name)
    app.logger.addHandler(LogHandler)    
    return app