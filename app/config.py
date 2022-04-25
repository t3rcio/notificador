import os

from app.database import migrate, InterfaceDataBase

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database.db')

class Config(object):
    CSRF_ENABLED = True
    SECRET = '90a8a4bbb3860653f49bd0d0023b8fd5'
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    APP = None
    os.environ['APP_STATUS'] = 'stoped'

    def create_database():
        if not os.path.isfile(DATABASE):
            open(DATABASE, "w").close()
        InterfaceDataBase(db=DATABASE)
        os.environ['APP_STATUS'] = 'running'
    
    def migrate_database():
        migrate(DATABASE)

class DevelopmentConfig(Config):
    TESTING = True
    DEBUG = True
    IP_HOST = '0.0.0.0'
    PORT_HOST = 8001
    URL_MAIN = 'http://%s:%s/' % (IP_HOST, PORT_HOST)
    Config.create_database()
    Config.migrate_database()

class DockerConfig(Config):
    TESTING = True
    DEBUG = True
    IP_HOST = '172.19.0.5'
    PORT_HOST = 8000
    URL_MAIN = 'http://%s:%s/' % (IP_HOST, PORT_HOST)
    Config.create_database()
    Config.migrate_database()

app_config = {
    'development': DevelopmentConfig(),
    'docker': DockerConfig(),
}

app_active = os.getenv('FLASK_ENV')
