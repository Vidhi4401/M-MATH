from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String)


class File(Base):

    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    class_name = Column(String)
    topic = Column(String)
    filename = Column(String)
    uploaded_by = Column(String)
