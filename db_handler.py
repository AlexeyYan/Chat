from db_models import User, Message, File
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import cloudinary
from cloudinary import uploader, api
import os
from datetime import datetime
import threading

con = create_engine(os.environ.get('DATABASE_URL'))


Session = sessionmaker(con)
db = Session()

'''Fucntion newMessage:
   Args: message - information about message from client
         attch_list - attachments for the message
   
   Description: Write information about message to database
   
   Return: dict with information about message'''

def newMessage(message, attch_list):
    attach = []
    author = db.query(User).filter_by(key=message['key']).first()
    msg = Message(text=message['message'], author=author)
    msg.attachments = attch_list
    for ids in attch_list:
        attachment = db.query(File).filter_by(id=ids).first()
        attach.append({'id': attachment.id, 'type': attachment.type, 'name': attachment.name,
                       'link': attachment.link, 'owner_id': attachment.owner_id})
    db.add(msg)
    db.commit()

    return {'event': 'message', 'id': msg.id, 'text': msg.text, 'attachments': attach, 'author': {
        'id': msg.author.id, 'name': msg.author.name}, 'timestamp': msg.timestamp.isoformat()}

'''Function loginUser:
   Args: name - name of user
         passwd - password of user
   Description: This function find user in database by name and if user exist
                run password check.
   Return: user object'''
def loginUser(name, passwd):
    user = db.query(User).filter_by(name=name).first()
    if user != None and user.check_passwd(passwd):
        user.set_key()
        db.commit()
        return user


def registerUser(name, email, passwd):
    user = db.query(User).filter_by(name=name).first()
    if user == None:
        user = db.query(User).filter_by(email=email).first()
        if user == None:
            user = User(name=name, email=email)
            user.set_passwd(passwd)
            db.add(user)
            db.commit()
            return None
        return 'This email has already been registered!'
    return 'This name is already been changed!'


def getMessages():
    messages = db.query(Message).all()
    msg = []
    attach = []
    attach_ids = []
    if messages != None:
        for message in messages:
            if message.attachments != None:
                attach_ids = message.attachments
                for ids in attach_ids:
                    attachment = db.query(File).filter_by(id=ids).first()
                    attach.append({'id': attachment.id, 'type': attachment.type,
                                   'link': attachment.link, 'owner_id': attachment.owner_id})

            # print(attach)
            msg.append({'id': message.id, 'text': message.text, 'attachments': attach, 'author': {
                       'id': message.author.id, 'name': message.author.name}, 'timestamp': message.timestamp.isoformat()})
            attach = []
    return msg


'''cloudinary.config(
    cloud_name=os.environ.get('CNAME'),
    api_key=os.environ.get('CKEY'),
    api_secret=os.environ.get('CSECRET')
)'''

cloudinary.config(
    cloud_name='alexby',
    api_key='311589761642417',
    api_secret='iXZ0TzzPvOgG9DGKhro9NGulxQ8'
)

filetypes = {
    'image': [
        'image/png',
        'image/jpeg',
        'image/gif',
        'image/x-icon',
        'image/svg+xml',
        'image/tiff',
        'image/webp'
    ],
    'file': [
        'text/css',
        'application/msword',
        'text/html',
        'application/pdf',
        'application/vnd.ms-powerpoint'
        'application/x-rar-compressed',
        'application/rtf',
        'application/zip',
        'application/x-7z-compressed'
    ]
}


def newFile(file, key):
    if file['content_type'] in filetypes['image']:
        name = file['filename']
        author = db.query(User).filter_by(key=key).first()
        url = cloudinary.uploader.upload(file.body)['url']
        f = File(type=file['content_type'], name=name, link=url, owner=author)
        db.add(f)
        db.commit()
    return f.id
