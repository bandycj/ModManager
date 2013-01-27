from functools import wraps
from flask import render_template, g, redirect, request, session, flash, url_for, jsonify
from ModManager import oid, ADMINS
from ModManager.models import User, db
from flask.ext.wtf import Form
from sqlalchemy.exc import IntegrityError, OperationalError
from werkzeug.exceptions import HTTPException
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.validators import Required, Email

__author__ = 'e83800'

UserForm = model_form(User, base_class=Form, field_args={
    'name': {
        'validators': [Required()]
    },
    'email': {
        'validators': [Email(), Required()]
    }
})

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None or 'openid' not in session:
            return redirect(url_for('login', next=request.url))
        if g.user.active == False:
            flash(u'Account not active!')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if g.user.admin == False:
            flash(u'Admin access required!')
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return decorated_function


@oid.loginhandler
def login():
    """Does the login via OpenID. Has to call into `oid.try_login`
    to start the OpenID machinery.
    """
    # if we are already logged in, go back to were we came from
    if g.user is not None and g.user.active:
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid')
        if openid:
            return oid.try_login(openid, ask_for=['email', 'fullname',
                                                  'nickname'])
    return redirect(url_for('index'))


@oid.after_login
def create_or_login(resp):
    """This is called when login with OpenID succeeded and it's not
    necessary to figure out if this is the users's first login or not.
    This function has to redirect otherwise the user will be presented
    with a terrible URL which we certainly don't want.
    """
    session['openid'] = resp.identity_url
    user = User.query.filter_by(email=resp.email).first()
    if user is not None:
        flash(u'Successfully signed in')
    else:
        create_profile(
            name=resp.fullname or resp.nickname,
            email=resp.email)
        user = User.query.filter_by(email=resp.email).first()
        flash(u'Successfully signed in')

    g.user = user
    return redirect(oid.get_next_url())

def create_profile(name, email):
    """If this is the user's first login, the create_or_login function
    will redirect here so that the user can set up his profile.
    """
    if g.user is not None or 'openid' not in session:
        return redirect(url_for('index'))
    admin = False
    active = False
    for adminAddress in ADMINS:
        if email == adminAddress:
            admin = True
            active = True
            break
    db.session.add(User(name, email, session['openid'], admin, active))
    db.session.commit()

@login_required
def logout():
    session.pop('openid', None)
    g.user = None
    flash(u'You have been signed out')
    return redirect(url_for('login', next=oid.get_next_url()))


@admin_required
def edit_user(id=None):
    user = User.query.filter_by(id=id).first()
    form = UserForm(request.form, obj=user)

    if form.validate_on_submit():
        if user is None:
            user = User()

        form.populate_obj(user)
        db.session.add(user)
        try:
            db.session.commit()
            flash("Success")
            return redirect(url_for('index'))
        except (IntegrityError, OperationalError) as e:
            flash("Failed")

    return render_template('create_update.html', form=form, id=id)

