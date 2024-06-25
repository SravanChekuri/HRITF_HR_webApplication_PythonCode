
from flask import Flask, request, jsonify
import mysql.connector
from model.LetterTemplates import *
from datetime import date, datetime
from flask import make_response
import io  
import comtypes.client
import pdfkit
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
import os
import base64
import tempfile
from flask import send_file
import pythoncom
import win32com.client
import mimetypes
from mimetypes import guess_type


# def uploadTemplate():
#     try:
#         created_By = 'HR'
#         Last_Updated_By = 'HR'
#         filename = request.form['Filename']
    
#         if 'File' not in request.files:
#             return 'No file part'
 
#         file = request.files['File']
#         if file.filename == '':
#             return 'No selected file'
 
#         # Read RTF file into memory
#         pdf_data = file.read()
 
#         # Save RTF file to the database
#         new_pdf = LetterTemplates(TEMPLATE_NAME=filename, 
#         FILE_SIZE=len(pdf_data), 
#         TEMPLATE_TYPE=file.mimetype, 
#         TEMPLATE=pdf_data, 
#         CREATED_BY=created_By, 
#         LAST_UPDATED_BY=Last_Updated_By)
#         db.session.add(new_pdf)
#         db.session.commit()

#         return jsonify({'message': 'File uploaded successfully'}), 200
#     except Exception as e:
#         print(f"Error: {e}")
#         return jsonofy({'error': {e}}), 500

def uploadTemplate():
    try:
        created_By = 'HR'
        Last_Updated_By = 'HR'
        filename = request.form['Filename']
    
        if 'File' not in request.files:
            return 'No file part'
 
        file = request.files['File']
        if file.filename == '':
            return 'No selected file'
 
        # Read RTF file into memory
        pdf_data = file.read()

        dbdata = LetterTemplates.query.all()
        checkFile = LetterTemplates.query.filter_by(TEMPLATE_NAME=filename).first()
        print("checkFile",checkFile)
        if checkFile:

            checkFile.TEMPLATE_ID = checkFile.TEMPLATE_ID
            checkFile.TEMPLATE_NAME = checkFile.TEMPLATE_NAME
            checkFile.FILE_SIZE=len(pdf_data)
            checkFile.TEMPLATE_TYPE = file.mimetype
            checkFile.TEMPLATE = pdf_data
            db.session.commit()
            return jsonify({'message': 'Template updated successfully', "data": checkFile.serialize() }), 200

        else:
            temp = []
            for i in dbdata:
                temp.append(i.TEMPLATE_ID[6:])
            if not dbdata:
                Id = 'LETTER10001'
                new_pdf = LetterTemplates(
                    TEMPLATE_ID = Id,
                    TEMPLATE_NAME=filename, 
                    FILE_SIZE=len(pdf_data), 
                    TEMPLATE_TYPE=file.mimetype, 
                    TEMPLATE=pdf_data, 
                    CREATED_BY=created_By, 
                    LAST_UPDATED_BY=Last_Updated_By)
                    
                    
            else:
                a = max(temp)
                print("max(temp+1)",type(a),int(max(temp))+1)
                new_pdf = LetterTemplates(
                    TEMPLATE_ID = 'LETTER'+str(int(max(temp))+1),
                    TEMPLATE_NAME=filename, 
                    FILE_SIZE=len(pdf_data), 
                    TEMPLATE_TYPE=file.mimetype, 
                    TEMPLATE=pdf_data, 
                    CREATED_BY=created_By, 
                    LAST_UPDATED_BY=Last_Updated_By)

            db.session.add(new_pdf)
            db.session.commit()

            return jsonify({'message': f'{filename} Template added successfully', "data": new_pdf.serialize()}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': {e}}), 500



def temp(TEMPLATE_ID):
    try:
        temp = LetterTemplates.query.get(TEMPLATE_ID)
        print("Template_name",temp)
 
        file_obj = BytesIO(temp.TEMPLATE)
       
 
    # Return the file as a response
        return send_file(file_obj, mimetype=temp.TEMPLATE_TYPE)
    except Exception as e:
        return jsonify({'error':str(e)}),500

def gettemplate():
    data =LetterTemplates.query.all()
    print(data)
    returnData= []
    for i in data:
        returnData.append(i.serialize())
    print('returnData',returnData)
    return returnData


# def updatetemplate(id):
#     try:
#         filename = request.form['Filename']

#         file = request.files['File']

#             # Read RTF file into memory
#         pdf_data = file.read()

#         # Retrieve the template from the database based on TEMPLATE_ID
#         template = LetterTemplates.query.get(id)
#         if not template:
#             return jsonify({'error': 'Template not found'}), 404

#         # Update template attributes
#         template.TEMPLATE_NAME = filename
#         template.TEMPLATE = pdf_data
#         # Commit changes to the database
#         db.session.commit()
#         return jsonify({'message': 'Template updated successfully'}), 200
#     except Exception as e:
#         print(f"Error: {e}")
#         return jsonify({'error': str(e)}), 500





def gettemplatea():
    try:
        returndata =[]
        get = LetterTemplates.query.all()
        print("get",get)
        if not get:
            return jsonify({"error":"templates not found"}),400
        for i in get:
            print("i",i)
            returndata.append(i.serialize())
        return jsonify({'data': returndata}),200
    except Exception as e:
        return jsonify({'error':str(e)}),500
    
def convertrtf(TEMPLATE_ID):
    try:
        temp = LetterTemplates.query.filter(LetterTemplates.TEMPLATE_ID==TEMPLATE_ID).one()
        print("temp",temp)
        x = temp.TEMPLATE
        print("x",x)
       
        file_obj = BytesIO(x)
 
        rtf_file_name = 'rtffile.rtf'
        pdf_file_name = 'pdffile.pdf'
        rtf_file_path = os.path.join(os.getcwd(), rtf_file_name)
        print("rtf_file_path",rtf_file_path)
        with open(rtf_file_path, 'wb') as file:
                file.write(file_obj.read())
 
        pythoncom.CoInitialize()
        word = win32com.client.Dispatch("Word.Application")
        doc = word.Documents.Open(rtf_file_path)
       
        pdfpath = os.path.join(os.getcwd(), pdf_file_name)
        doc.SaveAs(pdfpath, FileFormat=17)
        print("pdfpath",pdfpath)
        doc.Close()
        word.Quit()
        pythoncom.CoUninitialize()
        os.remove(rtf_file_path)
 
        with open ('c:pdffile.pdf','rb') as file:
            a = file.read()
 
        file_obj = BytesIO(a)
        mimetype = mimetypes.MimeTypes().guess_type(pdf_file_name)[0]
        os.remove(pdfpath)
    # Return the file as a response
        return send_file(file_obj, mimetype=mimetype)    
    except Exception as e:
        return jsonify({'error':str(e)}),500
# convertpdf @app.route('/convert_rtf/<stri... by Chandrakala Nallamilli
@app.route('/letter-templatesname/<template_name>', methods=['GET'])
def get_letter_template_by_name(template_name):
    letter_template = LetterTemplates.query.filter_by(TEMPLATE_NAME=template_name).first()
    if not letter_template:
        return jsonify({'error': 'Letter template not found'}), 404
    response = {
        'TEMPLATE_ID': letter_template.TEMPLATE_ID
    }
 
    return jsonify(response), 200
def gettemplate():
    data = LetterTemplates.query.all()
    print(data)
    returnData= []
    for i in data:
        returnData.append(i.serialize())
    print('returnData',returnData)
    return returnData