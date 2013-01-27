from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import  Column, Integer, String, Text, Boolean
from ModManager import application


__author__ = 'e83800'


application.config.update(
    SQLALCHEMY_DATABASE_URI='sqlite:///./test.db',
    SECRET_KEY='asdf',
    DEBUG=True
)
db = SQLAlchemy(application)

class User(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(length=60))
    email = Column(String(length=200))
    openid = Column(String(length=200))
    admin = Column(Boolean, default=False)
    active =  Column(Boolean, default=False)

    def __init__(self, name=None, email=None, openid=None, admin=None, active=None):
        self.name = name
        self.email = email
        self.openid = openid
        self.admin = admin
        self.active = active


class Mod(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(length=60), unique=True)
    link = Column(String(length=200))
    description = Column(Text(length=500))
    critical = Column(Boolean(), default=False)
    bukkit = Column(Boolean(), default=False)
    latestVersion = Column(String(length=16))
    mcVersion = Column(String(length=16))

    def __init__(self, name):
        self.name = name

    def _asdict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

db.create_all()