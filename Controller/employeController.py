from ctypes import pythonapi
from io import BytesIO
from sqlite3 import IntegrityError
from flask import Flask, request, jsonify, send_file
import mysql.connector
from requests import get
from sqlalchemy import Text, and_, desc, func
import win32com
from model.EmployeDetalies import *
from flask import jsonify, request
import bcrypt
import re
import pandas as pd
from model.EmployeeLetters import EmployeeLetters
from model.EmploymentDetaliess import EmploymentDetails
from model.EmpAddrDetaliess import EmployeeAddressDetails

from model.LetterTemplates import LetterTemplates
from model.UserDetalies import UserDetails
from datetime import datetime, timedelta, date


def register_employee_data():
    try:
        print("fghjk")
        data = request.json
        print("data",data)
       
        if not data:
            return jsonify({'error': 'data is required'}), 400
 
        # Validate email address
        e_id = data.get('EMAIL_ADDRESS')
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not e_id or not re.match(email_pattern, e_id):
            return jsonify({'error': 'Invalid email'}), 400
 
        # Check for duplicate EMP_NO
        emp_no = data.get('EMP_NO')
        if not emp_no:
            return jsonify({'error': 'EMP_NO is required'}), 400
 
        existing_empnum = EmployeeDetails.query.filter_by(EMP_NO=emp_no).first()
        if existing_empnum:
            return jsonify({'message': f'Employee Number {emp_no} already exists'}), 400
 
        # Validate date of birth and age
        date_of_birth_str = data.get('DATE_OF_BIRTH')
        if not date_of_birth_str:
            return jsonify({'error': 'DATE_OF_BIRTH is required'}), 400
       
        date_of_birth = datetime.strptime(date_of_birth_str, "%Y-%m-%d").date()
        today = date.today()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        if age < 18:
            return jsonify({'message': 'Employee must be at least 18 years old'}), 400
 
        # Check for duplicate EMAIL_ADDRESS
        existing_emp = EmployeeDetails.query.filter_by(EMAIL_ADDRESS=e_id).first()
        if existing_emp:
            return jsonify({'message': f'Email {e_id} already exists'}), 400
 
        # Validate required fields
        required_fields = ['EMP_NO', 'FIRST_NAME', 'LAST_NAME', 'EFFECTIVE_START_DATE', 'WORKER_TYPE', 'WORK_LOCATION', 'EMAIL_ADDRESS']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'message': [f'{field} is required' for field in missing_fields]}), 400
 
        # Get user for USER_ID assignment
        userEmail = 'sowmya@gmail.com'
        user = UserDetails.query.filter_by(EMAIL=userEmail).first()
        if not user:
            return jsonify({'error': 'User not found'}), 400
 
        # Create new employee record
        new_employee = EmployeeDetails(
            EMP_NO=emp_no,
            FIRST_NAME=data['FIRST_NAME'],
            MIDDLE_NAME=data.get('MIDDLE_NAME'),
            LAST_NAME=data['LAST_NAME'],
            WORKER_TYPE=data['WORKER_TYPE'],
            DATE_OF_BIRTH=date_of_birth,
            EFFECTIVE_START_DATE=datetime.strptime(data['EFFECTIVE_START_DATE'], '%Y-%m-%d').date(),
            EFFECTIVE_END_DATE=datetime.strptime(data['EFFECTIVE_END_DATE'], '%Y-%m-%d').date() if 'EFFECTIVE_END_DATE' in data else date(4712, 12, 31),
            WORK_LOCATION=data['WORK_LOCATION'],
            USER_ID=user.USER_ID,
            EMAIL_ADDRESS=e_id,
            CREATED_BY='HRName',
            LAST_UPDATED_BY='HRName'
        )
 
        db.session.add(new_employee)
        db.session.commit()
 
        return jsonify({'details': new_employee.serialize()}), 201
 
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
def editemployee(Id):
    try:
        details = request.json
        emp_id = Id
        emp_no = details.get('EMP_NO')
        email = details.get('EMAIL_ADDRESS')
        effective_start_date = details.get('EFFECTIVE_START_DATE')
        effective_end_date = details.get('EFFECTIVE_END_DATE')
 
        existing_employee = EmployeeDetails.query.filter_by(EMP_ID=emp_id).first()
        if not existing_employee:
            return jsonify({'error': 'Employee with the provided ID does not exist'}), 404
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'error': 'Invalid email'}), 400
        if effective_start_date:
            effective_start_date = datetime.strptime(effective_start_date, '%Y-%m-%d').date()
        else:
            effective_start_date = date.today()
        if effective_end_date:
            effective_end_date = datetime.strptime(effective_end_date, '%Y-%m-%d').date()
        else:
            effective_end_date = date(4712, 12, 31)
        if not emp_no.startswith('C') and not emp_no.startswith('E'):
            return jsonify({'error': "Invalid EMP_NO. It should start with 'C' or 'E'"}), 400
        date_of_birth = datetime.strptime(details.get('DATE_OF_BIRTH'), "%Y-%m-%d").date()
        today = date.today()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        if age < 18:
            return jsonify({'message': 'Employee must be at least 18 years old'}), 400
 
        existing_emp_no = EmployeeDetails.query.filter(EmployeeDetails.EMP_NO == emp_no, EmployeeDetails.EMP_ID != emp_id).first()
        if existing_emp_no:
            return jsonify({'error': 'EMP_NO already exists'}), 400
 
        dbdata = EmployeeDetails.query.filter(
            (EmployeeDetails.EMP_ID == emp_id)
            & (EmployeeDetails.EFFECTIVE_START_DATE <= details.get('EFFECTIVE_START_DATE'))
            & (details.get('EFFECTIVE_START_DATE') <= EmployeeDetails.EFFECTIVE_END_DATE)
            ).order_by(EmployeeDetails.EFFECTIVE_START_DATE.asc()).first()
        print("dbdata",dbdata)
        if dbdata:
            if dbdata.WORKER_TYPE == 'Candidate' and details.get('WORKER_TYPE') == 'Employee':
                existing_email = EmployeeDetails.query.filter(
                    EmployeeDetails.EMAIL_ADDRESS == email,
                    EmployeeDetails.EMP_NO != emp_no
                ).first()
                if existing_email:
                    return jsonify({'error': 'Email address already exists for another employee'}), 400
               
                Datedb = str(details['EFFECTIVE_START_DATE'])
                print("Datedb",Datedb)
                Datedb = datetime.strptime(Datedb, "%Y-%m-%d")
                PrevEED = Datedb - timedelta(days=1)
                dbESD = datetime.strptime(str(dbdata.EFFECTIVE_START_DATE), "%Y-%m-%d")
                if dbESD == Datedb:
                        dbdata.EFFECTIVE_END_DATE = dbdata.EFFECTIVE_START_DATE
                elif dbESD < Datedb:
                    dbdata.EFFECTIVE_END_DATE = PrevEED
               
                new_employee = EmployeeDetails(
                            EMP_ID=emp_id,
                            EMP_NO=emp_no,
                            FIRST_NAME=details.get('FIRST_NAME'),
                            MIDDLE_NAME=details.get('MIDDLE_NAME'),
                            LAST_NAME=details.get('LAST_NAME'),
                            EMAIL_ADDRESS=email,
                            DATE_OF_BIRTH=date_of_birth,
                            WORKER_TYPE=details.get('WORKER_TYPE'),
                            WORK_LOCATION=details.get('WORK_LOCATION'),
                            USER_ID=details.get('USER_ID'),
                            EFFECTIVE_START_DATE=effective_start_date,
                            EFFECTIVE_END_DATE=date(4712, 12, 31),
                            CREATED_BY=details.get('CREATED_BY') or "HR",
                            LAST_UPDATED_BY="HR",
                            LAST_UPDATED_AT=datetime.now()
                        )
                db.session.add(new_employee)
                db.session.commit()
                return jsonify({"message": "Employee details added successfully"}),201
            if dbdata.WORKER_TYPE == 'Employee':
                print("WORKER_TYPE",dbdata)
                exact_samedate_employee = EmployeeDetails.query.filter(
                (EmployeeDetails.EMP_NO == emp_no)
                # (EmployeeDetails.EMP_ID == emp_id)
                & (EmployeeDetails.EFFECTIVE_START_DATE == details.get('EFFECTIVE_START_DATE'))
                &(details.get('EFFECTIVE_START_DATE') < EmployeeDetails.EFFECTIVE_END_DATE)
                ).first()
               
                # exact_employee = EmployeeDetails.query.all()
 
                print("inside 2nd if..",0,exact_samedate_employee)
                test = ['FIRST_NAME','MIDDLE_NAME','LAST_NAME','WORK_LOCATION','EMAIL_ADDRESS']
                if exact_samedate_employee:
                    fupdate = EmployeeDetails.query.filter(
                    (EmployeeDetails.EMP_ID == emp_id) &
                    (EmployeeDetails.EMP_NO == emp_no) &
                    (EmployeeDetails.EFFECTIVE_START_DATE > effective_start_date)
                    ).all()
                    # print("fupdate",dbdata,fupdate[0])
                    if fupdate:
                        today = date.today()
                        print("fupdate",fupdate,dbdata)
                        returndata = []
                        # test = ['FIRST_NAME','MIDDLE_NAME','LAST_NAME','DATE_OF_BIRTH','MOBILE_NO','JOB_LOCATION','EMAIL_ID']
                        test = ['FIRST_NAME','MIDDLE_NAME','LAST_NAME','WORK_LOCATION','EMAIL_ADDRESS']
                        for j in fupdate:
                            # storedata = {}
                            for i in test:
                                # m = test[i]
                                print(i)
                                dbdata_attr = getattr(dbdata, i, None)
                                # dbdata_attr = dbdata.i
                                print(dbdata_attr)
                                j_attr = getattr(j, i,None)
                                print(dbdata_attr,j_attr)
                                if dbdata_attr == j_attr:
                                    print("i",i)
                                    setattr(j, i, details.get(i))
 
                            returndata.append(j.serialize())
                        print("returndata",returndata)
                        db.session.commit()
                    for i in test:
                    # m = test[i]
                        print("test")
                        print(i)
                        dbdata_attr = getattr(exact_samedate_employee, i, None)
                        # dbdata_attr = dbdata.i
                        print(dbdata_attr)
                        j_attr = details.get(i)
                        print(dbdata_attr,j_attr)
                        if dbdata_attr != j_attr:
                            print("i",i)
                            setattr(exact_samedate_employee, i, details.get(i))
 
                    db.session.commit()
                    return jsonify({"message": "record updated successfully"}),200
 
                exact_employee = EmployeeDetails.query.filter(
                (EmployeeDetails.EMP_NO == emp_no)
                & (EmployeeDetails.EFFECTIVE_START_DATE <= details.get('EFFECTIVE_START_DATE'))
                &(details.get('EFFECTIVE_START_DATE') <= EmployeeDetails.EFFECTIVE_END_DATE)
                ).first()
                # for existing_record in existing_employees:
                Datedb = str(details['EFFECTIVE_START_DATE'])
                print("Datedb",Datedb)
                Datedb = datetime.strptime(Datedb, "%Y-%m-%d")
                PrevEED = Datedb - timedelta(days=1)
                dbESD = datetime.strptime(str(dbdata.EFFECTIVE_START_DATE), "%Y-%m-%d")
                if dbESD == Datedb:
                        dbdata.EFFECTIVE_END_DATE = dbdata.EFFECTIVE_START_DATE
                elif dbESD < Datedb:
                    dbdata.EFFECTIVE_END_DATE = PrevEED
           
                if exact_employee:
                    print("inside else1", details.get('WORKER_TYPE') == 'Employee')
 
                    fdata = EmployeeDetails.query.filter(
                                        (EmployeeDetails.EMP_ID == Id) &
                                            (EmployeeDetails.EMP_NO == details.get('EMP_NO'))&
                                            (EmployeeDetails.EFFECTIVE_START_DATE > details.get('EFFECTIVE_START_DATE'))
                                        ).order_by(EmployeeDetails.EFFECTIVE_START_DATE.asc()).first()
                    print(fdata,"lkjnhbgvfc")
                    if not fdata:
                        print("inside else")
                        eed = date(4712, 12, 31)
                    else:
                        print("fdata",fdata)
                        FESD = str(fdata.EFFECTIVE_START_DATE)
                        print("FESD",FESD)
                        fESD = datetime.strptime(FESD, "%Y-%m-%d")
                        print("fESD",fESD)
                        eed = fESD - timedelta(days=1)
                        print("eed",eed,details.get('EFFECTIVE_START_DATE'))
 
                        fupdate = EmployeeDetails.query.filter(
                            (EmployeeDetails.EMP_ID == emp_id) &
                            (EmployeeDetails.EMP_NO == emp_no) &
                            (EmployeeDetails.EFFECTIVE_START_DATE > effective_start_date)
                        ).all()
                        print("fupdate",dbdata,fupdate[0])
 
                        returndata = []
                        # test = ['FIRST_NAME','MIDDLE_NAME','LAST_NAME','DATE_OF_BIRTH','MOBILE_NO','JOB_LOCATION','EMAIL_ID']
                        test = ['FIRST_NAME','MIDDLE_NAME','LAST_NAME','WORK_LOCATION','EMAIL_ADDRESS']
                        for j in fupdate:
                            # storedata = {}
                            for i in test:
                                # m = test[i]
                                print(i)
                                dbdata_attr = getattr(dbdata, i, None)
                                # dbdata_attr = dbdata.i
                                print(dbdata_attr)
                                j_attr = getattr(j, i)
                                print(dbdata_attr,j_attr)
                                if dbdata_attr == j_attr:
                                    print("i",i)
                                    setattr(j, i, details.get(i))
 
                            returndata.append(j.serialize())
                            print("returndata",returndata)
                            db.session.commit()
                       
 
                   
                    new_employee = EmployeeDetails(
                        EMP_ID=emp_id,
                        EMP_NO=emp_no,
                        FIRST_NAME=details.get('FIRST_NAME'),
                        MIDDLE_NAME=details.get('MIDDLE_NAME'),
                        LAST_NAME=details.get('LAST_NAME'),
                        EMAIL_ADDRESS=email,
                        DATE_OF_BIRTH=date_of_birth,
                        WORKER_TYPE=details.get('WORKER_TYPE'),
                        WORK_LOCATION=details.get('WORK_LOCATION'),
                        USER_ID=details.get('USER_ID'),
                        EFFECTIVE_START_DATE=effective_start_date,
                        EFFECTIVE_END_DATE=eed,
                        CREATED_BY=details.get('CREATED_BY') or "HR",
                        LAST_UPDATED_BY="HR",
                        LAST_UPDATED_AT=datetime.now()
                    )
 
                    db.session.add(new_employee)
                    db.session.commit()
                    return jsonify({"message": "Employee details added successfully"}),201
 
        db.session.commit()
        return jsonify({"message": "Employee details updated successfully"}),200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
   

from flask import Flask, jsonify, request
import pandas as pd
from datetime import datetime
# from models import EmployeeDetails, UserDetails, db



# def getEmployeedetails(id,date):
#     try:
#         print("kjnhbgvf")
#         # data = request.form
#         ESD = date
#         print("ESD",ESD)
#         get = EmployeeDetails.query.filter(
#                                    (EmployeeDetails.EMP_ID == id) &
#                                     (EmployeeDetails.EFFECTIVE_START_DATE >= ESD)
#                                 ).order_by(EmployeeDetails.EFFECTIVE_START_DATE.asc()).first()
       
#         print("get", get)
#         if not get:
#             return jsonify({'message': 'data not found'}), 404
#         print("data.serialize()", get.serialize())
#         return jsonify({'data': get.serialize()}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
def getEmployeedetails(id,date,enddate):
    try:
        print("kjnhbgvf")
        # data = request.form
        ESD = date
        EED = enddate
        print("ESD",ESD)
        get = EmployeeDetails.query.filter(
                                   (EmployeeDetails.EMP_ID == id) |
                                    (EmployeeDetails.EFFECTIVE_START_DATE <= ESD)|
                                    (EmployeeDetails.EFFECTIVE_START_DATE <= EED)
                                ).order_by(EmployeeDetails.EFFECTIVE_START_DATE.desc()).first()
       
        print("get", get)
        if not get:
            return jsonify({'message': 'data not found'}), 404
        print("data.serialize()", get.serialize())
        return jsonify({'data': get.serialize()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 

# def SearchEmployeedetails(emp,date):
#     try:
#         print("emp",emp)
#         print("Date",date)
#         # data = request.json
#         ESD = date
#         emp_no = emp
#         # emp_no = request.args.get('emp_no')
#         # ESD = request.args.get('date')
#         # date1 = request.args.get('enddate')
#         print("ESD",ESD)
#         existing_employee = EmployeeDetails.query.filter_by(EMP_NO=emp_no).first()
#         if not existing_employee:
#             return jsonify({'error': 'Employee does not exist'}), 404

#         # EED = enddate if enddate else date(4712, 12, 31)
#         returndata = {}
#         if date != 'undefined':
#             get = EmployeeDetails.query.filter(
#                                     (EmployeeDetails.EMP_NO == emp_no) &
#                                         (EmployeeDetails.EFFECTIVE_START_DATE <= ESD)
#                                         # (EmployeeDetails.EFFECTIVE_START_DATE <= ESD)
#                                         # (EmployeeDetails.EFFECTIVE_END_DATE <= EED)
#                                     ).order_by(EmployeeDetails.EFFECTIVE_START_DATE.desc()).first()
        
#             print("get", get)
#             if not get:
#                 return jsonify({'message': 'data not found'}), 404
#             print("data1.serialize()", get.serialize())
#             returndata['EMPLOYEE_DETAILS'] =get.serialize()
#             get2 = EmploymentDetails.query.filter(
#                                     (EmploymentDetails.EMP_ID == get.EMP_ID  ) &
#                                         (EmploymentDetails.EFFECTIVE_START_DATE <= ESD)
#                                         # (EmploymentDetails.EFFECTIVE_START_DATE <= ESD)
#                                         # (EmploymentDetails.EFFECTIVE_END_DATE <= EED)
#                                     ).order_by(EmploymentDetails.EFFECTIVE_START_DATE.desc()).first()
#             print("get", get2)
        
#             returndata['Employement_Details'] =get2.serialize()
            
#         if date == 'undefined':
#             get = EmployeeDetails.query.filter(
#                                     (EmployeeDetails.EMP_NO == emp_no) 
#                                         # | (EmployeeDetails.EFFECTIVE_START_DATE <= ESD)
#                                         # (EmployeeDetails.EFFECTIVE_END_DATE <= EED)
#                                     ).order_by(EmployeeDetails.EFFECTIVE_START_DATE.desc()).first()
        
#             print("get", get)
#             if not get:
#                 return jsonify({'message': 'data not found'}), 404
#             print("data2.serialize()", get.serialize())
#             returndata['EMPLOYEE_DETAILS'] =get.serialize()
#             get2 = EmploymentDetails.query.filter(
#                                     (EmploymentDetails.EMP_ID == get.EMP_ID  )
#                                         # | (EmploymentDetails.EFFECTIVE_START_DATE <= ESD)
#                                         # (EmploymentDetails.EFFECTIVE_END_DATE <= EED)
#                                     ).order_by(EmploymentDetails.EFFECTIVE_START_DATE.desc()).first()
        
#             returndata['Employement_Details'] =get2.serialize()
            
        
 
        
#         return returndata, 200
#     except Exception as e:
# #         return jsonify({'error': str(e)}), 500 
def SearchEmployeedetails(emp, date):
    try:
        ESD = date if date != 'undefined' else None
        emp_no = emp
        print("ESD", ESD)
        existing_employee = EmployeeDetails.query.filter_by(EMP_NO=emp_no).first()
        if not existing_employee:
            return jsonify({'error': 'Employee does not exist'}), 404
 
        returndata = {}
        if ESD is not None:
            get = EmployeeDetails.query.filter(
                (EmployeeDetails.EMP_NO == emp_no) |
                (EmployeeDetails.EFFECTIVE_START_DATE <= ESD)
            ).order_by(EmployeeDetails.EFFECTIVE_START_DATE.desc()).first()
 
            print("get", get)
            if not get:
                return jsonify({'message': 'data not found'}), 404
            returndata['EMPLOYEE_DETAILS'] = get.serialize()
 
            get2 = EmploymentDetails.query.filter(
                (EmploymentDetails.EMP_ID == get.EMP_ID) |
                (EmploymentDetails.EFFECTIVE_START_DATE <= ESD)
            ).order_by(EmploymentDetails.EFFECTIVE_START_DATE.desc()).first()
 
            if get2:
                returndata['Employment_Details'] = get2.serialize()
 
            get3 = EmployeeAddressDetails.query.filter(
                (EmployeeAddressDetails.EMP_ID == get.EMP_ID) |
                (EmployeeAddressDetails.DATE_FROM <= ESD)
                # & (EmployeeAddressDetails.DATE_TO <= ESD)
            ).order_by(EmployeeAddressDetails.DATE_FROM.desc()).all()
            print("45y66",get3)
            m = []
            if get3:
                for i in get3:
                    m.append(i.serialize())
                returndata['EmployeeAddressDetails'] = m
                print("45y66",returndata['EmployeeAddressDetails'])
 
        else:
            get = EmployeeDetails.query.filter(
                EmployeeDetails.EMP_NO == emp_no
            ).order_by(EmployeeDetails.EFFECTIVE_START_DATE.desc()).first()
 
            print("get", get)
            if not get:
                return jsonify({'message': 'data not found'}), 404
            returndata['EMPLOYEE_DETAILS'] = get.serialize()
 
            get2 = EmploymentDetails.query.filter(
                EmploymentDetails.EMP_ID == get.EMP_ID
            ).order_by(EmploymentDetails.EFFECTIVE_START_DATE.desc()).first()
 
            if get2:
                returndata['Employment_Details'] = get2.serialize()
 
            get3 = EmployeeAddressDetails.query.filter(
                EmployeeAddressDetails.EMP_ID == get.EMP_ID
            ).order_by(EmployeeAddressDetails.DATE_FROM.desc()).first()
            print("45000006",get3)
 
 
            if get3:
                returndata['EmployeeAddressDetails'] = get3.serialize()
                print("4500007",returndata['EmployeeAddressDetails'])
 
 
        return jsonify(returndata), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
def get_latest_records(emp, date, enddate=None):
    try:
        emp_no = emp
        ESD = datetime.strptime(date, '%Y-%m-%d').date()
        EED = datetime.strptime(enddate, '%Y-%m-%d').date() if enddate else datetime(4712, 12, 31).date()
        
        # Fetching the latest Employee Details
        emp_latest_record = EmployeeDetails.query.filter(
            EmployeeDetails.EMP_NO == emp_no,
            EmployeeDetails.EFFECTIVE_START_DATE <= ESD,
            EmployeeDetails.EFFECTIVE_END_DATE <= EED
        ).order_by(EmployeeDetails.EFFECTIVE_START_DATE.desc()).first()
        print("1230",emp_latest_record)
        if not emp_latest_record:
            return jsonify({
                'employee_details': [],
                'employment_details': [],
                'home_address_details': [],
                'work_address_details': []
            }), 404
        
        # Fetching the latest Employment Details
        employment_latest_record = EmploymentDetails.query.filter(
            EmploymentDetails.EMP_ID == emp_latest_record.EMP_ID,
            EmploymentDetails.EFFECTIVE_START_DATE <= ESD,
            EmploymentDetails.EFFECTIVE_END_DATE <= "4712-12-31"
        ).order_by(EmploymentDetails.EFFECTIVE_START_DATE.desc()).first()
        
        print("1230",employment_latest_record)
        # Fetching the latest Home Address Details
        home_address_latest_record = EmployeeAddressDetails.query.filter(
            EmployeeAddressDetails.EMP_ID == emp_latest_record.EMP_ID,
            EmployeeAddressDetails.ADDRESS_TYPE == 'PERMANENT',
            EmployeeAddressDetails.DATE_FROM <= ESD,
            EmployeeAddressDetails.DATE_TO <= EED
        ).order_by(EmployeeAddressDetails.DATE_FROM.desc()).first()
        
        # Fetching the latest Work Address Details
        work_address_latest_record = EmployeeAddressDetails.query.filter(
            EmployeeAddressDetails.EMP_ID == emp_latest_record.EMP_ID,
            EmployeeAddressDetails.ADDRESS_TYPE == 'PRESENT',
            EmployeeAddressDetails.DATE_FROM <= ESD,
            EmployeeAddressDetails.DATE_TO <= EED
        ).order_by(EmployeeAddressDetails.DATE_FROM.desc()).first()
        
        # Creating the response data in list format
        combined_data = {
            'employee_details': [emp_latest_record.serialize()] if emp_latest_record else [],
            'employment_details': [employment_latest_record.serialize()] if employment_latest_record else [],
            'home_address_details': [home_address_latest_record.serialize()] if home_address_latest_record else [],
            'work_address_details': [work_address_latest_record.serialize()] if work_address_latest_record else []
        }
        
        return jsonify(combined_data), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500




def SearchEmployeedetailss(emp, date, enddate=None):
    try:
        ESD = date
        emp_no = emp
        
        EED = enddate if enddate else '4712-12-31'
        
        returndata = {}
        
        get = EmployeeDetails.query.filter(
            EmployeeDetails.EMP_NO == emp_no,
            EmployeeDetails.EFFECTIVE_START_DATE <= ESD,
            EmployeeDetails.EFFECTIVE_END_DATE <= EED
        ).order_by(EmployeeDetails.EFFECTIVE_START_DATE.desc()).first()
        
        if not get:
            return jsonify([]), 404
        
        returndata['EmployeeDetails'] = get.serialize()
        
        get2 = EmploymentDetails.query.filter(
            EmploymentDetails.EMP_ID == get.EMP_ID,
            EmploymentDetails.EFFECTIVE_START_DATE <= ESD,
            EmploymentDetails.EFFECTIVE_END_DATE <= EED
        ).order_by(EmploymentDetails.EFFECTIVE_START_DATE.desc()).first()
        
        
        if get2:
            returndata['EmploymentDetails'] = get2.serialize()
        
        get3 = EmployeeAddressDetails.query.filter(
            EmployeeAddressDetails.EMP_ID == get.EMP_ID,
            EmployeeAddressDetails.ADDRESS_TYPE == 'PRESENT',
            EmployeeAddressDetails.DATE_FROM <= ESD,
            EmployeeAddressDetails.DATE_TO <= EED
        ).order_by(EmployeeAddressDetails.DATE_FROM.desc()).first()
        
        if get3:
            returndata['HomeEmployeeAddressDetails'] = get3.serialize()
        
        get4 = EmployeeAddressDetails.query.filter(
            EmployeeAddressDetails.EMP_ID == get.EMP_ID,
            EmployeeAddressDetails.ADDRESS_TYPE == 'PERMANENT',
            EmployeeAddressDetails.DATE_FROM <= ESD,
            EmployeeAddressDetails.DATE_TO <= EED
        ).order_by(EmployeeAddressDetails.DATE_FROM.desc()).first()
        
        if get4:
            returndata['WorkEmployeeAddressDetails'] = get4.serialize()
        
        return jsonify([returndata]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    



# def SearchEmployeedetailss(emp,date,enddate):
#     try:
#         # data = request.json
#         ESD = date
#         emp_no = emp
       
#         print("ESD",type(ESD)),#type(enddate))
#         EED = '4712-12-31' #if enddate == 'undefined' else enddate
#         print("EED",EED)
#         returndata = []
#         get = EmployeeDetails.query.filter(
#                                    (EmployeeDetails.EMP_NO == emp_no) &
#                                     (EmployeeDetails.EFFECTIVE_START_DATE <= ESD)&
#                                     (EmployeeDetails.EFFECTIVE_END_DATE <= EED)
#                                 ).order_by(EmployeeDetails.EFFECTIVE_START_DATE.desc()).first()
       
#         print("get", get)
#         if not get:
#             return jsonify({'message': 'data not found'}), 404
#         returndata['EmployeeDetails'] =get.serialize()
#         get2 = EmploymentDetails.query.filter(
#                                    (EmploymentDetails.EMP_ID == get.EMP_ID) &
#                                     (EmploymentDetails.EFFECTIVE_START_DATE <= ESD)&
#                                     (EmploymentDetails.EFFECTIVE_END_DATE <= EED)
#                                 ).order_by(EmploymentDetails.EFFECTIVE_START_DATE.desc()).first()
#         if get2:
#             returndata['Employement_Details'] =get2.serialize()
 
#         get3 = EmployeeAddressDetails.query.filter(
#                                    (EmployeeAddressDetails.EMP_ID == get.EMP_ID) &
#                                    (EmployeeAddressDetails.ADDRESS_TYPE == 'HOME')&
#                                     (EmployeeAddressDetails.DATE_FROM <= ESD)&
#                                     (EmployeeAddressDetails.DATE_TO <= EED)
#                                 ).order_by(EmployeeAddressDetails.DATE_FROM.desc()).first()
#         if get3:
#             returndata['Home_EmployeeAddressDetails'] =get3.serialize()
       
#         get4 = EmployeeAddressDetails.query.filter(
#                                    (EmployeeAddressDetails.EMP_ID == get.EMP_ID) &
#                                    (EmployeeAddressDetails.ADDRESS_TYPE == 'WORK')&
#                                     (EmployeeAddressDetails.DATE_FROM <= ESD)&
#                                     (EmployeeAddressDetails.DATE_TO <= EED)
#                                 ).order_by(EmployeeAddressDetails.DATE_FROM.desc()).first()
#         if get4:
#             returndata['Work_EmployeeAddressDetails'] =get4.serialize()
 
       
#         print("data.serialize()", returndata)
#         return jsonify({'message': returndata}), 500, 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
 

def getEmpdetails(id):
    try:
        # data =Employement_Details.query.get(id)
        today = date.today()
        data = EmployeeDetails.query.filter((EmployeeDetails.EMP_ID==id) & (EmployeeDetails.EFFECTIVE_START_DATE <= today) &(today <= EmployeeDetails.EFFECTIVE_END_DATE)).first()
 
        print('data',data)
        if not data:
            return jsonify({'message': f'data {id} not found'}),404
        print("data.serialize()",data.serialize())
        return jsonify({'data' : data.serialize()}),200
    except Exception as e:
        return jsonify({'error':str(e)}),500

def getEmployee():
    try:
        today = date.today()
        # get=EMPLOYEE_DETAILS.query.filter((EMPLOYEE_DETAILS.EFFECTIVE_START_DATE <= today) &(today <= EMPLOYEE_DETAILS.EFFECTIVE_END_DATE)).all()
        # get = EmployeeDetails.query.filter(((EmployeeDetails.EMPLOYEE_NUMBER).startswith('C') & (today <= EmployeeDetails.EFFECTIVE_END_DATE)) |
        #                                      ((EmployeeDetails.EFFECTIVE_START_DATE <= today) &(today <= EmployeeDetails.EFFECTIVE_END_DATE))) .all()
        get = EmployeeDetails.query.filter(((EmployeeDetails.EFFECTIVE_START_DATE <= today) &(today <= EmployeeDetails.EFFECTIVE_END_DATE))) .all()
        returndata=[]
        if not get:
            return jsonify({'message': f'person {id} not found'}),404
        for i in get:
            returndata.append(i.serialize())
        return jsonify({'data': returndata}),200
    except Exception as e:
        return jsonify({'error':str(e)}),500

def upload_excel():
    try:
        excel = request.files['Excel']
        df = pd.read_excel(excel, sheet_name=0)
        duplicate_emp_nos = df[df.duplicated(subset='EMP_NO', keep=False)]['EMP_NO'].unique()
        duplicate_emails = df[df.duplicated(subset='EMAIL_ADDRESS', keep=False)]['EMAIL_ADDRESS'].unique()
 
        if duplicate_emp_nos.size > 0:
            return jsonify({'error': f'Duplicate employee numbers found in the uploaded file: {", ".join(map(str, duplicate_emp_nos))}'}), 400
 
        if duplicate_emails.size > 0:
            return jsonify({'error': f'Duplicate email addresses found in the uploaded file: {", ".join(map(str, duplicate_emails))}'}), 400
 
        newly_added_or_updated = []
        userEmail = 'sowmya@gmail.com'
        user = UserDetails.query.filter_by(EMAIL=userEmail).first()
 
        for index, row in df.iterrows():
            e_id = row.get('EMAIL_ADDRESS')
            e_no = row.get('EMP_NO')
 
            e_no_last_three = str(e_no)[-3:]
            existing_emp = EmployeeDetails.query.filter(
                EmployeeDetails.EMP_NO.like(f'%{e_no_last_three}') &
                (EmployeeDetails.EFFECTIVE_START_DATE <= row['EFFECTIVE_START_DATE']) &
                (EmployeeDetails.EFFECTIVE_END_DATE >= row['EFFECTIVE_START_DATE'])
            ).first()
 
            middleName = row.get('MIDDLE_NAME') if not pd.isna(row.get('MIDDLE_NAME')) else None 
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, e_id):
                return jsonify({'error': 'Invalid email format in the uploaded file'}), 400
 
            date_of_birth = row['DATE_OF_BIRTH']
            if isinstance(date_of_birth, pd.Timestamp):
                date_of_birth = date_of_birth.to_pydatetime().date()
            else:
                date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
 
            today = date.today()
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            if age < 18:
                return jsonify({'message': 'Employee must be at least 18 years old'}, 400)
 
            effective_start_date = row['EFFECTIVE_START_DATE']
            if isinstance(effective_start_date, pd.Timestamp):
                effective_start_date = effective_start_date.to_pydatetime().date()
            else:
                effective_start_date = datetime.strptime(effective_start_date, '%Y-%m-%d').date()
            existing_record = EmployeeDetails.query.filter_by(
                EMP_NO=row['EMP_NO'],
                FIRST_NAME=row['FIRST_NAME'],
                MIDDLE_NAME=middleName,
                LAST_NAME=row['LAST_NAME'],
                EMAIL_ADDRESS=e_id,
                DATE_OF_BIRTH=date_of_birth,
                WORKER_TYPE=row['WORKER_TYPE'],
                WORK_LOCATION=row['WORK_LOCATION'],
                EFFECTIVE_START_DATE=effective_start_date,
            ).first()
 
            if existing_record:
                continue  
 
            if existing_emp:
                if existing_emp.EFFECTIVE_START_DATE == effective_start_date:
                    updateData = {
                        'EMP_NO':row.get('EMP_NO'),
                        'FIRST_NAME': row.get('FIRST_NAME'),
                        'MIDDLE_NAME': row.get('MIDDLE_NAME'),
                        'LAST_NAME': row.get('LAST_NAME'),
                        'WORK_LOCATION': row.get('WORK_LOCATION'),
                        'WORKER_TYPE': row.get('WORKER_TYPE'),
                        'EMAIL_ADDRESS': e_id,
                    }
                    for key, value in updateData.items():
                        if getattr(existing_emp, key) != value:
                            setattr(existing_emp, key, value)
                    db.session.commit()
                    newly_added_or_updated.append(existing_emp.serialize())
                else:
                    emp_id = existing_emp.EMP_ID
 
                    existing_emp.EFFECTIVE_END_DATE = effective_start_date - timedelta(days=1)
                    db.session.commit()
 
                    future_records = EmployeeDetails.query.filter(
                        (EmployeeDetails.EMP_ID == emp_id) &
                        (EmployeeDetails.EFFECTIVE_START_DATE > effective_start_date)
                    ).order_by(EmployeeDetails.EFFECTIVE_START_DATE.asc()).all()
 
                    if future_records:
                        effective_end_date = future_records[0].EFFECTIVE_START_DATE - timedelta(days=1)
                    else:
                        effective_end_date = '4712-12-31'
 
                    for future_record in future_records:
                        if future_record.EFFECTIVE_START_DATE <= effective_end_date:
                            future_record.EFFECTIVE_END_DATE = effective_end_date
                            db.session.commit()
 
                    new_record = EmployeeDetails(
                        EMP_ID=emp_id,
                        EMP_NO=row['EMP_NO'],
                        FIRST_NAME=row['FIRST_NAME'],
                        MIDDLE_NAME=middleName,
                        LAST_NAME=row['LAST_NAME'],
                        WORK_LOCATION=row['WORK_LOCATION'],
                        EFFECTIVE_START_DATE=effective_start_date,
                        USER_ID=user.USER_ID,
                        DATE_OF_BIRTH=date_of_birth,
                        EFFECTIVE_END_DATE=effective_end_date,
                        WORKER_TYPE=row['WORKER_TYPE'],
                        EMAIL_ADDRESS=e_id,
                        CREATED_BY='HR',
                        LAST_UPDATED_BY='HR'
                    )
                    db.session.add(new_record)
                    db.session.commit()
                    newly_added_or_updated.append(new_record.serialize())
            else:
                details = EmployeeDetails(
                    EMP_NO=row['EMP_NO'],
                    FIRST_NAME=row['FIRST_NAME'],
                    MIDDLE_NAME=middleName,
                    LAST_NAME=row['LAST_NAME'],
                    WORK_LOCATION=row['WORK_LOCATION'],
                    EFFECTIVE_START_DATE=effective_start_date,
                    USER_ID=user.USER_ID,
                    DATE_OF_BIRTH=date_of_birth,
                    EFFECTIVE_END_DATE='4712-12-31',
                    WORKER_TYPE=row['WORKER_TYPE'],
                    EMAIL_ADDRESS=e_id,
                    CREATED_BY='HR',
                    LAST_UPDATED_BY='HR'
                )
                db.session.add(details)
                db.session.commit()
                newly_added_or_updated.append(details.serialize())
 
        if not newly_added_or_updated:
            return jsonify({"message": "No new data added"}), 200
 
        return jsonify({"message": "Bulk data added/updated successfully", 'details': newly_added_or_updated}), 201
 
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# def upload_excel():
#     try:
#         excel = request.files['Excel']
#         df = pd.read_excel(excel, sheet_name=0)
 
#         # Check for duplicates in EMP_NO and EMAIL_ADDRESS in the DataFrame
#         duplicate_emp_nos = df[df.duplicated(subset='EMP_NO', keep=False)]['EMP_NO'].unique()
#         duplicate_emails = df[df.duplicated(subset='EMAIL_ADDRESS', keep=False)]['EMAIL_ADDRESS'].unique()
 
#         if duplicate_emp_nos.size > 0:
#             return jsonify({'error': f'Duplicate employee numbers found in the uploaded file: {", ".join(map(str, duplicate_emp_nos))}'}), 400
 
#         if duplicate_emails.size > 0:
#             return jsonify({'error': f'Duplicate email addresses found in the uploaded file: {", ".join(map(str, duplicate_emails))}'}), 400
 
#         newly_added_or_updated = []
#         userEmail = 'sowmyanf@gmail.com'
#         user = UserDetails.query.filter_by(EMAIL=userEmail).first()
 
#         for index, row in df.iterrows():
#             e_id = row.get('EMAIL_ADDRESS')
#             e_no = row.get('EMP_NO')
 
#             # Get the last three digits of EMP_NO
#             e_no_last_three = str(e_no)[-3:]
 
#             # Check for existing records in the database with matching last three digits of EMP_NO
#             existing_emp = EmployeeDetails.query.filter(
#                 EmployeeDetails.EMP_NO.like(f'%{e_no_last_three}') &
#                 (EmployeeDetails.EFFECTIVE_START_DATE <= row['EFFECTIVE_START_DATE']) &
#                 (EmployeeDetails.EFFECTIVE_END_DATE >= row['EFFECTIVE_START_DATE'])
#             ).first()
 
#             middleName = row.get('MIDDLE_NAME') if not pd.isna(row.get('MIDDLE_NAME')) else None
 
#             email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#             if not re.match(email_pattern, e_id):
#                 return jsonify({'error': 'Invalid email format in the uploaded file'}), 400
 
#             date_of_birth = row['DATE_OF_BIRTH']
#             if isinstance(date_of_birth, pd.Timestamp):
#                 date_of_birth = date_of_birth.to_pydatetime().date()
#             else:
#                 date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
 
#             today = date.today()
#             age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
#             if age < 18:
#                 return jsonify({'message': 'Employee must be at least 18 years old'}, 400)
 
#             effective_start_date = row['EFFECTIVE_START_DATE']
#             if isinstance(effective_start_date, pd.Timestamp):
#                 effective_start_date = effective_start_date.to_pydatetime().date()
#             else:
#                 effective_start_date = datetime.strptime(effective_start_date, '%Y-%m-%d').date()
 
#             existing_record = EmployeeDetails.query.filter_by(
#                 EMP_NO=row['EMP_NO'],
#                 FIRST_NAME=row['FIRST_NAME'],
#                 MIDDLE_NAME=middleName,
#                 LAST_NAME=row['LAST_NAME'],
#                 EMAIL_ADDRESS=e_id,
#                 DATE_OF_BIRTH=date_of_birth,
#                 WORKER_TYPE=row['WORKER_TYPE'],
#                 WORK_LOCATION=row['WORK_LOCATION'],
#                 EFFECTIVE_START_DATE=effective_start_date,
#             ).first()
 
#             if existing_record:
#                 continue  
 
#             if existing_emp:
#                 emp_id = existing_emp.EMP_ID
 
#                 # Update the previous record's effective end date
#                 existing_emp.EFFECTIVE_END_DATE = effective_start_date - timedelta(days=1)
#                 db.session.commit()
 
#                 # Update the effective end dates of any future records
#                 future_records = EmployeeDetails.query.filter(
#                     (EmployeeDetails.EMP_ID == emp_id) &
#                     (EmployeeDetails.EFFECTIVE_START_DATE > effective_start_date)
#                 ).order_by(EmployeeDetails.EFFECTIVE_START_DATE.asc()).all()
 
#                 if future_records:
#                     # Update the new record's effective end date to be one day before the next future record's start date
#                     effective_end_date = future_records[0].EFFECTIVE_START_DATE - timedelta(days=1)
#                 else:
#                     effective_end_date = '4712-12-31'
 
#                 # Update effective end date of any future record that is now overlapping with the new record
#                 for future_record in future_records:
#                     if future_record.EFFECTIVE_START_DATE <= effective_end_date:
#                         future_record.EFFECTIVE_END_DATE = effective_end_date
#                         db.session.commit()
 
#                 # Add the new record with the same EMP_ID as the existing record
#                 new_record = EmployeeDetails(
#                     EMP_ID=emp_id,
#                     EMP_NO=row['EMP_NO'],
#                     FIRST_NAME=row['FIRST_NAME'],
#                     MIDDLE_NAME=middleName,
#                     LAST_NAME=row['LAST_NAME'],
#                     WORK_LOCATION=row['WORK_LOCATION'],
#                     EFFECTIVE_START_DATE=effective_start_date,
#                     USER_ID=user.USER_ID,
#                     DATE_OF_BIRTH=date_of_birth,
#                     EFFECTIVE_END_DATE=effective_end_date,
#                     WORKER_TYPE=row['WORKER_TYPE'],
#                     EMAIL_ADDRESS=e_id,
#                     CREATED_BY='HR',
#                     LAST_UPDATED_BY='HR'
#                 )
#                 db.session.add(new_record)
#                 db.session.commit()
#                 newly_added_or_updated.append(new_record.serialize())
#             else:
#                 # Insert a new record if no matching existing record is found
#                 details = EmployeeDetails(
#                     EMP_NO=row['EMP_NO'],
#                     FIRST_NAME=row['FIRST_NAME'],
#                     MIDDLE_NAME=middleName,
#                     LAST_NAME=row['LAST_NAME'],
#                     WORK_LOCATION=row['WORK_LOCATION'],
#                     EFFECTIVE_START_DATE=effective_start_date,
#                     USER_ID=user.USER_ID,
#                     DATE_OF_BIRTH=date_of_birth,
#                     EFFECTIVE_END_DATE='4712-12-31',
#                     WORKER_TYPE=row['WORKER_TYPE'],
#                     EMAIL_ADDRESS=e_id,
#                     CREATED_BY='HR',
#                     LAST_UPDATED_BY='HR'
#                 )
#                 db.session.add(details)
#                 db.session.commit()
#                 newly_added_or_updated.append(details.serialize())
 
#         if not newly_added_or_updated:
#             return jsonify({"message": "No new data added"}), 200
 
#         return jsonify({"message": "Bulk data added/updated successfully", 'details': newly_added_or_updated}), 201
 
#     except IntegrityError as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
   


def filter_employees(search_data):
    print('type(search_data):', type(search_data))
    person_list = []  
    try:
        search_date = date.fromisoformat(search_data)
        is_date = True
    except ValueError:
        is_date = False
    if is_date:
        person = EmployeeDetails.query.filter(
            (EmployeeDetails.EFFECTIVE_START_DATE <= search_date) &
            (EmployeeDetails.EFFECTIVE_END_DATE >= search_date)
        ).order_by(EmployeeDetails.EFFECTIVE_START_DATE.asc(), EmployeeDetails.EFFECTIVE_END_DATE.asc()).all()        
        if not person:
            person = EmployeeDetails.query.filter(
                EmployeeDetails.EFFECTIVE_START_DATE > search_date
            ).order_by(EmployeeDetails.EFFECTIVE_START_DATE.asc()).all()
        if person:
            person_dict = person.serialize()
            person_list.append(person_dict)
    else:
        persons = EmployeeDetails.query.filter(
            (EmployeeDetails.EMP_NO == search_data) |
            (EmployeeDetails.EMAIL_ADDRESS == search_data) |
            (func.lower(EmployeeDetails.FIRST_NAME).startswith(search_data.lower())) |
            (func.lower(EmployeeDetails.LAST_NAME).startswith(search_data.lower()))
        ).order_by(EmployeeDetails.EFFECTIVE_START_DATE.asc(), EmployeeDetails.EFFECTIVE_END_DATE.asc()).all()        
        if persons:
            for person in persons:
                person_dict = person.serialize()
                person_list.append(person_dict)  
    return jsonify(person_list), 200
 
 


def get_employees_all():
    try:
        today = date.today()
        subquery = (
            db.session.query(
                EmployeeDetails.EMP_ID,
                func.max(EmployeeDetails.EFFECTIVE_START_DATE).label("max_effective_start_date")
            )
            .group_by(EmployeeDetails.EMP_ID)
            .subquery()
        )
        latest_records = (
            db.session.query(EmployeeDetails)
            .join(subquery, and_(
                EmployeeDetails.EMP_ID == subquery.c.EMP_ID,
                EmployeeDetails.EFFECTIVE_START_DATE == subquery.c.max_effective_start_date
            ))
            .filter(EmployeeDetails.EFFECTIVE_END_DATE > today)
            .all()
        )
        returndata = [record.serialize() for record in latest_records]
        return jsonify({'data': returndata}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 



from num2words import num2words
import pythoncom


# def file_convert():
#     try:
#         data = request.json
#         if not data:
#             return jsonify({'error': 'No JSON data provided'}), 400          
       
#         EMP_ID, TEMPLATE_ID, TEMPLATE_NAME, ANNUAL_SALARY = data.get('EMP_ID'), data.get('TEMPLATE_ID'), data.get('TEMPLATE_NAME'), data.get('ANNUAL_SALARY')
     
#         if not all([EMP_ID, TEMPLATE_ID, ANNUAL_SALARY, TEMPLATE_NAME]):
#             return jsonify({'error': 'Missing required fields in JSON data'}), 400      
       
#         end_date = date(4712, 12, 31)
#         emp_latest_records = (
#             db.session.query(EmployeeDetails)
#             .filter(EmployeeDetails.EFFECTIVE_END_DATE == end_date)
#             .filter(EmployeeDetails.EMP_ID == EMP_ID)
#             .all()
#         )
#         employment_latest_records = (
#             db.session.query(EmploymentDetails)
#             .filter(EmploymentDetails.EFFECTIVE_END_DATE == end_date)
#             .filter(EmploymentDetails.EMP_ID == EMP_ID)
#             .all()
#         )
#         if not emp_latest_records or not employment_latest_records:
#             return jsonify({'error': 'No records found for the given EMP_ID with the specified end date'}), 404
#         emp_data = [record.serialize() for record in emp_latest_records]
#         employment_data = [record.serialize() for record in employment_latest_records]
#         file_info_employee = emp_data[0] if emp_data else {}
#         file_info_employments = employment_data[0] if employment_data else {}

#         dictt = {}
#         Basic_Salary_year = ANNUAL_SALARY * 0.5
#         dictt['Basic_Salary_year'] = f'{Basic_Salary_year:,.0f}'
#         Basic_Salary_month = Basic_Salary_year // 12
#         dictt['Basic_Salary_month'] = int(Basic_Salary_month)
#         House_Rent_Allowance_year = Basic_Salary_year * 0.4
#         dictt['House_Rent_Allowance_year'] = int(House_Rent_Allowance_year)
#         House_Rent_Allowance_month = Basic_Salary_month * 0.4
#         dictt['House_Rent_Allowance_month'] = int(House_Rent_Allowance_month)
#         Special_Allowance_year = ANNUAL_SALARY - Basic_Salary_year - House_Rent_Allowance_year
#         dictt['Special_Allowance_year'] = int(Special_Allowance_year)
#         Special_Allowance_month = ANNUAL_SALARY // 12 - Basic_Salary_month - House_Rent_Allowance_month
#         dictt['Special_Allowance_month'] = int(Special_Allowance_month)
#         Gross_Compensation_year = Basic_Salary_year + House_Rent_Allowance_year + Special_Allowance_year
#         dictt['Gross_Compensation_year'] = int(Gross_Compensation_year)
#         Gross_Compensation_month = Basic_Salary_month + House_Rent_Allowance_month + Special_Allowance_month
#         dictt['Gross_Compensation_month'] = int(Gross_Compensation_month)
#         PF_month = 0 if Basic_Salary_month < 15000 else 1800
#         dictt['PF_month'] = int(PF_month)
#         PF_year = 0 if Basic_Salary_year < 180000 else 1800
#         dictt['PF_year'] = int(PF_year)
#         Total_Base_Compensation_year = Gross_Compensation_year + PF_year
#         dictt['Total_Base_Compensation_year'] = int(Total_Base_Compensation_year)
#         Total_Base_Compensation_month = Gross_Compensation_month + PF_month
#         dictt['Total_Base_Compensation_month'] = int(Total_Base_Compensation_month)
#         Gratuity_month = Basic_Salary_month * 4.81 / 100
#         dictt['Gratuity_month'] = int(Gratuity_month)
#         Gratuity_year = Basic_Salary_year * 4.81 / 100
#         dictt['Gratuity_year'] = int(Gratuity_year)
#         Insurance_annum =  25000 if Gross_Compensation_month > 21000 else 0
#         dictt['Insurance_annum'] = Insurance_annum
#         Insurance_month = Insurance_annum // 12
#         dictt['Insurance_month'] = Insurance_month
#         Performance_incentive_year = 0
#         dictt['Performance_incentive_year'] = Performance_incentive_year
#         Performance_incentive_month = 0
#         dictt['Performance_incentive_month'] = Performance_incentive_month
#         Total_Cost_to_Company_year = Total_Base_Compensation_year + Gratuity_year + Insurance_annum +Performance_incentive_year
#         dictt['Total_Cost_to_Company_year'] = f'{Total_Cost_to_Company_year:,.0f}'
#         Total_Cost_to_Company_month = Total_Base_Compensation_month + Gratuity_month +Insurance_month + Performance_incentive_month
#         dictt['Total_Cost_to_Company_month'] = int(Total_Cost_to_Company_month)
#         today_date = datetime.today().date()
#         dictt['today_date']=today_date
        # output_pdf = 'C:\\Users\\durga\\Downloads\\NFCS\\n90.pdf'

#         template = LetterTemplates.query.get(TEMPLATE_ID)
#         if not template:
#             return jsonify({'error': 'Template not found'}), 404
#         rtf_content = template.TEMPLATE.decode('utf-8')
#         file3 = rtf_content
#         for key, value in file_info_employee.items():
#             file3 = re.sub(fr'\b{re.escape(key)}\b', str(value), file3)
#         for key, value in file_info_employments.items():
#             file3 = re.sub(fr'\b{re.escape(key)}\b', str(value), file3)
#         for key, value in dictt.items():
#             file3 = re.sub(fr'\b{re.escape(key)}\b', str(value), file3)
        # file_name = f'C:\\Users\\durga\\Downloads\\NFCS\\EMOLOYEE_{EMP_ID}.rtf'
#         with open(file_name, 'wb') as file2:
#             file2.write(file3.encode('utf-8'))        
#         pythoncom.CoInitialize()
#         word = win32com.client.Dispatch("Word.Application")
#         doc = word.Documents.Open(os.path.abspath(file_name))
#         doc.SaveAs(output_pdf, FileFormat=17)
#         doc.Close()
#         word.Quit()
#         with open(output_pdf, 'rb') as file:
#             file_contents = file.read()

#         return send_file(BytesIO(file_contents), as_attachment=True, mimetype='application/pdf', download_name='n90.pdf')    
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
 
def file_convert():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
 
        EMP_NO = data.get('EMP_NO')
        TEMPLATE_ID = data.get('TEMPLATE_ID')
        TEMPLATE_NAME = data.get('TEMPLATE_NAME')
        
       
  
        if not all([EMP_NO, TEMPLATE_ID, TEMPLATE_NAME]):
            return jsonify({'error': 'Missing required fields in JSON data'}), 400
 
        if TEMPLATE_NAME == "Appoinment Letter" and not EMP_NO.startswith('C'):
            return jsonify({'error': 'Invalid EMP_NO for Appointment Letter'}), 400
 
        today = date.today()
 
        emp_record = (
            db.session.query(EmployeeDetails)
            .filter(EmployeeDetails.EMP_NO == EMP_NO)
            .order_by(EmployeeDetails.EFFECTIVE_START_DATE.desc())
            .first()
        )
 
        if not emp_record:
            return jsonify({'error': 'No employee found with the given EMP_NO'}), 404
 
        EMP_ID = emp_record.EMP_ID
        
 
        if TEMPLATE_NAME == "Appoinment Letter":
            emp_latest_record = (
                db.session.query(EmployeeDetails)
                .filter(EmployeeDetails.EMP_NO == EMP_NO)
                .filter(EmployeeDetails.EFFECTIVE_START_DATE <= today)
                .order_by(EmployeeDetails.EFFECTIVE_START_DATE.asc())
                .first()
            )
        else:
            emp_latest_record = (
                db.session.query(EmployeeDetails)
                .filter(EmployeeDetails.EMP_NO == EMP_NO)
                .filter(EmployeeDetails.EFFECTIVE_START_DATE <= today)
                .order_by(EmployeeDetails.EFFECTIVE_START_DATE.desc())
                .first()
            )
            print("dcfgh235j",emp_latest_record)
 
        employment_latest_record = (
            db.session.query(EmploymentDetails)
            .filter(EmploymentDetails.EMP_ID == emp_record.EMP_ID)
            .filter(EmploymentDetails.EFFECTIVE_START_DATE <= today)
            .order_by(EmploymentDetails.EFFECTIVE_START_DATE.desc())
            .first()
        )
        print("dcfvgbhnj",employment_latest_record)
        print("234567",EMP_ID)
 
        if not emp_latest_record or not employment_latest_record:
            return jsonify({'error': 'No records found for the given EMP_NO with the specified end date'}), 404
 
        emp_data = emp_latest_record.serialize()
        employment_data = employment_latest_record.serialize()
        ANNUAL_SALARY=employment_latest_record.ANNUAL_SALARY
        print("2345",ANNUAL_SALARY)
        
 
        dictt = {}
 
        if ANNUAL_SALARY:
            Basic_Salary_year = ANNUAL_SALARY * 0.5
            dictt['Basic_Salary_year'] = f'{Basic_Salary_year:,.0f}'
            Basic_Salary_month = Basic_Salary_year / 12
            dictt['Basic_Salary_month'] = int(Basic_Salary_month)
            House_Rent_Allowance_year = Basic_Salary_year * 0.4
            dictt['House_Rent_Allowance_year'] = int(House_Rent_Allowance_year)
            House_Rent_Allowance_month = Basic_Salary_month * 0.4
            dictt['House_Rent_Allowance_month'] = int(House_Rent_Allowance_month)
            Special_Allowance_year = ANNUAL_SALARY - Basic_Salary_year - House_Rent_Allowance_year
            dictt['Special_Allowance_year'] = int(Special_Allowance_year)
            Special_Allowance_month = ANNUAL_SALARY / 12 - Basic_Salary_month - House_Rent_Allowance_month
            dictt['Special_Allowance_month'] = int(Special_Allowance_month)
            Gross_Compensation_year = Basic_Salary_year + House_Rent_Allowance_year + Special_Allowance_year
            dictt['Gross_Compensation_year'] = int(Gross_Compensation_year)
            Gross_Compensation_month = Basic_Salary_month + House_Rent_Allowance_month + Special_Allowance_month
            dictt['Gross_Compensation_month'] = int(Gross_Compensation_month)
            PF_month = 0 if Basic_Salary_month < 15000 else 1800
            dictt['PF_month'] = int(PF_month)
            PF_year = 0 if Basic_Salary_year < 180000 else 21600
            dictt['PF_year'] = int(PF_year)
            Total_Base_Compensation_year = Gross_Compensation_year + PF_year
            dictt['Total_Base_Compensation_year'] = int(Total_Base_Compensation_year)
            Total_Base_Compensation_month = Gross_Compensation_month + PF_month
            dictt['Total_Base_Compensation_month'] = int(Total_Base_Compensation_month)
            Gratuity_month = Basic_Salary_month * 4.81 / 100
            dictt['Gratuity_month'] = int(Gratuity_month)
            Gratuity_year = Basic_Salary_year * 4.81 / 100
            dictt['Gratuity_year'] = int(Gratuity_year)
            Insurance_annum = 25000 if Gross_Compensation_month > 21000 else 0
            dictt['Insurance_annum'] = Insurance_annum
            Insurance_month = Insurance_annum / 12
            dictt['Insurance_month'] = int(Insurance_month)
            Performance_incentive_year = 0
            dictt['Performance_incentive_year'] = Performance_incentive_year
            dictt['Performance_incentive_month'] = 0
            Total_Cost_to_Company_year = Total_Base_Compensation_year + Gratuity_year + Insurance_annum + Performance_incentive_year
            dictt['Total_Cost_to_Company_year'] = f'{Total_Cost_to_Company_year:,.0f}'
            Total_Cost_to_Company_month = Total_Base_Compensation_month + Gratuity_month + Insurance_month
            dictt['Total_Cost_to_Company_month'] = int(Total_Cost_to_Company_month)
            SALARY_INWORD = num2words(ANNUAL_SALARY, lang='en_IN').replace(',', '').replace('-', ' ')
            dictt['WORDS'] = SALARY_INWORD
            dictt['CTC'] = ANNUAL_SALARY
 
        dictt['today_date'] = datetime.today().date()
 
        output_pdf = 'C:\\Users\\durga\\Downloads\\NFCS\\n90.pdf'
        template = LetterTemplates.query.get(TEMPLATE_ID)
        if not template:
            return jsonify({'error': 'Template not found'}), 404
 
        rtf_content = template.TEMPLATE.decode('utf-8')
        file3 = rtf_content
        for key, value in {**emp_data, **employment_data, **dictt}.items():
            file3 = re.sub(fr'\b{re.escape(key)}\b', str(value), file3)
        file_name = f'C:\\Users\\durga\\Downloads\\NFCS\\EMOLOYEE_{EMP_ID}.rtf'
        with open(file_name, 'wb') as file2:
            file2.write(file3.encode('utf-8'))
 
        pythoncom.CoInitialize()
        word = win32com.client.Dispatch("Word.Application")
        doc = word.Documents.Open(os.path.abspath(file_name))
        doc.SaveAs(output_pdf, FileFormat=17)
        doc.Close()
        word.Quit()
 
        with open(output_pdf, 'rb') as file:
            file_contents = file.read()
 
        new_letter = EmployeeLetters(
            EMP_ID=EMP_ID,
            TEMPLATE_ID=TEMPLATE_ID,
            LETTER_TYPE=TEMPLATE_NAME,
            LETTER=file_contents,
            CREATED_BY="HR",  
            LAST_UPDATED_BY="HR"  
        )
        db.session.add(new_letter)
        db.session.commit()
 
        return send_file(BytesIO(file_contents), as_attachment=True, mimetype='application/pdf', download_name='n90.pdf')
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 

# def file_convert():
#     try:
#         data = request.json
#         if not data:
#             return jsonify({'error': 'No JSON data provided'}), 400

#         EMP_ID = data.get('EMP_ID')
#         TEMPLATE_ID = data.get('TEMPLATE_ID')
#         TEMPLATE_NAME = data.get('TEMPLATE_NAME')
#         CTC = data.get('CTC')

#         if not all([EMP_ID, TEMPLATE_ID, TEMPLATE_NAME]):
#             return jsonify({'error': 'Missing required fields in JSON data'}), 400

#         today = date.today()

#         # Fetch employee details based on EMP_ID
#         if TEMPLATE_NAME == "Appointment_Letter":
#             emp_latest_record = (
#                 db.session.query(EmployeeDetails)
#                 .filter(EmployeeDetails.EMP_ID == EMP_ID)
#                 .filter(EmployeeDetails.EFFECTIVE_START_DATE <= today)
#                 .order_by(EmployeeDetails.EFFECTIVE_START_DATE.asc()).first()
#             )
#         else:
#             emp_latest_record = (
#                 db.session.query(EmployeeDetails)
#                 .filter(EmployeeDetails.EMP_ID == EMP_ID)
#                 .filter(EmployeeDetails.EFFECTIVE_START_DATE <= today)
#                 .order_by(EmployeeDetails.EFFECTIVE_START_DATE.desc()).first()
#             )

#         if not emp_latest_record:
#             return jsonify({'error': 'No employee details found for the given EMP_ID with the specified end date'}), 404

#         employment_latest_record = (
#             db.session.query(EmploymentDetails)
#             .filter(EmploymentDetails.EMP_ID == EMP_ID)
#             .filter(EmploymentDetails.EFFECTIVE_START_DATE >= today)
#             .order_by(EmploymentDetails.EFFECTIVE_START_DATE.desc()).first()
#         )

#         if not employment_latest_record:
#             return jsonify({'error': 'No employment details found for the given EMP_ID with the specified end date'}), 404

#         emp_data = emp_latest_record.serialize()
#         employment_data = employment_latest_record.serialize()

#         dictt = {}

#         if CTC:
#             Basic_Salary_year = CTC * 0.5
#             dictt['Basic_Salary_year'] = f'{Basic_Salary_year:,.0f}'
#             Basic_Salary_month = Basic_Salary_year / 12
#             dictt['Basic_Salary_month'] = int(Basic_Salary_month)
#             House_Rent_Allowance_year = Basic_Salary_year * 0.4
#             dictt['House_Rent_Allowance_year'] = int(House_Rent_Allowance_year)
#             House_Rent_Allowance_month = Basic_Salary_month * 0.4
#             dictt['House_Rent_Allowance_month'] = int(House_Rent_Allowance_month)
#             Special_Allowance_year = CTC - Basic_Salary_year - House_Rent_Allowance_year
#             dictt['Special_Allowance_year'] = int(Special_Allowance_year)
#             Special_Allowance_month = CTC / 12 - Basic_Salary_month - House_Rent_Allowance_month
#             dictt['Special_Allowance_month'] = int(Special_Allowance_month)
#             Gross_Compensation_year = Basic_Salary_year + House_Rent_Allowance_year + Special_Allowance_year
#             dictt['Gross_Compensation_year'] = int(Gross_Compensation_year)
#             Gross_Compensation_month = Basic_Salary_month + House_Rent_Allowance_month + Special_Allowance_month
#             dictt['Gross_Compensation_month'] = int(Gross_Compensation_month)
#             PF_month = 0 if Basic_Salary_month < 15000 else 1800
#             dictt['PF_month'] = int(PF_month)
#             PF_year = 0 if Basic_Salary_year < 180000 else 21600  # Corrected PF_year calculation
#             dictt['PF_year'] = int(PF_year)
#             Total_Base_Compensation_year = Gross_Compensation_year + PF_year
#             dictt['Total_Base_Compensation_year'] = int(Total_Base_Compensation_year)
#             Total_Base_Compensation_month = Gross_Compensation_month + PF_month
#             dictt['Total_Base_Compensation_month'] = int(Total_Base_Compensation_month)
#             Gratuity_month = Basic_Salary_month * 4.81 / 100
#             dictt['Gratuity_month'] = int(Gratuity_month)
#             Gratuity_year = Basic_Salary_year * 4.81 / 100
#             dictt['Gratuity_year'] = int(Gratuity_year)
#             Insurance_annum = 25000 if Gross_Compensation_month > 21000 else 0
#             dictt['Insurance_annum'] = Insurance_annum
#             Insurance_month = Insurance_annum / 12
#             dictt['Insurance_month'] = int(Insurance_month)
#             Performance_incentive_year = 0
#             dictt['Performance_incentive_year'] = Performance_incentive_year
#             Performance_incentive_month = 0
#             dictt['Performance_incentive_month'] = Performance_incentive_month
#             Total_Cost_to_Company_year = Total_Base_Compensation_year + Gratuity_year + Insurance_annum + Performance_incentive_year
#             dictt['Total_Cost_to_Company_year'] = f'{Total_Cost_to_Company_year:,.0f}'
#             Total_Cost_to_Company_month = Total_Base_Compensation_month + Gratuity_month + Insurance_month + Performance_incentive_month
#             dictt['Total_Cost_to_Company_month'] = int(Total_Cost_to_Company_month)
#             SALARY_INWORD = num2words(CTC, lang='en_IN').replace(',', '').replace('-', ' ')
#             dictt['WORDS'] = SALARY_INWORD
#             dictt['CTC'] = CTC

#         dictt['today_date'] = datetime.today().date()

#         output_pdf = 'F:\\new\\n90.pdf'
#         template = LetterTemplates.query.get(TEMPLATE_ID)
#         if not template:
#             return jsonify({'error': 'Template not found'}), 404
#         rtf_content = template.TEMPLATE.decode('utf-8')
#         file3 = rtf_content
#         for key, value in {**emp_data, **employment_data, **dictt}.items():
#             file3 = re.sub(fr'\b{re.escape(key)}\b', str(value), file3)
#         file_name = f'F:\\file\\EMPLOYEE_{EMP_ID}.rtf'
#         with open(file_name, 'wb') as file2:
#             file2.write(file3.encode('utf-8'))

#         pythoncom.CoInitialize()
#         word = win32com.client.Dispatch("Word.Application")
#         doc = word.Documents.Open(os.path.abspath(file_name))
#         doc.SaveAs(output_pdf, FileFormat=17)
#         doc.Close()
#         word.Quit()

#         with open(output_pdf, 'rb') as file:
#             file_contents = file.read()

#         return send_file(BytesIO(file_contents), as_attachment=True, mimetype='application/pdf', download_name='n90.pdf')
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500