from config import *
from sqlalchemy import Column, LargeBinary,String,Integer
from datetime import datetime
from flask import Flask, make_response, render_template, request, jsonify, send_file
from sqlalchemy.orm import relationship

#===========================================================================================



class EmployeeAddressDetails(db.Model):
    __tablename__ = 'employee_address_details'
 
    ADDRESS_ID = db.Column(db.Integer, primary_key=True,autoincrement=True)
    EMP_ID = db.Column(db.Integer, db.ForeignKey('employee_details.EMP_ID'))
    DATE_FROM = db.Column(db.Date, primary_key=True)
    DATE_TO = db.Column(db.Date, primary_key=True)
    ADDRESS_TYPE = db.Column(db.String(225), nullable=False)
    ADDRESS = db.Column(db.String(225), nullable=False)
    CITY = db.Column(db.String(225), nullable=False)
    STATE = db.Column(db.String(225), nullable=False)
    COUNTRY = db.Column(db.String(225), nullable=False)
    PIN_CODE = db.Column(db.Integer, nullable=False)
    PHONE_1 = db.Column(db.String(225))
    PHONE_2 = db.Column(db.String(225))
    CREATED_BY = db.Column(db.String(225), nullable=False)
    LAST_UPDATED_BY = db.Column(db.String(225), nullable=False)
    CREATED_AT = db.Column(db.DateTime, default=datetime.now, nullable=False)
    LAST_UPDATED_AT = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
 
    def serialize(self):
        serialized_data = {
            "ADDRESS_ID": self.ADDRESS_ID,
            "EMP_ID": self.EMP_ID,
            "ADDRESS_TYPE": self.ADDRESS_TYPE,
            "ADDRESS": self.ADDRESS,
            "CITY": self.CITY,
            "STATE": self.STATE,
            "COUNTRY": self.COUNTRY,
            "PIN_CODE": self.PIN_CODE,
            "DATE_FROM": self.DATE_FROM.strftime('%Y-%m-%d'),
            "DATE_TO": self.DATE_TO.strftime('%Y-%m-%d'),
            "PHONE_1": self.PHONE_1,
            "PHONE_2": self.PHONE_2,
            "CREATED_BY": self.CREATED_BY,
            "LAST_UPDATED_BY": self.LAST_UPDATED_BY
        }
        return serialized_data
    



@app.route('/get_employee_address_details', methods=['POST'])
# def get_employee_address_details():
#     try:
#         data = request.json
#         if not data:
#             return jsonify({'error': 'No JSON data provided'}), 400
#         EMP_ID = data.get('EMP_ID')
#         ADDRESS_TYPE = data.get('ADDRESS_TYPE')
#         DATE_FROM = data.get('DATE_FROM')
#         DATE_TO = data.get('DATE_TO')
 
#         # Validate the input parameters
#         if not EMP_ID or not ADDRESS_TYPE or not DATE_FROM or not DATE_TO:
#             return jsonify({'error': 'Missing required fields in JSON data'}), 400
 
#         # Parse the dates from the input
#         start_date = datetime.strptime(DATE_FROM, '%Y-%m-%d').date()
#         end_date = datetime.strptime(DATE_TO, '%Y-%m-%d').date()
#         # Query the database for the address details
#         address_details = EmployeeAddressDetails.query.filter(
#             EmployeeAddressDetails.EMP_ID == EMP_ID,
#             EmployeeAddressDetails.ADDRESS_TYPE.in_(ADDRESS_TYPE),
#             EmployeeAddressDetails.DATE_FROM >= start_date,
#             EmployeeAddressDetails.DATE_TO <= end_date
#         ).order_by(EmployeeAddressDetails.DATE_FROM.asc()).first()
#         # If no records are found, return a 404 error
#         if not address_details:
#             return jsonify({'message': 'Data not found'}), 404
 
#         # Serialize the result and return it
#         return jsonify({'data': address_details.serialize()}), 200
#     except Exception as e:
#         # Handle any exceptions and return a 500 error
#         return jsonify({'error': str(e)}), 500
def get_employee_address_details():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
       
        EMP_ID = data.get('EMP_ID')
        ADDRESS_TYPE = data.get('ADDRESS_TYPE')
       
 
        # Validate the input parameters
        if not EMP_ID or not ADDRESS_TYPE :
            return jsonify({'error': 'Missing required fields in JSON data'}), 400
 
        # Parse the dates from the input
       
        # Query the database for the address details
        address_details = EmployeeAddressDetails.query.filter(
            EmployeeAddressDetails.EMP_ID == EMP_ID,
            EmployeeAddressDetails.ADDRESS_TYPE.in_(ADDRESS_TYPE)
          ).first()
       
        # If no records are found, return a 404 error
        if not address_details:
            return jsonify({'message': 'Data not found'}), 404
 
        # Serialize the result and return it
        return jsonify({'data': address_details.serialize()}), 200
    except Exception as e:
        # Handle any exceptions and return a 500 error
        return jsonify({'error': str(e)}), 500
 
 
 