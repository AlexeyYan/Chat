from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import os

con=create_engine(os.environ.get["DATABASE_URL"])
base=declarative_base()
from db_models import *
