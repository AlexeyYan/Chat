from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from db_handler import base
from hashlib import md5
import time

class User(base):
    __tablename__='Users'

    id=Column(Integer, primary_key=True)
    name=Column(String(40), index=True, unique=True)
    passwd=Column(String(30))
    key=Column(String(128))

    def set_passwd(self, passwd):
        self.passwd=md5(str(passwd).encode()).hexdigest()

    def check_passwd(self, passwd):
        return self.passwd==md5(str(passwd).encode()).hexdigest()
    
    def set_key(self):
        pre_key=self.passwd+str(time.time())
        self.key=md5(pre_key.encode()).hexdigest()