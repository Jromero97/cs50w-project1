from os import environ

uri = environ.get('SQLALCHEMY_DATABASE_URI')

if uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)


class Config(object):
    """
    Config class to setting in flask project
    """

    if not uri:
        raise RuntimeError('You need to set SQLALCHEMY_DATABASE_URI variable')

    DATABASE_URL = uri
    SECRET_KEY = environ.get('SECRET_KEY')
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = '/tmp/flask_session'
