from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from hashlib import md5
import time
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy.dialects import postgresql

#con=create_engine('postgres://zukhoddbycbjwa:c9f97c2b0181717d494fef4859b391cca10220aa3b5698a5a9b09faef2823895@ec2-54-246-101-215.eu-west-1.compute.amazonaws.com:5432/d91t85m8v78sgs')
con=create_engine('postgres://postgres:0x112524x0Yan@localhost:8080/postgres')
base=declarative_base()

'''class User(base):
    __tablename__='Users'

    id=Column(Integer, primary_key=True)
    name=Column(String(40), index=True, unique=True)
    email=Column(String(80), index=True, unique=True)
    passwd=Column(String(128))
    key=Column(String(128))
    avatar=Column(String)

    messages=relationship('Message', backref='author', lazy='dynamic')
    files=relationship('File', back_populates='owner', lazy='dynamic')

    def set_passwd(self, passwd):
        self.passwd=md5(str(passwd).encode()).hexdigest()

    def check_passwd(self, passwd):
        return self.passwd==md5(str(passwd).encode()).hexdigest()
    
    def set_key(self):
        pre_key=self.passwd+str(time.time())
        self.key=md5(pre_key.encode()).hexdigest()

    def __repr__(self):
        return '<User {}>'.format(self.name)

class Message(base):
    __tablename__='Messages'

    id=Column(Integer, primary_key=True)
    text=Column(String(300))
    user_id=Column(Integer, ForeignKey('Users.id'))
    timestamp=Column(DateTime, index=True, default=datetime.utcnow())
    attachments=Column(Integer, ForeignKey('Files.id'))
    
    attachments=relationship('File', back_populates='message')
    user=relationship('User', back_populates='messages')

    def  __repr__(self):
       return '<Message: {}>'.format(self.text)

class File(base):
    __tablename__='Files'

    id=Column(Integer, primary_key=True)
    type=Column(String)
    link=Column(String)
    upload_time=Column(DateTime, index=True, default=datetime.utcnow())
    owner_id=Column(Integer, ForeignKey('Users.id'))
    message_id=Column(Integer, ForeignKey('Messages.id'))
    
    message=relationship('Message', back_populates='attachments')
    owner=relationship('User', back_populates='files')'''
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql
from hashlib import md5
import time
from datetime import datetime

base=declarative_base()

class User(base):
    __tablename__='Users'

    id=Column(Integer, primary_key=True)
    name=Column(String(40), index=True, unique=True)
    email=Column(String(80), index=True, unique=True)
    passwd=Column(String(128))
    key=Column(String(128))
    avatar=Column(String)

    messages=relationship('Message', backref='author', lazy='dynamic')
    files=relationship('File', back_populates='owner', lazy='dynamic')

    def set_passwd(self, passwd):
        self.passwd=md5(str(passwd).encode()).hexdigest()

    def check_passwd(self, passwd):
        return self.passwd==md5(str(passwd).encode()).hexdigest()
    
    def set_key(self):
        pre_key=self.passwd+str(time.time())
        self.key=md5(pre_key.encode()).hexdigest()

    def __repr__(self):
        return '<User {}>'.format(self.name)

class Message(base):
    __tablename__='Messages'

    id=Column(Integer, primary_key=True)
    text=Column(String(300))
    user_id=Column(Integer, ForeignKey('Users.id'))
    timestamp=Column(DateTime, index=True, default=datetime.utcnow())
    attachments=Column(postgresql.ARRAY(Integer))
    
    user=relationship('User', back_populates='messages')

    def  __repr__(self):
       return '<Message: {} attachments: {}>'.format(self.text, len(self.attachments))

class File(base):
    __tablename__='Files'

    id=Column(Integer, primary_key=True)
    type=Column(String)
    link=Column(String)
    upload_time=Column(DateTime, index=True, default=datetime.utcnow())
    owner_id=Column(Integer, ForeignKey('Users.id'))
    
    owner=relationship('User', back_populates='files')

Session=sessionmaker(con)
db=Session()
base.metadata.create_all(con)

#name=input("Введите ник: ")
#passw=input("Введите пароль: ")
u=User(name="AlexYan", email="yanovichaleksey@gamil.com")
u.set_passwd("0x112524x0Yan")
#u= db.query(User).filter_by(name='root').first()
db.add(u)
#user=db.query(User).filter_by(name="AlexYan").first()
#msg=Message(text="Eeee boi", author=user
#messages=db.query(Message).all()
#msg=db.query(Message).filter_by(id=13).first()
#db.delete(msg)
#db.commit()
#for message in messages:
 #   print("id: "+str(message.id))
  #  print("text: "+message.text)
   # print("author_name: "+str(message.author.id))
#print(msg.author)
db.commit()
#print(u.id)
#print(u.name)
#print(u.passwd)
#print(u.key)
print('OK')

