import logging
import os

class BaseConfig(object):
    DEBUG = False
    TESTING = False
    WTF_CSRF_ENABLED = True
    SECRET_KEY = 'you will never guess'
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOGGING_LOCATION = '../logs/messaging.log'
    LOGGING_LEVEL = logging.INFO
    ENV_VARIABLE = os.environ.get("ENV_VARIABLE", "default")
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'
    REDIS_CONFIG = {"host": os.environ.get("REDIS_HOST", "localhost"),
                    "username": os.environ.get("REDIS_USERNAME", ""),
                    "password": os.environ.get("REDIS_PASSWORD", ""),
                    "db": int(os.environ.get("REDIS_DB", 0)),
                    "port": int(os.environ.get("REDIS_PORT", 6379)),
                    }

config = {
    "default": "config.BaseConfig"
}

def configure_app(application):
    config_name = os.getenv('FLASK_CONFIGURATION', 'default')
    application.config.from_object(config[config_name])
    application.config.from_pyfile('config.py', silent=True)
    
    # Configure logging
    logger = logging.getLogger()
    handler = logging.FileHandler(application.config['LOGGING_LOCATION'])
    handler.setLevel(application.config['LOGGING_LEVEL'])
    formatter = logging.Formatter(application.config['LOGGING_FORMAT'])
    handler.setFormatter(formatter)
    application.logger.addHandler(handler)
    application.logger.setLevel(application.config['LOGGING_LEVEL'])