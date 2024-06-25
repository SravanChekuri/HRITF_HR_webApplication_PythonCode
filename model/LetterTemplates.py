from sqlalchemy import Column, Integer, String, BLOB, TIMESTAMP
from config import *
from datetime import datetime


class LetterTemplates(db.Model):
    __tablename__ = 'letter_templates'

    TEMPLATE_ID = db.Column(db.String(225), primary_key=True)
    TEMPLATE_NAME = db.Column(db.String(225), nullable=False)
    TEMPLATE = db.Column(db.LargeBinary(length=10 * (1024 * 1024)))
    FILE_SIZE = db.Column(db.Integer)
    TEMPLATE_TYPE = db.Column(db.String(225), nullable=False)
    CREATED_BY = db.Column(db.String(225), nullable=False)
    LAST_UPDATED_BY = db.Column(db.String(225), nullable=False)
    CREATED_AT = db.Column(db.DateTime, default=datetime.now, nullable=False)
    LAST_UPDATED_AT = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    


    def serialize(self):
        serialized_data = {
            "TEMPLATE_ID": self.TEMPLATE_ID,
            "TEMPLATE_NAME": self.TEMPLATE_NAME,
            "TEMPLATE": self.TEMPLATE.decode('utf-8'),
            "FILE_SIZE":self.FILE_SIZE,
            "TEMPLATE_TYPE":self.TEMPLATE_TYPE,
            "CREATED_BY": self.CREATED_BY,
            "LAST_UPDATED_BY": self.LAST_UPDATED_BY
        }
        return serialized_data
