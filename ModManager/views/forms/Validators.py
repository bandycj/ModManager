import re
from wtforms.validators import Regexp

__author__ = 'Chris'

class DomainValid(Regexp):
    """
    Simple regexp based url validation. Much like the email validator, you
    probably want to validate the url later by other means if the url must
    resolve.

    :param require_tld:
        If true, then the domain-name portion of the URL must contain a .tld
        suffix.  Set this to false if you want to allow domains like
        `localhost`.
    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, require_tld=True, message=None):
        tld_part = (require_tld and r'\.[a-z]{2,10}' or '')
        regex = r'^([^/:]+%s|([0-9]{1,3}\.){3}[0-9]{1,3})$' % tld_part
        super(DomainValid, self).__init__(regex, re.IGNORECASE, message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = field.gettext('Invalid URL.')

        super(DomainValid, self).__call__(form, field)