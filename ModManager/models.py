from flask import flash, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import  Column, Integer, String, Text, Boolean
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import relationship
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
    name = Column(String(length=60), primary_key=True)
    link = Column(String(length=200))
    latestVersion = Column(String(length=16))

    def __init__(self, name):
        self.name = name

    def _asdict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Server(db.Model):
    serverId = Column(Integer, primary_key=True)
    name = Column(String(length=60), unique=True)
    ip = Column(String(length=15))
    port = Column(Integer(length=6))
    bukkit = Column(Boolean(), default=False)
    forge = Column(Boolean(), default=False)
    mods_url = Column(Text())

    def __init__(self, name, ip, port, bukkit, forge, mods_url):
        self.name = name
        self.ip = ip
        self.port = port
        self.bukkit = bukkit
        self.forge = forge
        self.mods_url = mods_url

    def _asdict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

def commit(obj):
    db.session.add(obj)
    try:
        db.session.commit()
        return True
    except (IntegrityError, OperationalError) as e:
        return False

def delete(obj):
    try:
        db.session.delete(obj)
        db.session.commit()
        return True
    except (IntegrityError, OperationalError) as e:
        return False

db.create_all()