from datetime import datetime
from sqlalchemy import Column, Integer, String, BLOB, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from config import *


class EmployeeLetters(db.Model):
    __tablename__ = 'emp_letters'

    LETTER_ID = db.Column(db.Integer, primary_key=True)
    EMP_ID = db.Column(db.Integer, db.ForeignKey('employee_details.EMP_ID'))
    TEMPLATE_ID = db.Column(db.String(225), db.ForeignKey('letter_templates.TEMPLATE_ID'))
    LETTER_TYPE = db.Column(db.String(50), nullable=False)
    LETTER = db.Column(db.LargeBinary(length=10 * (1024 * 1024)))
    CREATED_BY = db.Column(db.String(50), nullable=False)
    LAST_UPDATED_BY = db.Column(db.String(50), nullable=False)
    CREATED_AT = db.Column(db.DateTime, default=datetime.now, nullable=False)
    LAST_UPDATED_AT = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    employee = relationship('EmployeeDetails', back_populates='letters')

    def serialize(self):
        serialized_data = {
            "LETTER_ID": self.LETTER_ID,
            "EMP_ID": self.EMP_ID,
            "TEMPLATE_ID": self.TEMPLATE_ID,
            "LETTER_TYPE": self.LETTER_TYPE,
            "CREATED_BY": self.CREATED_BY,
            "LAST_UPDATED_BY": self.LAST_UPDATED_BY,
        }
        return serialized_data
