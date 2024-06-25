from datetime import date, timedelta
import io
import re
from sqlite3 import IntegrityError
from flask import Flask, make_response, render_template, request, jsonify, send_file
import mysql.connector
from sqlalchemy import Text
from config import db
from model.EmpAddrDetaliess import *
from model.EmployeDetalies import EmployeeDetails


# def add_employee_address():
#     try:
#         data = request.json
#         print('data-->', data)
#         emp_id = data.get('EMP_ID')
#         employee = EmployeeDetails.query.get(emp_id)
#         if not employee:
#             return jsonify({'error': 'Employee does not exist'}), 400
#         address_id = data.get('ADDRESS_ID')
#         address = EmployeeAddressDetails.query.filter_by(ADDRESS_ID=address_id).first()
#         if address:
#             return jsonify({'error': 'Address ID already exists'}), 400
#         address_data = EmployeeAddressDetails(
#             EMP_ID=emp_id,
#             ADDRESS_ID=address_id,
#             ADDRESS_TYPE=data['ADDRESS_TYPE'],
#             ADDRESS=data['ADDRESS'],
#             CITY=data['CITY'],
#             STATE=data['STATE'],
#             COUNTRY=data['COUNTRY'],
#             PIN_CODE=data['PIN_CODE'],
#             DATE_FROM=data['DATE_FROM'],
#             DATE_TO=data['DATE_TO'],
#             PHONE_1=data['PHONE_1'],
#             PHONE_2=data['PHONE_2'],
#             CREATED_BY="HR",
#             LAST_UPDATED_BY="HR"
#         )
#         db.session.add(address_data)
#         db.session.commit()
#         return jsonify({'message': 'Employee address data added successfully', 'data': address_data.serialize()}), 201
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
 
# def add_employee_address(id):
#     try:
#         data = request.json
#         print("data", data)
 
#         if 'ADDRESS_TYPE' not in data:
#             return jsonify({'error': 'ADDRESS_TYPE is required'}), 400
 
#         ADDRESS_TYPE = data['ADDRESS_TYPE']
#         today = date.today()
 
#         dbdata = EmployeeAddressDetails.query.filter(
#             (EmployeeAddressDetails.EMP_ID == id) &
#             (EmployeeAddressDetails.DATE_FROM <= today) &
#             (today <= EmployeeAddressDetails.DATE_TO) &
#             (EmployeeAddressDetails.ADDRESS_TYPE == ADDRESS_TYPE)
#         ).first()
#         print("dbdata", dbdata)
 
#         emp_id = data.get('EMP_ID')
 
#         if not emp_id:
#             return jsonify({'error': 'EMP_ID is required'}), 400
 
#         # Fetch the latest effective start and end dates for the given EMP_ID
#         employee = EmployeeDetails.query.filter_by(EMP_ID=emp_id).order_by(EmployeeDetails.EFFECTIVE_START_DATE.desc()).first()
#         if not employee:
#             return jsonify({'error': 'Employee does not exist'}), 400
 
#         effective_start_date = employee.EFFECTIVE_START_DATE
#         effective_end_date = employee.EFFECTIVE_END_DATE
 
#         address_id = data.get('ADDRESS_ID')
#         if address_id:
#             address = EmployeeAddressDetails.query.filter_by(ADDRESS_ID=address_id).first()
#             if address:
#                 return jsonify({'error': 'Address ID already exists'}), 400
 
#         phone_1 = data.get('PHONE_1')
#         phone_2 = data.get('PHONE_2')
#         if phone_1 and EmployeeAddressDetails.query.filter_by(PHONE_1=phone_1).first():
#             return jsonify({'error': 'Phone number 1 already exists'}), 400
#         if phone_2 and EmployeeAddressDetails.query.filter_by(PHONE_2=phone_2).first():
#             return jsonify({'error': 'Phone number 2 already exists'}), 400
 
#         if phone_1 and not re.match(r'^\d{10}$', str(phone_1)):
#             return jsonify({'error': 'Phone number 1 should be exactly 10 digits long'}), 400
#         if phone_2 and not re.match(r'^\d{10}$', str(phone_2)):
#             return jsonify({'error': 'Phone number 2 should be exactly 10 digits long'}), 400
 
#         if ADDRESS_TYPE in ['WORK', 'HOME']:
#             if dbdata:
#                 Dated = data['DATE_FROM']
#                 Datedb = datetime.strptime(Dated, "%Y-%m-%d").date()
#                 dates = dbdata.DATE_FROM
#                 if dates == Datedb:
#                     for key in data:
#                         cap = key.upper()
#                         new_value = data.get(key)
#                         if getattr(dbdata, cap) != new_value:
#                             setattr(dbdata, cap, new_value)
#                     db.session.commit()
#                     print("details3",details)

#                     return jsonify({"message": "Updated existing record", "data": dbdata.serialize()}), 200
#                 else:
#                     Datedb = datetime.strptime(Dated, "%Y-%m-%d").date()
#                     PrevEED = Datedb - timedelta(days=1)
#                     dbdata.DATE_TO = PrevEED
#                     details = EmployeeAddressDetails(
#                         EMP_ID=data.get('EMP_ID'),
#                         ADDRESS_TYPE=data.get('ADDRESS_TYPE'),
#                         ADDRESS=data.get('ADDRESS'),
#                         CITY=data.get('CITY'),
#                         STATE=data.get('STATE'),
#                         COUNTRY=data.get('COUNTRY'),
#                         PIN_CODE=data.get('PIN_CODE'),
#                         DATE_FROM=data.get('DATE_FROM'),
#                         DATE_TO=data.get('DATE_TO'),
#                         PHONE_1=data.get('PHONE_1'),
#                         PHONE_2=data.get('PHONE_2'),
#                         CREATED_BY='HR',
#                         LAST_UPDATED_BY='HR'
#                     )
#                     db.session.add(details)
#                     db.session.commit()
#                     print("details1",details)

#                     return jsonify({"message": f"{data.get('EMP_ID')} new record added successfully", "data": details.serialize()}), 201
#             else:
#                 details = EmployeeAddressDetails(
#                     EMP_ID=data.get('EMP_ID'),
#                     ADDRESS_TYPE=data.get('ADDRESS_TYPE'),
#                     ADDRESS=data.get('ADDRESS'),
#                     CITY=data.get('CITY'),
#                     STATE=data.get('STATE'),
#                     COUNTRY=data.get('COUNTRY'),
#                     PIN_CODE=data.get('PIN_CODE'),
#                     DATE_FROM=data.get('DATE_FROM'),
#                     DATE_TO=data.get('DATE_TO'),
#                     PHONE_1=data.get('PHONE_1'),
#                     PHONE_2=data.get('PHONE_2'),
#                     CREATED_BY='HR',
#                     LAST_UPDATED_BY='HR'
#                 )
#                 db.session.add(details)
#                 db.session.commit()
#                 print("details",details)
#                 return jsonify({"message": f"{id} address details added successfully", "data": details.serialize()}), 201
#         else:
#             return jsonify({'error': 'Invalid ADDRESS_TYPE. Must be "WORK" or "HOME".'}), 400
 
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500
 
def add_employee_address(id):
    try:
        data = request.json
        print("data", data)
 
        if 'ADDRESS_TYPE' not in data:
            return jsonify({'error': 'ADDRESS_TYPE is required'}), 400
 
        ADDRESS_TYPE = data['ADDRESS_TYPE']
        today = data.get('DATE_FROM')
 
        emp_id = data.get('EMP_ID')
 
        if not emp_id:
            return jsonify({'error': 'EMP_ID is required'}), 400
 
        # Fetch the latest effective start and end dates for the given EMP_ID
        employee = EmployeeDetails.query.filter_by(EMP_ID=emp_id).order_by(EmployeeDetails.EFFECTIVE_START_DATE.desc()).first()
        if not employee:
            return jsonify({'error': 'Employee does not exist'}), 400
 
        DATE_TO = employee.EFFECTIVE_END_DATE
 
        address_id = data.get('ADDRESS_ID')
        if address_id:
            address = EmployeeAddressDetails.query.filter_by(ADDRESS_ID=address_id).first()
            if address:
                return jsonify({'error': 'Address ID already exists'}), 400
 
        phone_1, phone_2 = data.get('PHONE_1'), data.get('PHONE_2')
        if phone_1 or phone_2:
            phone_query = EmployeeAddressDetails.query.filter(
                (EmployeeAddressDetails.EMP_ID != emp_id) &
                ((EmployeeAddressDetails.PHONE_1 == phone_1) |
                (EmployeeAddressDetails.PHONE_2 == phone_2))
            ).first()
            if phone_query or (phone_1 and not re.match(r'^\d{10}$', str(phone_1))) or (phone_2 and not re.match(r'^\d{10}$', str(phone_2))):
                return jsonify({'error': 'Invalid phone number or phone number already exists'}), 400
 
        start_date_str = data.get('DATE_FROM')
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else date.today()
 
        employee_details = EmployeeDetails.query.filter_by(EMP_ID=emp_id).first()
        if not employee_details:
            return jsonify({'error': 'Employee ID not found'}), 404
 
        dbemployee = EmployeeAddressDetails.query.filter(
            (EmployeeAddressDetails.EMP_ID == id) &
            (EmployeeAddressDetails.DATE_FROM <= today) &
            (today <= EmployeeAddressDetails.DATE_TO)
        ).all()
 
        for i in dbemployee:
            if i.ADDRESS_TYPE == ADDRESS_TYPE:
                if i and start_date == i.DATE_FROM:
                    # Update existing record
                    i.ADDRESS_TYPE = data.get('ADDRESS_TYPE')
                    i.ADDRESS = data.get('ADDRESS')
                    i.CITY = data.get('CITY')
                    i.STATE = data.get('STATE')
                    i.COUNTRY = data.get('COUNTRY')
                    i.PIN_CODE = data.get('PIN_CODE')
                    i.DATE_FROM = data.get('DATE_FROM')
                    i.PHONE_1 = data.get('PHONE_1')
                    i.PHONE_2 = data.get('PHONE_2')
                    i.DATE_TO = data.get('DATE_TO', date(4712, 12, 31))  # Update DATE_TO
                    i.LAST_UPDATED_BY = "HR"
                    db.session.commit()
                    return jsonify({'message': 'Existing record updated', 'data': i.serialize()}), 200
                elif i and i.DATE_TO == start_date:
                    i.DATE_TO = start_date
                else:
                    i.DATE_TO = start_date - timedelta(days=1)  # Update DATE_TO
                    db.session.commit()
 
        future_records = EmployeeAddressDetails.query.filter(
            (EmployeeAddressDetails.EMP_ID == emp_id) &
            (EmployeeAddressDetails.DATE_FROM > start_date)
        ).all()
 
        for future_record in future_records:
            if future_record.DATE_FROM > start_date:
                future_record.DATE_FROM = start_date + timedelta(days=1)
                db.session.commit()
 
        new_data = EmployeeAddressDetails(
            EMP_ID=data.get('EMP_ID'),
            ADDRESS_TYPE=data.get('ADDRESS_TYPE'),
            ADDRESS=data.get('ADDRESS'),
            CITY=data.get('CITY'),
            STATE=data.get('STATE'),
            COUNTRY=data.get('COUNTRY'),
            PIN_CODE=data.get('PIN_CODE'),
            DATE_FROM=start_date,
            DATE_TO=data.get('DATE_TO', date(4712, 12, 31)),
            PHONE_1=data.get('PHONE_1'),
            PHONE_2=data.get('PHONE_2'),
            CREATED_BY="HR",
            LAST_UPDATED_BY="HR"
        )
 
        db.session.add(new_data)
        db.session.commit()
        return jsonify({'message': "New record added", 'data': new_data.serialize()}), 201
 
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500