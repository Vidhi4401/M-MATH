from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Class(Base):

    __tablename__ = "classes"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    subjects = relationship("Subject", back_populates="class_obj")


class Subject(Base):

    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    class_id = Column(Integer, ForeignKey("classes.id"))

    class_obj = relationship("Class", back_populates="subjects")

    chapters = relationship("Chapter", back_populates="subject")


class Chapter(Base):

    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    subject_id = Column(Integer, ForeignKey("subjects.id"))

    subject = relationship("Subject", back_populates="chapters")

    notes = relationship("Note", back_populates="chapter")


class Note(Base):

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)

    title = Column(String)

    filename = Column(String)

    chapter_id = Column(Integer, ForeignKey("chapters.id"))

    chapter = relationship("Chapter", back_populates="notes")
