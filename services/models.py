from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class URL(db.Model):
    __tablename__ = 'drive_uploaded_files'

    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(255), nullable=False)
    tiny_url = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<URL {self.tiny_url}>'


from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UploadedFile(Base):
    __tablename__ = 'drive_uploaded_files'

    id = Column(Integer, primary_key=True, autoincrement=True)
    super_id = Column(Integer, nullable=False)
    file_id = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    original_url = Column(Text, nullable=False)
    tiny_url = Column(Text)
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')
    description = db.Column(db.String(255))
