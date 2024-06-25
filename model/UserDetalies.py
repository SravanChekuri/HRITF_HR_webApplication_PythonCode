
from config import *
from sqlalchemy import Column,String,Integer,Float
from datetime import datetime
from flask import Flask, request, jsonify




class UserDetails(db.Model):
    __tablename__ = 'userdetails'

    USER_ID = db.Column(db.Integer, primary_key=True)
    USER_NAME = db.Column(db.String(250), nullable=False)
    PASSWORD = db.Column(db.String(250), nullable=False)
    FIRST_NAME = db.Column(db.String(250), nullable=False)
    MIDDLE_NAME = db.Column(db.String(250))
    MOBILE_NO = db.Column(db.BigInteger, unique=True)
    LAST_NAME = db.Column(db.String(250), nullable=False)
    EMAIL = db.Column(db.String(250), unique=True)
    USER_TYPE = db.Column(db.String(250), nullable=False)
    CREATED_BY = db.Column(db.String(250), nullable=False)
    LAST_UPDATED_BY = db.Column(db.String(250), nullable=False)
    CREATION_AT = db.Column(db.DateTime, default=datetime.now, nullable=False)
    LAST_UPDATED_AT = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    

    def serialize(self):
        serialized_data = {
            "USER_ID": self.USER_ID,
            'USER_NAME': self.USER_NAME,
            'PASSWORD': self.PASSWORD,
            'FIRST_NAME': self.FIRST_NAME,
            'LAST_NAME': self.LAST_NAME,
            'EMAIL': self.EMAIL,
            'MOBILE_NO': self.MOBILE_NO,
            'USER_TYPE': self.USER_TYPE,
            'CREATED_BY': self.CREATED_BY,
            'LAST_UPDATED_BY': self.LAST_UPDATED_BY,
            'CREATED_AT': self.CREATION_AT.strftime('%Y-%m-%d %H:%M:%S'),  
            'LAST_UPDATED_AT': self.LAST_UPDATED_AT.strftime('%Y-%m-%d %H:%M:%S') 
        }
        
        if hasattr(self, 'MIDDLE_NAME'):
            serialized_data['MIDDLE_NAME'] = self.MIDDLE_NAME
        
        return serialized_data