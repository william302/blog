from flask import Flask, render_template, redirect, url_for, request, flash,jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import User, Post, Comment, Base

engine = create_engine("mysql+pymysql://root:admin@localhost:3306/blog", pool_recycle=3600, echo=True)
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
session = Session()


@app.route('/')
def index():
    users = session.query(User).all()
    return render_template('blog.html', users=users)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)