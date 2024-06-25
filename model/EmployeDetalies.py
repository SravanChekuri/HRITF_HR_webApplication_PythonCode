
from enum import unique
from config import *
from datetime import datetime
from flask import Flask, request, jsonify
from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, DateTime
from sqlalchemy.orm import relationship


class EmployeeDetails(db.Model):
    __tablename__ = 'employee_details'

    EMP_ID = db.Column(db.Integer, primary_key=True,autoincrement=True)
    EMP_NO = db.Column(db.String(225), nullable=False)
    EFFECTIVE_START_DATE = db.Column(db.Date, primary_key=True)
    EFFECTIVE_END_DATE = db.Column(db.Date, primary_key=True) 
    FIRST_NAME = db.Column(db.String(225), nullable=False)
    MIDDLE_NAME = db.Column(db.String(225))
    LAST_NAME = db.Column(db.String(225), nullable=False)
    EMAIL_ADDRESS = db.Column(db.String(225))
    WORKER_TYPE = db.Column(db.String(225))
    DATE_OF_BIRTH = db.Column(db.Date, nullable=False)
    WORK_LOCATION= db.Column(db.String(225), nullable =False)
    USER_ID = db.Column(db.Integer, db.ForeignKey('userdetails.USER_ID'))     
    CREATED_BY = db.Column(db.String(225), nullable=False)
    LAST_UPDATED_BY = db.Column(db.String(225), nullable=False)
    CREATED_AT = db.Column(db.DateTime, default=datetime.now, nullable=False)
    LAST_UPDATED_AT = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    letters = relationship('EmployeeLetters', back_populates='employee')

    def serialize(self):
        serialized_data = {
            "EMP_ID": self.EMP_ID,
            "EMP_NO": self.EMP_NO,
            "EFFECTIVE_START_DATE": self.EFFECTIVE_START_DATE.strftime('%Y-%m-%d'),
            "EFFECTIVE_END_DATE": self.EFFECTIVE_END_DATE.strftime('%Y-%m-%d'),
            "FIRST_NAME": self.FIRST_NAME,
            "LAST_NAME": self.LAST_NAME,
            "EMAIL_ADDRESS": self.EMAIL_ADDRESS,
            "WORKER_TYPE":self.WORKER_TYPE,
            "DATE_OF_BIRTH": self.DATE_OF_BIRTH.strftime('%Y-%m-%d'),
            "USER_ID": self.USER_ID,
            "WORK_LOCATION":self.WORK_LOCATION,
            "CREATED_BY": self.CREATED_BY,
            "LAST_UPDATED_BY": self.LAST_UPDATED_BY
        }
        
        if hasattr(self, 'MIDDLE_NAME') and self.MIDDLE_NAME:
            serialized_data['MIDDLE_NAME'] = self.MIDDLE_NAME
        
        return serialized_data
#=============================================================================================
# def getemployees():
#     data = EmployeeDetails.query.all()
#     print(data)
#     returnData= []
#     for i in data:
#         returnData.append(i.serialize())
#     print('returnData',returnData)
#     return returnData

def getemployeeId(EMP_ID):
    try:
        data = EmployeeDetails.query.get(EMP_ID)
        if not data:
                return jsonify({'message':'employees not found'}),404
        return jsonify({'message':f'employee {EMP_ID}','data':data.serialize()}),200
    except Exception as err:
        return jsonify({'err':str(err)}),500
    
    

# def deleteemployee(EMP_ID):
#     try:
#         employees=Employee_Details.query.get(EMP_ID)
#         print("gghah",employees)
#         if not employees:
#             return jsonify({'message':'employees not found'}),404
#         db.session.delete(employees)
#         db.session.commit()
#         return jsonify({'message':f'employee {EMP_ID} deleted succesfully','data':employees.serialize()}),200
#     except Exception as err:
#         return jsonify({'err':str(err)}),500
    

# def updateemployees(EMP_ID):
#     try:
#         data=request.json
#         employees=EmployeeDetails.query.get(EMP_ID)
#         for field in data.keys():
#             new_value=data.get(field)
#             if getattr(employees,field)!=new_value:
#                 setattr(employees,field,new_value)
#         db.session.commit()
#         return jsonify({'message':employees.serialize()})
#     except Exception as e:
        # return jsonify({'e':str(e)}),500





































