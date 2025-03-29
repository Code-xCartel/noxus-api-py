import logging.config

from app.create_app import create_app

app = create_app()
logging.config.dictConfig(app.config.LOGGING_CONFIG)
