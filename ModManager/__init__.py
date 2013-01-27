import os
from flask import Flask, g, session
from flask.ext.openid import OpenID
from werkzeug.contrib.cache import SimpleCache

application = Flask(__name__)

ADMINS = ['bandycj@gmail.com']
import models

# setup flask-openid
oid = OpenID(application)

cache = None
if 'nt' in os.name:
    cache = SimpleCache()
else:
    from werkzeug.contrib.cache import MemcachedCache
    cache = MemcachedCache(['/tmp/memcached.sock'])

@application.before_request
def before_request():
    g.user = None
    if 'openid' in session:
        g.user = models.User.query.filter_by(openid=session['openid']).first()


from ModManager.views import site, auth
import  urls
