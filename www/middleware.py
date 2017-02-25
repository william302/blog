import hmac

from flask import request

SECRET = 'imsosecret'
def hash_str(s):
    return hmac.new(SECRET.encode('utf-8'), s.encode('utf-8')).hexdigest()


def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))


def check_secure_val(h):
    if h:
        val = h.split('|')[0]
        if h == make_secure_val(val):
            return val


class SimpleMiddleWare(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        val_email = request.cookies.get('email')
        email = check_secure_val(val_email)
        if email:
            return email
        else:
            return self.app(environ, start_response)