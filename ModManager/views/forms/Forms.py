from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.validators import URL, Required, NumberRange
from ModManager.models import Mod, Server
from ModManager.views.forms.Validators import DomainValid

__author__ = 'Chris'

ModForm = model_form(Mod, base_class=Form, field_args={
    'name': {
        'validators': [Required()]
    },
    'link': {
        'validators': [URL()]
    },
    'server': {

    }
})

ServerForm = model_form(Server, base_class=Form, field_args={
    'name': {
        'validators': [Required()]
    },
    'ip': {
        'validators': [Required(), DomainValid()]
    },
    'port': {
        'validators': [Required(), NumberRange(min=0, max=65535)]
    },
    'bukkit': {
        'validators': []
    },
    'forge': {
        'validators': []
    },
    'mods_url': {
        'validators': [URL()]
    }
})
