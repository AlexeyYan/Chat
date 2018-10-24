from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

con=create_engine(os.environ.get["DATABASE_URL"])
from db_models import User, Message

Session=sessionmaker(con)
db=Session()

def newMessage(message, author):
    msg=Message(text=message, author=author)
    db.add(msg)
    db.commit()
    return msg

def registerUser(name, passwd):
    user=db.query(User).filter_by(name=name)
    if user!=None and user.check_passwd(passwd):
        user.set_key()
        db.commit()
        return user

