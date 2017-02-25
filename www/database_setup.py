
from sqlalchemy import create_engine, Column, Integer, String, MetaData, DateTime, Boolean,Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

engine = create_engine("mysql+pymysql://root:admin@localhost:3306/blog?charset=utf8", pool_recycle=3600, echo=True)
Base = declarative_base()


def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(180))
    admin = Column(Boolean, default=False)
    passwd = Column(String(80), nullable=False)
    image = Column(Text(8000))
    created = Column(DateTime, default=datetime.now())

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'admin': self.admin,
            'created': dump_datetime(self.created),
            'passwd': self.passwd,
            'image': self.image,
        }


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
    user_name = Column(String(80), nullable=False)
    user_image = Column(Text(8000), nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'summary': self.summary,
            'content': self.content,
            'created': dump_datetime(self.created),
            'last_modify': dump_datetime(self.last_modify),
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_image': self.user_image
        }


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
    user_name = Column(String(80), nullable=False)
    user_image = Column(Text(8000), nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'content': self.content,
            'created': dump_datetime(self.created),
            'last_modify': dump_datetime(self.last_modify),
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_image': self.user_image,
            'post_id': self.post_id
        }


Base.metadata.create_all(engine)


