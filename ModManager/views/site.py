import urllib2
from flask import render_template, jsonify, flash, redirect, url_for, json, request
from flask.ext.wtf import Form
from models import Mod, db, User
from sqlalchemy.exc import IntegrityError, OperationalError
from views.auth import login_required, admin_required
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.validators import URL, Required

__author__ = 'e83800'

VERSION_INFO_URL = "http://wiper.myftp.org/mod_versions.json"
ModForm = model_form(Mod, base_class=Form, field_args={
    'name': {
        'validators': [Required()]
    },
    'link': {
        'validators': [URL()]
    }
})

class Users(object):
    pass


def index():
    mods = Mod.query.all()
    mod_info = json.loads(urllib2.urlopen(VERSION_INFO_URL).read())
    users = User.query.all()
    return render_template('index.html', users=users, mods=mods, mod_info=mod_info)


@login_required
def mod_info():
    mod_info = json.loads(urllib2.urlopen(VERSION_INFO_URL).read())
    mods = []
    for result in Mod.query.all():
        mods.append(result._asdict())
    return jsonify(mod_list=mods, version_list=mod_info)


@admin_required
def create_update(id=None):
    mod = Mod.query.filter_by(id=id).first()
    form = ModForm(request.form, obj=mod)

    if form.validate_on_submit():
        if mod is None:
            mod = Mod(form.name.data)

        form.populate_obj(mod)
        db.session.add(mod)
        try:
            db.session.commit()
            flash("Success")
            return redirect(url_for('index'))
        except (IntegrityError, OperationalError) as e:
            flash("Failed")

    return render_template('create_update.html', form=form, id=id)


@admin_required
def delete(id=None):
    mod = Mod.query.filter_by(id=id).first()
    try:
        db.session.delete(mod)
        db.session.commit()
        flash("Success")
        return redirect(url_for('index'))
    except (IntegrityError, OperationalError) as e:
        flash("Delete failed!")
    return redirect(url_for('create_update', id=id))