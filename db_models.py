from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql
from hashlib import md5
import time
from datetime import datetime

base = declarative_base()


class User(base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    name = Column(String(40), index=True, unique=True)
    email = Column(String(80), index=True, unique=True)
    passwd = Column(String(128))
    key = Column(String(128))
    avatar = Column(String)

    messages = relationship('Message', backref='author', lazy='dynamic')
    files = relationship('File', back_populates='owner', lazy='dynamic')

    def set_passwd(self, passwd):
        self.passwd = md5(str(passwd).encode()).hexdigest()

    def check_passwd(self, passwd):
        return self.passwd == md5(str(passwd).encode()).hexdigest()

    def set_key(self):
        pre_key = self.passwd+str(time.time())
        self.key = md5(pre_key.encode()).hexdigest()

    def __repr__(self):
        return '<User {}>'.format(self.name)


class Message(base):
    __tablename__ = 'Messages'

    id = Column(Integer, primary_key=True)
    text = Column(String(300))
    user_id = Column(Integer, ForeignKey('Users.id'))
    timestamp = Column(DateTime, index=True, default=datetime.utcnow())
    attachments = Column(postgresql.ARRAY(Integer))

    user = relationship('User', back_populates='messages')

    def __repr__(self):
        return '<Message: {} attachments: {}>'.format(self.text, len(self.attachments))


class File(base):
    __tablename__ = 'Files'

    id = Column(Integer, primary_key=True)
    type = Column(String)
    name = Column(String)
    link = Column(String)
    upload_time = Column(DateTime, index=True, default=datetime.utcnow())
    owner_id = Column(Integer, ForeignKey('Users.id'))

    owner = relationship('User', back_populates='files')
