import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://" + os.getenv("POSTGRES_USER") + ":" + os.getenv("POSTGRES_PASSWORD") + "@" + os.getenv("SQL_HOST") + ":" + os.getenv("SQL_PORT") + "/" + os.getenv("POSTGRES_DB")
    SQLALCHEMY_TRACK_MODIFICATIONS = False