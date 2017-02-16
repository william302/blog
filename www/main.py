import hashlib
import hmac
import random
import re
import string

import time
from aiohttp import web
from flask import Flask, render_template, redirect, url_for, request, flash,jsonify
from flask import json
from flask import logging
from flask import make_response

app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import User, Post, Comment, Base
from apis import APIError, APIValueError, APIPermissionError, APIResourceNotFoundError

engine = create_engine("mysql+pymysql://root:admin@localhost:3306/blog", pool_recycle=3600, echo=True)
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
session = Session()


def user2cookie(user, max_age):
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [str(user.id), expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)

#Password portion
def make_salt():
    return ''.join(random.choice(string.ascii_letters) for x in range(5))


def make_pw_hash(email, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256((email + pw + salt).encode('utf-8')).hexdigest()
    return '%s,%s' % (h, salt)


def valid_pw(email, pw, h):
    salt = h.split(',')[1]
    hash_val = make_pw_hash(email, pw, salt)
    return hash_val == h


#Cookie portion
SECRET = 'imsosecret'
COOKIE_NAME = 'session'
_COOKIE_KEY = 'imsosecret'

def hash_str(s):
    return hmac.new(SECRET.encode('utf-8'), s.encode('utf-8')).hexdigest()


def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))


def check_secure_val(h):
    if h:
        val = h.split('|')[0]
        if h == make_secure_val(val):
            return val

#RE portion
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")


def valid_username(username):
    return USER_RE.match(username)


def valid_password(password):
    return PASSWORD_RE.match(password)


def valid_email(email):
    return EMAIL_RE.match(email) or not email

# Handler portion
@app.route('/')
def index():
    val_email = request.cookies.get('email')
    email = check_secure_val(val_email)
    if email:
        user = session.query(User).filter_by(email=email).first()
        return render_template('blog.html', user=user)
    else:
        return render_template('blog.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        app.logger.error('post')
        data = request.get_json()
        name = data['name']
        email = data['email']
        passwd = data['passwd']
        if not name or not name.strip():
            raise APIValueError('name')
        if not email or not EMAIL_RE.match(email):
            raise APIValueError('email')
        if not passwd or not PASSWORD_RE.match(passwd):
            raise APIValueError('passwd')
        users = session.query(User).filter_by(email=email).first()
        if users:
            raise APIError('register:failed', email, 'Email is already in use.')
        else:
            pw_hash = make_pw_hash(email, passwd)
            user = User(name=name.strip(), email=email, passwd=pw_hash,
                        image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(
                            email.encode('utf-8')).hexdigest())
            session.add(user)
            session.commit()
            r = make_response(json.dumps(user.name, ensure_ascii=False).encode('utf-8'))
            r.headers['Content-type'] = 'application/json; charset=utf-8'
            r.set_cookie('email', make_secure_val(email))
            return r


@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    if request.method == 'GET':
        return render_template('signin.html')
    if request.method == 'POST':
        data = request.get_json()
        email = data['email']
        passwd = data['passwd']
        u = session.query(User).filter_by(email=email).first()
        if u:
            pw_hash = u.passwd
            if valid_pw(email, passwd, pw_hash):
                r = make_response(json.dumps(u.name, ensure_ascii=False).encode('utf-8'))
                r.headers['Content-type'] = 'application/json; charset=utf-8'
                r.set_cookie('email', make_secure_val(email))
                return r
            else:
                raise APIValueError('passwd', 'Invalid password.')
        else:
            raise APIValueError('email', 'Email not exist.')
            return 'ok'








if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)