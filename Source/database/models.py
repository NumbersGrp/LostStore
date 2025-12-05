from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from database.database import Base

import uuid


class User(Base):
    __tablename__ = 'users'

    uid = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
    tusername = Column(String, nullable=False, unique=True)
    tid = Column(BigInteger, nullable=False, unique=True)
    role = Column(String, nullable=False, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    end_message_sended = Column(Boolean, nullable=False, default=False)
    chat_id = Column(BigInteger, nullable=True)


class Books(Base):
    __tablename__ = 'books'

    uid = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    image_id = Column(String)
    author = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    file_ids = Column(ARRAY(String), nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Orders(Base):
    __tablename__ = 'orders'

    uid = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_tid = Column(BigInteger, nullable=False)
    book_uid = Column(String, nullable=False)
    screenshot = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Questions(Base):
    __tablename__ = 'questions'

    uid = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
    text = Column(String, nullable=False)
    user_uid = Column(String, nullable=False)
    tusername = Column(String, nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Setting(Base):
    __tablename__ = 'settings'

    key = Column(String, primary_key=True, nullable=False)
    value = Column(String, nullable=False)


# class LessonContent(Base):
#     __tablename__ = 'lesson_contents'

#     uid = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
#     lesson_uid = Column(String, nullable=False)
#     message_id = Column(BigInteger, nullable=True)
#     position = Column(Integer, nullable=False, default=0)
#     # New fields to support multiple content types
#     content_type = Column(String, nullable=False, default='message')  # e.g. 'text','photo','document','audio','video','url','message'
#     file_id = Column(String, nullable=True)  # Telegram file_id (if stored)
#     file_path = Column(String, nullable=True)  # Local path (optional)
#     text = Column(String, nullable=True)  # For text content
#     url = Column(String, nullable=True)  # For URL content
#     metadata_json = Column(String, nullable=True)  # JSON string with extra metadata like duration, thumb, etc.
