import urllib2

from flask import render_template, jsonify, flash, redirect, url_for, json, request, abort, g
from ModManager import models

from ModManager.models import Mod, User, Server
from ModManager.views.auth import login_required, admin_required
from ModManager.views.forms.Forms import ModForm, ServerForm


__author__ = 'e83800'

MOD_INFO = "http://www.selurgniman.org/mod_info.json"

def index():
    users = None
    if g.user != None and g.user.admin == True:
        users = User.query.all()

    servers = Server.query.all()
    mods = {}

    for server in servers:
        try:
            mods[server.name] = json.loads(urllib2.urlopen(server.mods_url).read())
        except ValueError:
            mods[server.name] = {}

    update_info = json.loads(urllib2.urlopen(MOD_INFO).read())

    return render_template('index.html', users=users, servers=servers, mods=mods, update_info=update_info)


@login_required
def server_info():
    servers = []
    for result in Server.query.all():
        servers.append(result._asdict())
    return jsonify(servers=servers)


@admin_required
def create_update_mod(mod_id=None):
    mod = Mod.query.filter_by(id=mod_id).first()
    form = ModForm(request.form, obj=mod)

    if form.validate_on_submit():
        if mod is None:
            mod = Mod(form.name.data)
        form.populate_obj(mod)
        if models.commit(mod):
            flash("Success")
            return redirect(url_for('index'))
        else:
            flash("Failed")
    return render_template('create_update_mod.html', form=form, mod_id=mod_id)


@admin_required
def create_update_server(server_id=None):
    server = Server.query.filter_by(serverId=server_id).first()
    form = ServerForm(request.form, obj=server)

    if form.validate_on_submit():
        if server is None:
            server = Server(form.name.data, form.ip.data, form.port.data, form.bukkit.data, form.forge.data, form.mods_url.data)
        form.populate_obj(server)
        if models.commit(server):
            flash("Success")
            return redirect(url_for('index'))
        else:
            flash("Failed")

    return render_template('create_update_server.html', form=form, server_id=server_id)


@admin_required
def delete_mod(mod_id=None):
    mod = Mod.query.filter_by(id=mod_id).first()
    if models.delete(mod):
        flash("Success")
        return redirect(url_for('index'))
    else:
        flash("Delete failed!")
    return redirect(url_for('create_update_mod', mod_id=mod_id))


@admin_required
def delete_server(server_id=None):
    server = Server.query.filter_by(id=server_id).first()
    if models.delete(server):
        flash("Success")
        return redirect(url_for('index'))
    else:
        flash("Delete failed!")
    return redirect(url_for('create_update_server', server_id=server_id))
