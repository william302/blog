import hashlib
import hmac
import random
import re
import string

from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask import json
from flask import make_response

from sqlalchemy.orm import sessionmaker

from database_setup import User, Post, Comment, Base, engine
from apis import APIError, APIValueError, APIPermissionError, APIResourceNotFoundError, Page

app = Flask(__name__)

Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
session = Session()


#Page stuff
def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


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
    page = request.args.get('page')
    if not page:
        page = '1'
    page_index = get_page_index(page)
    try:
        num = session.query(Post).count()
    except:
        session.rollback()
        num = 1
    p = Page(num, page_index)
    blogs = []
    if num != 0:
        blogs = session.query(Post).order_by(Post.created).offset(p.offset).limit(p.limit)
        # session.close()
    if email:
        user = session.query(User).filter_by(email=email).first()
        # session.close()
        return render_template('blogs.html', user=user, blogs=blogs, page=p.serialize, page_index=page_index)
    else:
        return render_template('blogs.html', blogs=blogs, page=p.serialize, page_index=page_index)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
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
            email_hash = hashlib.md5(email.encode('utf-8')).hexdigest()
            app.logger.error(email_hash)
            user = User(name=name.strip(), email=email, passwd=pw_hash,
                        image='http://www.gravatar.com/avatar/%s?d=monsterid&s=120' % email_hash)
            session.add(user)
            try:
                session.commit()
            except:
                session.rollback()
            # session.close()
            r = make_response(jsonify(email))
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
        try:
            u = session.query(User).filter_by(email=email).first()
        except:
            session.rollback()
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


@app.route('/signout', methods=['GET', 'POST'])
def sign_out():
    if request.method == 'GET':
        r = make_response(redirect('/'))
        r.set_cookie('email', '', expires=0)
        return r


@app.route('/api/blogs', methods=['GET', 'POST'])
def api_blogs():
    if request.method == 'GET':
        page = request.args.get('page')
        if not page:
            page = '1'
        page_index = get_page_index(page)
        try:
            num = session.query(Post).count()
        except:
            session.rollback()
            num = 1
        p = Page(num, page_index)
        if num == 0:
            return jsonify(page=p.serialize, blogs=[])
        try:
            blogs = session.query(Post).order_by(Post.created).offset(p.offset).limit(p.limit)
        except: session.rollback()
        # session.close()
        return jsonify(page=p.serialize, blogs=[i.serialize for i in blogs])


@app.route('/api/users', methods=['GET', 'POST'])
def api_users(page='1'):
    if request.method == 'GET':
        page_index = get_page_index(page)
        try:
            num = session.query(User).count()
        except:
            session.rollback()
            num = 1
        p = Page(num, page_index)
        if num == 0:
            return jsonify(page=p.serialize, users=[])
        users = session.query(User).order_by(User.created).offset(p.offset).limit(p.limit)
        # session.close()
        return jsonify(page=p.serialize, users=[i.serialize for i in users])


@app.route('/api/comments', methods=['GET', 'POST'])
def api_comments(page='1'):
    if request.method == 'GET':
        page_index = get_page_index(page)
        try:
            num = session.query(Comment).count()
        except:
            session.rollback()
            num = 1
        # app.logger.error(num)
        p = Page(num, page_index)
        if num == 0:
            return jsonify(page=p.serialize, comments=[])
        comments = session.query(Comment).order_by(Comment.created).offset(p.offset).limit(p.limit)
        # session.close()
        return jsonify(page=p.serialize, comments=[i.serialize for i in comments])


@app.route('/api/blogs/<int:blog_id>', methods=['GET', 'POST'])
def api_blog_edit(blog_id):
    blog = session.query(Post).filter_by(id=blog_id).first()
    # session.close()
    if request.method == 'GET':
        return jsonify(blog.serialize)
    if request.method == 'POST':
        data = request.get_json()
        subject = data['subject']
        summary = data['summary']
        content = data['content']
        if not subject or not subject.strip():
            raise APIValueError('subject', 'subject cannot be empty.')
        if not summary or not summary.strip():
            raise APIValueError('summary', 'summary cannot be empty.')
        if not content or not content.strip():
            raise APIValueError('content', 'content cannot be empty.')
        blog.subject = subject.strip()
        blog.summary = summary.strip()
        blog.content = content.strip()
        session.add(blog)
        try:
            session.commit()
        except:
            session.rollback()
        blog = session.query(Post).filter_by(id=blog_id).first()
        # session.close()
        return jsonify(blog.serialize)


@app.route('/api/blogs/<int:blog_id>/delete', methods=['GET', 'POST'])
def api_blog_delete(blog_id):
    blog = session.query(Post).filter_by(id=blog_id).first()
    if request.method == 'POST':
        session.delete(blog)
        session.commit()
        session.close()
        return jsonify(id=blog_id)


@app.route('/api/comments/<int:comment_id>/delete', methods=['GET', 'POST'])
def api_comment_delete(comment_id):
    comment = session.query(Comment).filter_by(id=comment_id).first()
    if request.method == 'POST':
        session.delete(comment)
        session.commit()
        session.close()
        return jsonify(id=1)


@app.route('/blog/<int:blog_id>', methods=['GET', 'POST'])
def blog_handler(blog_id):
    val_email = request.cookies.get('email')
    email = check_secure_val(val_email)
    try:
        user = session.query(User).filter_by(email=email).first()
    except:
        session.rollback()
    if request.method == 'GET':
        blog = session.query(Post).filter_by(id=blog_id).first()
        comments = session.query(Comment).filter_by(post_id=blog_id).order_by(Comment.created).all()
        # session.close()
        return render_template('blog.html', blog=blog, user=user, comments=comments, blog_id=blog_id)


@app.route('/blogs/<int:blog_id>/comments', methods=['GET', 'POST'])
def comment_handler(blog_id):
    val_email = request.cookies.get('email')
    email = check_secure_val(val_email)
    try:
        user = session.query(User).filter_by(email=email).first()
    except:
        session.rollback()
    if request.method == 'POST':
        data = request.get_json()
        content = data['content']
        if not content or not content.strip():
            raise APIValueError('content', 'content cannot be empty.')
        comment = Comment(content=content.strip(), user_id=user.id, post_id=blog_id, user_name=user.name, user_image=user.image)
        session.add(comment)
        try:
            session.commit()
        except:
            session.rollback()
        # session.close()
        r = make_response(json.dumps(user.name, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-type'] = 'application/json; charset=utf-8'
        return r


@app.route('/manage/blogs', methods=['GET', 'POST'])
def manage_blog():
    val_email = request.cookies.get('email')
    email = check_secure_val(val_email)
    try:
        user = session.query(User).filter_by(email=email).first()
    except:
        session.rollback()
    if not user:
        return redirect('/authenticate')
    page = request.args.get('page')
    if not page:
        page = '1'
    if request.method == 'GET':
        return render_template('manage_blog.html', page_index=get_page_index(page), user=user)


@app.route('/manage/users', methods=['GET', 'POST'])
def manage_user():
    val_email = request.cookies.get('email')
    email = check_secure_val(val_email)
    try:
        user = session.query(User).filter_by(email=email).first()
    except:
        session.rollback()
    if not user:
        return redirect('/authenticate')
    page = request.args.get('page')
    if not page:
        page = '1'
    if request.method == 'GET':
        return render_template('manage_users.html', page_index=get_page_index(page), user=user)


@app.route('/manage/comments', methods=['GET', 'POST'])
def manage_comment():
    val_email = request.cookies.get('email')
    email = check_secure_val(val_email)
    try:
        user = session.query(User).filter_by(email=email).first()
    except:
        session.rollback()
    if not user:
        return redirect('/authenticate')
    page = request.args.get('page')
    if not page:
        page = '1'
    if request.method == 'GET':
        return render_template('manage_comments.html', page_index=get_page_index(page), user=user)


@app.route('/manage/blogs/create', methods=['GET', 'POST'])
def manage_new_blog():
    val_email = request.cookies.get('email')
    email = check_secure_val(val_email)
    try:
        user = session.query(User).filter_by(email=email).first()
    except:
        session.rollback()
    if not user:
        return redirect('/authenticate')
    if request.method == 'GET':
        return render_template('manage_blog_edit.html', id='', action='/manage/blogs/create', user=user)
    if request.method == 'POST':
        data = request.get_json()
        subject = data['subject']
        summary = data['summary']
        content = data['content']
        if not subject or not subject.strip():
            raise APIValueError('subject', 'subject cannot be empty.')
        if not summary or not summary.strip():
            raise APIValueError('summary', 'summary cannot be empty.')
        if not content or not content.strip():
            raise APIValueError('content', 'content cannot be empty.')
        post = Post(user_id=user.id, subject=subject.strip(), summary=summary.strip(), content=content.strip(),
                    user_name=user.name, user_image=user.image)
        session.add(post)
        try:
            session.commit()
        except:
            session.rollback()
        # session.close()
        r = make_response(json.dumps(user.name, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-type'] = 'application/json; charset=utf-8'
        return r


@app.route('/manage/blogs/edit', methods=['GET', 'POST'])
def manage_edit_blog():
    val_email = request.cookies.get('email')
    email = check_secure_val(val_email)
    try:
        user = session.query(User).filter_by(email=email).first()
    except:
        session.rollback()
    if not user:
        return redirect('/authenticate')
    if request.method == 'GET':
        blog_id = request.args.get('id')
        app.logger.error(blog_id)
        return render_template('manage_blog_edit.html', id=blog_id, action='/api/blogs/%s' % blog_id, user=user)


@app.route('/manage')
def manage():
    return redirect('/manage/blogs')


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
