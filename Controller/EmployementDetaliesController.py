import re
from sqlite3 import IntegrityError
from flask import Flask, request, jsonify
import mysql.connector
from sqlalchemy import Text, desc, func
from config import *
from model.EmployeDetalies import *
from model.EmploymentDetaliess import *
from datetime import date, datetime, timedelta




from flask import jsonify
# def add_employment_details():
#     try:
#         data = request.json
#         required_fields = [
#             'EMP_ID', 'ORGANIZATION_NAME', 'POSITION', 'DEPARTMENT', 'ANNUAL_SALARY',
#             'PREVIOUS_ANNUAL_SALARY', 'PROBATION_PERIOD', 'NOTICE_PERIOD', 'STATUS', 'EFFECTIVE_START_DATE', 'DATE_OF_JOINING'
#         ]
 
#         missing_fields = [field for field in required_fields if field not in data]
#         if missing_fields:
#             return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
 
#         mobile_no = data.get('MOBILE_NO')
#         if mobile_no and (not re.match(r'^\d{10}$', str(mobile_no))):
#             return jsonify({'error': 'Mobile number should be exactly 10 digits long'}), 400
 
#         emp_id = data.get('EMP_ID')
#         start_date_str = data.get('EFFECTIVE_START_DATE')
#         start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else date.today()
 
#         date_of_joining_str = data.get('DATE_OF_JOINING')
#         date_of_joining = datetime.strptime(date_of_joining_str, '%Y-%m-%d').date() if date_of_joining_str else None
 
#         if not date_of_joining:
#             return jsonify({'error': 'DATE_OF_JOINING is required'}), 400
#         confirmation_date = date_of_joining + timedelta(days=365)
 
#         employee_details = EmployeeDetails.query.filter_by(EMP_ID=emp_id).first()
#         if not employee_details:
#             return jsonify({'error': 'Employee ID not found'}), 404
 
#         dbemployee = EmploymentDetails.query.filter_by(EMP_ID=emp_id).order_by(EmploymentDetails.EFFECTIVE_START_DATE.desc()).first()
#         if dbemployee and start_date <= dbemployee.EFFECTIVE_END_DATE:
#             # Update existing record if it starts on or before the new start date
#             dbemployee.EFFECTIVE_END_DATE = start_date - timedelta(days=1)
#             db.session.commit()
 
#             # Ensure future records' EFFECTIVE_END_DATE are also updated correctly
#             future_records = EmploymentDetails.query.filter(
#                 (EmploymentDetails.EMP_ID == emp_id) &
#                 (EmploymentDetails.EFFECTIVE_START_DATE > start_date)
#             ).all()
 
#             for future_record in future_records:
#                 if future_record.EFFECTIVE_END_DATE > start_date:
#                     future_record.EFFECTIVE_END_DATE = start_date - timedelta(days=1)
#                     db.session.commit()
 
#         # Insert new employment details
#         new_data = EmploymentDetails(
#             EMP_ID=data.get('EMP_ID'),
#             ORGANIZATION_NAME=data.get('ORGANIZATION_NAME'),
#             POSITION=data.get('POSITION'),
#             DEPARTMENT=data.get('DEPARTMENT'),
#             ANNUAL_SALARY=data.get('ANNUAL_SALARY'),
#             WORKER_TYPE = data.get('WORKER_TYPE'),
#             DATE_OF_JOINING=date_of_joining,
#             PREVIOUS_ANNUAL_SALARY=data.get('PREVIOUS_ANNUAL_SALARY'),
#             CURRENT_COMP_EXPERIENCE = data.get('CURRENT_COMP_EXPERIENCE'),
#             PREVIOUS_EXPERIENCE = data.get('PREVIOUS_EXPERIENCE'),
#             STATUS=data.get('STATUS'),
#             CONFIRMATION_DATE=confirmation_date,
#             MOBILE_NO=mobile_no,
#             PROBATION_PERIOD=data.get('PROBATION_PERIOD'),
#             NOTICE_PERIOD=data.get('NOTICE_PERIOD'),
#             EFFECTIVE_START_DATE=start_date,
#             EFFECTIVE_END_DATE=data.get('EFFECTIVE_END_DATE', date(4712, 12, 31)),
#             CREATED_BY="HR",
#             LAST_UPDATED_BY="HR"
#         )
 
#         db.session.add(new_data)
#         db.session.commit()
 
#         return jsonify({'message': "New record added", 'data': new_data.serialize()}), 201
 
#     except IntegrityError as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
from dateutil.relativedelta import relativedelta

def add_employment_details():
    try:
        today = date.today()
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        EMP_ID = data.get('EMP_ID')
        EFFECTIVE_START_DATE = data.get('EFFECTIVE_START_DATE')
        DATE_OF_JOINING = data.get('DATE_OF_JOINING')
        if not all([EMP_ID, EFFECTIVE_START_DATE, DATE_OF_JOINING]):
            return jsonify({'error': 'Missing required fields in JSON data'}), 400

        esd = datetime.strptime(EFFECTIVE_START_DATE, "%Y-%m-%d").date()
        DOJ = datetime.strptime(DATE_OF_JOINING, "%Y-%m-%d").date()

        probation_period = data.get('PROBATION_PERIOD')
        if probation_period:
            if probation_period.isdigit():
                return jsonify({'error': 'Please specify the unit probation period(Days or Months or Years)'})
            elif 'Days' in probation_period:
                days = int(probation_period.split('Days')[0])
            elif 'Months' in probation_period:
                months = int(probation_period.split('Months')[0])
                days= months * 30
            elif 'Years' in probation_period:
                years = int(probation_period.split('Years')[0])
                days = years * 365
            else:
                return jsonify({'error': 'Invalid format for probation period eg:90 Days,2 Months,3 Years'}), 400
        else:
            days = 0

        confirmation_date = DOJ + timedelta(days=days)
        dbemp = EmploymentDetails.query.filter(
            (EmploymentDetails.EMP_ID == EMP_ID) &
            (EmploymentDetails.EFFECTIVE_START_DATE <= esd) &
            (esd <= EmploymentDetails.EFFECTIVE_END_DATE)
        ).first()

        if dbemp:
            # Existing employee
            if dbemp.EFFECTIVE_START_DATE == esd:
                # Update existing record
                updateData = {
                    'ORGANIZATION_NAME': data.get('ORGANIZATION_NAME'),
                    'POSITION': data.get('POSITION'),
                    'WORKER_TYPE': data.get('WORKER_TYPE'),
                    'CONFIRMATION_DATE': confirmation_date,
                    'STATUS': data.get('STATUS'),
                    'PROBATION_PERIOD': data.get('PROBATION_PERIOD'),
                    'DATE_OF_JOINING': data.get('DATE_OF_JOINING'),
                    'NOTICE_PERIOD': data.get('NOTICE_PERIOD'),
                    'CURRENT_COMP_EXPERIENCE': data.get('CURRENT_COMP_EXPERIENCE'),
                    'PREVIOUS_EXPERIENCE': data.get('PREVIOUS_EXPERIENCE'),
                    'MOBILE_NO': data.get('MOBILE_NO'),
                    'DEPARTMENT': data.get('DEPARTMENT'),
                    'PREVIOUS_ANNUAL_SALARY': data.get('PREVIOUS_ANNUAL_SALARY'),
                    'ANNUAL_SALARY': data.get('ANNUAL_SALARY')
                }
                for key, value in updateData.items():
                    if getattr(dbemp, key) != value:
                        setattr(dbemp, key, value)
                db.session.commit()
                return jsonify({"message": "Existing record updated", "data": dbemp.serialize()}), 200
            else:
                # Update existing record's end date and add a new record
                dbemp.EFFECTIVE_END_DATE = esd - timedelta(days=1)
                db.session.commit()

                # Calculate end date for current record
                next_record = EmploymentDetails.query.filter(
                    (EmploymentDetails.EMP_ID == EMP_ID) &
                    (EmploymentDetails.EFFECTIVE_START_DATE > esd)
                ).order_by(EmploymentDetails.EFFECTIVE_START_DATE.asc()).first()

                if next_record:
                    eed = next_record.EFFECTIVE_START_DATE - timedelta(days=1)
                else:
                    eed = date(4712, 12, 31)

                # Create new record
                new_details = EmploymentDetails(
                    EMP_ID=data.get('EMP_ID'),
                    ORGANIZATION_NAME=data.get('ORGANIZATION_NAME'),
                    POSITION=data.get('POSITION'),
                    DEPARTMENT=data.get('DEPARTMENT'),
                    CONFIRMATION_DATE=confirmation_date,
                    WORKER_TYPE=data.get('WORKER_TYPE'),
                    STATUS=data.get('STATUS'),
                    ANNUAL_SALARY=data.get('ANNUAL_SALARY'),
                    PROBATION_PERIOD=data.get('PROBATION_PERIOD'),
                    NOTICE_PERIOD=data.get('NOTICE_PERIOD'),
                    MOBILE_NO=data.get('MOBILE_NO'),
                    DATE_OF_JOINING=data.get('DATE_OF_JOINING'),
                    CURRENT_COMP_EXPERIENCE=data.get('CURRENT_COMP_EXPERIENCE'),
                    PREVIOUS_EXPERIENCE=data.get('PREVIOUS_EXPERIENCE'),
                    PREVIOUS_ANNUAL_SALARY=data.get('PREVIOUS_ANNUAL_SALARY'),
                    EFFECTIVE_START_DATE=esd,
                    EFFECTIVE_END_DATE=eed,
                    CREATED_BY='HR',
                    LAST_UPDATED_BY='HR'
                )
                db.session.add(new_details)
                db.session.commit()
                return jsonify({"message": f"{data['EMP_ID']} new record added successfully", "data": new_details.serialize()}), 201

        else:
            # New employee
            details = EmploymentDetails(
                EMP_ID=data.get('EMP_ID'),
                ORGANIZATION_NAME=data.get('ORGANIZATION_NAME'),
                POSITION=data.get('POSITION'),
                DEPARTMENT=data.get('DEPARTMENT'),
                CONFIRMATION_DATE=confirmation_date,
                WORKER_TYPE=data.get('WORKER_TYPE'),
                STATUS=data.get('STATUS'),
                ANNUAL_SALARY=data.get('ANNUAL_SALARY'),
                PROBATION_PERIOD=data.get('PROBATION_PERIOD'),
                NOTICE_PERIOD=data.get('NOTICE_PERIOD'),
                MOBILE_NO=data.get('MOBILE_NO'),
                DATE_OF_JOINING=data.get('DATE_OF_JOINING'),
                CURRENT_COMP_EXPERIENCE=data.get('CURRENT_COMP_EXPERIENCE'),
                PREVIOUS_EXPERIENCE=data.get('PREVIOUS_EXPERIENCE'),
                PREVIOUS_ANNUAL_SALARY=data.get('PREVIOUS_ANNUAL_SALARY'),
                EFFECTIVE_START_DATE=data.get('EFFECTIVE_START_DATE'),
                EFFECTIVE_END_DATE=data.get('EFFECTIVE_END_DATE') if data.get('EFFECTIVE_END_DATE') else date(4712, 12, 31),
                CREATED_BY='HR',
                LAST_UPDATED_BY='HR'
            )
            db.session.add(details)
            db.session.commit()
            return jsonify({"message": f"{data['EMP_ID']} employment details added successfully", "data": details.serialize()}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
