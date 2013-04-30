from ModManager import application
from ModManager.views.site import index, create_update_mod, mod_info, delete_mod, delete_server, create_update_server, server_info
from views import auth

__author__ = 'e83800'

application.add_url_rule('/', 'index', index)
application.add_url_rule('/create_update_mod', 'create_update_mod', create_update_mod, methods=['GET', 'POST'])
application.add_url_rule('/create_update_mod/<mod_id>', 'create_update_mod', create_update_mod, methods=['GET', 'POST'])
application.add_url_rule('/delete_mod/<mod_id>', 'delete_mod', delete_mod)
application.add_url_rule('/mod_info/<server_id>', 'mod_info', mod_info)

application.add_url_rule('/create_update_server', 'create_update_server', create_update_server, methods=['GET', 'POST'])
application.add_url_rule('/create_update_server/<server_id>', 'create_update_server', create_update_server, methods=['GET', 'POST'])
application.add_url_rule('/delete_server/<server_id>', 'delete_server', delete_server)
application.add_url_rule('/server_info', 'server_info', server_info)

application.add_url_rule('/auth/login', 'login', auth.login, methods=['GET', 'POST'])
application.add_url_rule('/auth/logout', 'logout', auth.logout, methods=['GET', 'POST'])
application.add_url_rule('/auth/edit_user/<id>', 'edit_user', auth.edit_user, methods=['GET', 'POST'])