from sqlalchemy import create_engine, Column, Integer, String, MetaData, DateTime, Boolean,Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

engine = create_engine("mysql+pymysql://root:admin@localhost:3306/blog", pool_recycle=3600, echo=True)
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(180))
    admin = Column(Boolean, default=False)
    passwd = Column(String(80), nullable=False)
    image = Column(Text(8000))
    created = Column(DateTime, default=datetime.now())


class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    subject = Column(String(180))
    summary = Column(String(800))
    content = Column(Text(8000))
    created = Column(DateTime, default=datetime.now())
    last_modify = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    user = relationship(User)
    user_id = Column(Integer, ForeignKey('user.id'))


class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    content = Column(Text(8000))
    created = Column(DateTime, default=datetime.now())
    last_modify = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    user = relationship(User)
    user_id = Column(Integer, ForeignKey('user.id'))
    post = relationship(Post)
    post_id = Column(Integer, ForeignKey('post.id'))


Base.metadata.create_all(engine)


