from ModManager import application
from ModManager.views.site import index, create_update, mod_info, delete
from views import auth

__author__ = 'e83800'

application.add_url_rule('/', 'index', index)
application.add_url_rule('/create_update', 'create_update', create_update, methods=['GET', 'POST'])
application.add_url_rule('/create_update/<id>', 'create_update', create_update, methods=['GET', 'POST'])
application.add_url_rule('/delete/<id>', 'delete', delete)
application.add_url_rule('/mod_info', 'mod_info', mod_info)

application.add_url_rule('/auth/login', 'login', auth.login, methods=['GET', 'POST'])
application.add_url_rule('/auth/logout', 'logout', auth.logout, methods=['GET', 'POST'])
application.add_url_rule('/auth/edit_user/<id>', 'edit_user', auth.edit_user, methods=['GET', 'POST'])