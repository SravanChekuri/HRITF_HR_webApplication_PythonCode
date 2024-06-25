
from config import *
from sqlalchemy import Column,String,Integer
from datetime import datetime
from flask import Flask, request, jsonify
from sqlalchemy.orm import relationship


from datetime import datetime, date
from datetime import datetime, date, timedelta
from sqlalchemy import UniqueConstraint
 
class EmploymentDetails(db.Model):
    __tablename__ = 'employment_details'
 
    ASSIGNMENT_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    EMP_ID = db.Column(db.Integer, db.ForeignKey('employee_details.EMP_ID'))
    EFFECTIVE_START_DATE = db.Column(db.Date, primary_key=True)
    EFFECTIVE_END_DATE = db.Column(db.Date, primary_key=True)
    ORGANIZATION_NAME = db.Column(db.String(225), nullable=False)
    POSITION = db.Column(db.String(225), nullable=False)
    DEPARTMENT = db.Column(db.String(225), nullable=False)
    ANNUAL_SALARY = db.Column(db.Float)
    PREVIOUS_ANNUAL_SALARY = db.Column(db.Float)
    DATE_OF_JOINING = db.Column(db.Date, nullable=False)
    STATUS = db.Column(db.String(225), nullable=False)
    WORKER_TYPE=db.Column(db.String(225),nullable=False)
    PREVIOUS_EXPERIENCE = db.Column(db.String(225))
    CURRENT_COMP_EXPERIENCE=db.Column(db.String(225))
    MOBILE_NO = db.Column(db.BigInteger, nullable=False)
    PROBATION_PERIOD = db.Column(db.String(225))
    NOTICE_PERIOD = db.Column(db.String(225))
    CONFIRMATION_DATE = db.Column(db.Date)
    CREATED_BY = db.Column(db.String(225), nullable=False)
    LAST_UPDATED_BY = db.Column(db.String(225), nullable=False)
    CREATED_AT = db.Column(db.DateTime, default=datetime.now, nullable=False)
    LAST_UPDATED_AT = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
   
    # Remove the UniqueConstraint for EMAIL
    __table_args__ = (
        # Define the new composite primary key constraint
        db.PrimaryKeyConstraint('ASSIGNMENT_ID', 'EFFECTIVE_START_DATE', 'EFFECTIVE_END_DATE'),
    )
 
    # Keep the serialize method as it is
    def serialize(self):
        serialized_data = {
            "ASSIGNMENT_ID": self.ASSIGNMENT_ID,
            "ORGANIZATION_NAME": self.ORGANIZATION_NAME,
            "POSITION": self.POSITION,
            "DEPARTMENT": self.DEPARTMENT,
            "ANNUAL_SALARY": self.ANNUAL_SALARY,
            "PREVIOUS_ANNUAL_SALARY": self.PREVIOUS_ANNUAL_SALARY,
            "DATE_OF_JOINING": self.DATE_OF_JOINING.strftime('%Y-%m-%d') if self.DATE_OF_JOINING else None,
            "STATUS": self.STATUS,
            "PREVIOUS_EXPERIENCE": self.PREVIOUS_EXPERIENCE,
            "CURRENT_COMP_EXPERIENCE": self.CURRENT_COMP_EXPERIENCE,
            "WORKER_TYPE": self.WORKER_TYPE,
            "MOBILE_NO": self.MOBILE_NO,
            "PROBATION_PERIOD": self.PROBATION_PERIOD,
            "NOTICE_PERIOD": self.NOTICE_PERIOD,
            "EMP_ID": self.EMP_ID,
            "CREATED_BY": self.CREATED_BY,
            "LAST_UPDATED_BY": self.LAST_UPDATED_BY
        }
        
        if self.EFFECTIVE_START_DATE:
            serialized_data["EFFECTIVE_START_DATE"] = self.EFFECTIVE_START_DATE.strftime('%Y-%m-%d')
        if self.EFFECTIVE_END_DATE:
            serialized_data["EFFECTIVE_END_DATE"] = self.EFFECTIVE_END_DATE.strftime('%Y-%m-%d')

        return serialized_data