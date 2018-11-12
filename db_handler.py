from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

con=create_engine(os.environ.get('DATABASE_URL'))
from db_models import User, Message

Session=sessionmaker(con)
db=Session()

def newMessage(message, author_key):
    author=db.query(User).filter_by(key=author_key).first()
    msg=Message(text=message, author=author)
    db.add(msg)
    db.commit()
    return msg

def loginUser(name, passwd):
    user=db.query(User).filter_by(name=name).first()
    if user!=None and user.check_passwd(passwd):
        user.set_key()
        db.commit()
        return user

def registerUser(name, email, passwd):
        user=db.query(User).filter_by(name=name).first()
        if user==None:
                user=db.query(User).filter_by(email=email).first()
                if user==None:
                        user=User(name=name, email=email)
                        user.set_passwd(passwd)
                        db.add(user)
                        db.commit()
                        return None
                return 'This email has already been registered!'
        return 'This name is already been changed!'
                

def getMessages():
        messages=db.query(Message).all()
        msg=[]
        if messages==None: return msg
        for message in messages:
                msg.append({'id':message.id, 'text':message.text, 'author':{'id': message.author.id, 'name':message.author.name}, 'timestamp':message.timestamp.isoformat()})
        return msg
