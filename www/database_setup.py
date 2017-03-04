import markdown2
from sqlalchemy import create_engine, Column, Integer, String,  DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

engine = create_engine("mysql+pymysql://root:admin@localhost:3306/blog?charset=utf8", pool_recycle=3600, pool_size=100, echo=True)
Base = declarative_base()


def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)


def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    email = Column(String(30))
    admin = Column(Boolean, default=False)
    passwd = Column(String(200), nullable=False)
    image = Column(String(200))
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
    subject = Column(String(100))
    summary = Column(String(300))
    content = Column(String(3000))
    created = Column(DateTime, default=datetime.now())
    last_modify = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    user_id = Column(String(30), nullable=False)
    user_name = Column(String(30), nullable=False)
    user_image = Column(String(200), nullable=False)

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

    @property
    def content_html(self):
        return markdown2.markdown(self.content)


class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    content = Column(String(3000))
    created = Column(DateTime, default=datetime.now())
    last_modify = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    post_id = Column(String(30), nullable=False)
    user_id = Column(String(30), nullable=False)
    user_name = Column(String(30), nullable=False)
    user_image = Column(String(200), nullable=False)

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

    @property
    def content_html(self):
        return text2html(self.content)



Base.metadata.create_all(engine)


