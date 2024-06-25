
# from model.UserDetalies import *
import io
from flask import Flask, request, jsonify, send_file
from model.EmployeDetalies import EmployeeDetails
from model.EmployeeLetters import *
# from model.LetterTemplates import *
from datetime import datetime

from model.LetterTemplates import LetterTemplates

from sqlalchemy.orm import joinedload


from sqlalchemy.orm import aliased
from sqlalchemy import and_, asc, desc

from sqlalchemy import engine
from sqlalchemy.orm import sessionmaker

def add_employee_letter():
    try:
        data = request.json
        print('data', data)
        emp_id = data.get('EMP_ID')
        employee = EmployeeLetters.query.get(emp_id)
        if not employee:
            return jsonify({'error': 'Employee does not exist'}), 400
        
        template_id = data.get('TEMPLATE_ID')
        template = LetterTemplates.query.get(template_id)
        if not template:
            return jsonify({'error': 'Template does not exist'}), 400

        letter_data = EmployeeLetters(
            EMP_ID=emp_id,
            TEMPLATE_ID=template_id,
            LETTER_TYPE=data['LETTER_TYPE'],
            LETTER=data['LETTER'],  
            CREATED_BY="HR",
            LAST_UPDATED_BY="HR"
        )
        db.session.add(letter_data)
        db.session.commit()
        return jsonify({'message': 'Employee letter added successfully', 'data': letter_data.serialize()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_temployeeId(TEMPLATE_ID):
    try:
        data = EmployeeLetters.query.get(TEMPLATE_ID)
        if not data:
                return jsonify({'message':'template not found'}),404
        return jsonify({'message':f'employee {TEMPLATE_ID}','data':data.serialize()}),200
    except Exception as err:
        return jsonify({'err':str(err)}),500
    
# def get_employees_templates():
#     try:
#         all_letters = EmployeeLetters.query.all()
#         serialized_letters = [letter.serialize() for letter in all_letters]
#         return jsonify(serialized_letters), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
# def get_employees_templates():
#     try:
#         all_letters = EmployeeLetters.query.options(joinedload(EmployeeLetters.employee)).all()
        
#         serialized_letters = [
#             {
#                 'CREATED_BY': letter.CREATED_BY,
#                 'EMP_ID': letter.EMP_ID,
#                 'LAST_UPDATED_BY': letter.LAST_UPDATED_BY,
#                 'LETTER_ID': letter.LETTER_ID,
#                 'LETTER_TYPE': letter.LETTER_TYPE,
#                 'TEMPLATE_ID': letter.TEMPLATE_ID,
#                 'EMP_NO': letter.employee.EMP_NO  
#             }
#             for letter in all_letters
#         ]
        
#         return jsonify(serialized_letters), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
def get_employees_templates():
    try:
        # Alias for the EmployeeDetails to use in subquery
        EmployeeDetailsAlias = aliased(EmployeeDetails)
       
        # Function to create subquery based on order direction and filter for "C"
        def create_subquery(order_direction, filter_c=False):
            query = db.session.query(
                EmployeeDetailsAlias.EMP_ID,
                EmployeeDetailsAlias.EMP_NO
            ).filter(
                EmployeeDetailsAlias.EFFECTIVE_END_DATE >= datetime.now()
            )
            if filter_c:
                query = query.filter(EmployeeDetailsAlias.EMP_NO.like('C%'))
            return query.order_by(
                order_direction(EmployeeDetailsAlias.EFFECTIVE_START_DATE)
            ).subquery()
       
        # Subqueries for different orderings
        subquery_asc_c = create_subquery(asc, filter_c=True)
        subquery_desc = create_subquery(desc)
 
        # Main query to get all letters, join with the templates, and join with the latest employee details
        all_letters = db.session.query(
            EmployeeLetters,
            LetterTemplates.TEMPLATE_NAME,
            subquery_asc_c.c.EMP_NO.label("EMP_NO_ASC_C"),
            subquery_desc.c.EMP_NO.label("EMP_NO_DESC")
        ).join(
            LetterTemplates, EmployeeLetters.TEMPLATE_ID == LetterTemplates.TEMPLATE_ID
        ).join(
            subquery_asc_c, EmployeeLetters.EMP_ID == subquery_asc_c.c.EMP_ID, isouter=True
        ).join(
            subquery_desc, EmployeeLetters.EMP_ID == subquery_desc.c.EMP_ID
        ).options(
            joinedload(EmployeeLetters.employee)
        ).all()
 
        # Serialize the letters and associated employee data
        serialized_letters = []
        for letter, template_name, emp_no_asc_c, emp_no_desc in all_letters:
            if template_name == "Appoinment Letter":
                emp_latest_record = (
                    db.session.query(EmployeeDetails)
                    .filter(EmployeeDetails.EMP_ID == letter.EMP_ID)
                    .filter(EmployeeDetails.EFFECTIVE_START_DATE <= datetime.now())
                    .order_by(EmployeeDetails.EFFECTIVE_START_DATE.asc())
                    .first()
                )
                print("2345",emp_latest_record)
                emp_no = emp_latest_record.EMP_NO if emp_latest_record else None
                print("2345",emp_no)
            else:
                emp_no = emp_no_desc
                print("3456",emp_no)
            serialized_letters.append({
                'CREATED_BY': letter.CREATED_BY,
                'EMP_ID': letter.EMP_ID,
                'LAST_UPDATED_BY': letter.LAST_UPDATED_BY,
                'LETTER_ID': letter.LETTER_ID,
                'LETTER_TYPE': letter.LETTER_TYPE,
                'TEMPLATE_ID': letter.TEMPLATE_ID,
                'EMP_NO': emp_no  # Ensure employee relationship is correctly accessed
            })
 
        return jsonify(serialized_letters), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/getallemptemplates',methods=['GET'])
def getemptemplates():
    return get_employees_templates()
def filter_employee_letters(search_data):
    try:
        # Extract search parameters from the dictionary
        template_id = search_data.get('TEMPLATE_ID')
        emp_no = search_data.get('EMP_NO')
        first_name = search_data.get('FIRST_NAME')
        letter_type = search_data.get('LETTER_TYPE')
        email_address = search_data.get('EMAIL_ADDRESS')
 
        # Build the query with joins and filters
        query = db.session.query(EmployeeLetters, EmployeeDetails).join(EmployeeDetails, EmployeeLetters.EMP_ID == EmployeeDetails.EMP_ID)
 
        if template_id:
            query = query.filter(EmployeeLetters.TEMPLATE_ID == template_id)
        if emp_no:
            query = query.filter(EmployeeDetails.EMP_NO == emp_no)
        if first_name:
            query = query.filter(EmployeeDetails.FIRST_NAME.ilike(f"%{first_name}%"))
        if letter_type:
            query = query.filter(EmployeeLetters.LETTER_TYPE.ilike(f"%{letter_type}%"))
        if email_address:
            query = query.filter(EmployeeDetails.EMAIL_ADDRESS.ilike(f"%{email_address}%"))
 
        # Execute the query and serialize the results
        results = query.all()
        if not results:
            return jsonify({'message': 'No data found for the provided search criteria'}), 404
 
        serialized_results = []
        for letter, emp in results:
            letter_data = letter.serialize()
            emp_data = emp.serialize()
            combined_data = {**letter_data, **emp_data}
            serialized_results.append(combined_data)
 
        return jsonify(serialized_results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
@app.route('/filterEmployees_Letter/<search_data>', methods=['GET'])
def filter_employees_route(search_data):
    # Split the path into segments and map them to parameter names
    search_values = search_data.split('/')
    search_keys = ['TEMPLATE_ID', 'EMP_NO', 'FIRST_NAME', 'LETTER_TYPE', 'EMAIL_ADDRESS']
   
    # Create a dictionary from the keys and values
    search_data_dict = {key: value for key, value in zip(search_keys, search_values) if value}
   
    # Pass the dictionary to the filter function
    return filter_employee_letters(search_data_dict)



@app.route('/download_pdf_by_emp_no/<emp_no>', methods=['GET'])
 
#  http://localhost:5000/download_pdf_by_emp_no/
def download_pdf_by_emp_no(emp_no):
    try:  
        employee = EmployeeDetails.query.filter_by(EMP_NO=emp_no).first()
       
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        letter = EmployeeLetters.query.filter_by(EMP_ID=employee.EMP_ID).order_by(EmployeeLetters.CREATED_AT.desc()).first()
       
        if not letter or not letter.LETTER:
            return jsonify({'error': 'Letter not found or no PDF associated'}), 404
       
        return send_file(
            io.BytesIO(letter.LETTER),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'letter_PRASAD_{letter.LETTER_ID}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def deletetemplate(TEMPLATE_ID, EMP_NO):
    try:
        print("TEMPLATE_ID:", TEMPLATE_ID)
        print("EMP_NO:", EMP_NO)
        
        # Filter by both TEMPLATE_ID and EMP_NO
        template = EmployeeLetters.query.filter_by(TEMPLATE_ID=TEMPLATE_ID).first()
        print("Found template:", template)
        
        if not template:
            return jsonify({'message': 'Template not found'}), 404
        
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({'message': f'Template {TEMPLATE_ID} for employee {EMP_NO} deleted successfully', 
                        'data': template.serialize()}), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/getdeletetemplate/<TEMPLATE_ID>/<EMP_NO>', methods=['DELETE'])
def getdeleteBy(TEMPLATE_ID, EMP_NO):
    return deletetemplate(TEMPLATE_ID, EMP_NO)

@app.route('/get_excel',methods=['GET'])
def get_excel():
    return getexcel1()
       # Fetch ... by Tejaswi Denaboina
 
import os
import pandas as pd
from flask import send_file, jsonify
 
def getexcel1():
    try:
        # Assuming EmployeeDetails is properly defined and imported elsewhere in your code
        empDetails = EmployeeDetails.query.limit(3).all()
        data_list = []
        for emp in empDetails:
            data_list.append({
                'EMP_NO': emp.EMP_NO,
                'EFFECTIVE_START_DATE' : emp.EFFECTIVE_START_DATE,
                'EFFECTIVE_END_DATE' : emp.EFFECTIVE_END_DATE,
                'FIRST_NAME' : emp.FIRST_NAME,
                'MIDDLE_NAME' : emp.MIDDLE_NAME,
                'LAST_NAME' : emp.LAST_NAME,
                'DATE_OF_BIRTH' : emp.DATE_OF_BIRTH,
                # 'JOB_LOCATION' : emp.JOB_LOCATION,
                'WORKER_TYPE' : emp.WORKER_TYPE,
                'WORK_LOCATION': emp.WORK_LOCATION,
                'USER_ID' : emp.USER_ID,
                'EMAIL_ADDRESS' : emp.EMAIL_ADDRESS,
                'CREATED_AT' : emp.CREATED_AT,
                'LAST_UPDATED_AT' : emp.LAST_UPDATED_AT,
            })
 
        df = pd.DataFrame(data_list)
 
        script_dir = os.path.dirname(os.path.abspath(__file__))
 
        # Construct the absolute path to the output Excel file
        excel_file_path = os.path.join(script_dir, 'output.xlsx')
       
        # Export DataFrame to Excel
        df.to_excel(excel_file_path, index=False)
 
        # Send the Excel file as a response
        return send_file(excel_file_path, as_attachment=True, download_name='output.xlsx')
 
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 