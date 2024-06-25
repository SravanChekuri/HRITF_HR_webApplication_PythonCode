from app import app

from Controller.UserDetaliesController import *
from Controller.employeController import *
from Controller.EmployementDetaliesController import *
from Controller.empAddrController import *
from Controller.LetterTemplateController import *
from Controller.EmployeeLettersController import *

#REGISTER DETAILS
@app.route('/register',methods=['POST'])
def register():
    return register_data()

#LOGIN DETAILS
@app.route('/login',methods=['POST'])
def login():
    return login_user()

#register get method
@app.route('/getregister',methods=['GET'])
def getregister():
    return getemployee()
# @app.route('/getallemployees',methods=['GET'])
# def getemp():
#     return getemployees()


#register id get  method
@app.route('/getbyId/<USER_ID>',methods=['GET'])
def getById(USER_ID):
    print(type(USER_ID))
    return getemployeeId(USER_ID)

#register delete method
@app.route('/getdeleteid/<USER_ID>',methods=['DELETE'])
def getdeleteById(USER_ID):
    return deleteemployee(USER_ID)

#register update method
@app.route('/updateid/<USER_ID>',methods=['PUT'])
def updateid(USER_ID):
    return updateemployee(USER_ID)


# #register update method
# @app.route('/updateemployee/<EMP_ID>',methods=['PUT'])
# def updateemp(EMP_ID):
#     return updateemployees(EMP_ID)

#Forgetting Password
@app.route('/forgetpassword', methods=['POST'])
def forget_password():
    return forgetpassword()
 
 
#verify otp
@app.route('/verifyotp', methods=['POST'])
def verify_otp():
    return verifyotps()
 
 
##newpassword
@app.route('/newpassword', methods = ['PUT'])
def new_password():
    return newpassword()

############
###register add employees
@app.route('/registeremployee', methods=['POST'])
def register_employee():
    print("registeremp")
    return register_employee_data()

###update or edit employees
@app.route('/editemployee/<int:id>', methods=['PUT'])
def edit_employee(id):
    print("editemp")
    return editemployee(id)

##upload excel sheet
@app.route('/uploadexcel', methods=['POST'])
def upload():
    return upload_excel()


##filterData
@app.route('/filterEmployees/<search_data>',methods=['GET'])
def fillters(search_data):
    return filter_employees(search_data)

# #register get method
@app.route('/getallemployees',methods=['GET'])
def getemployees():
    return get_employees_all()

# #register id get  method
# @app.route('/getlatestemployeedetails/<EMP_ID>',methods=['GET'])
# def getlatestemployeedetails(EMP_ID):
#     print(type(EMP_ID))
#     return get_latest_employee_details(EMP_ID)



############## LetterTemplate
### upload rtf file
@app.route('/uploadTemplate', methods=['POST'])
def upload_Template():
    return uploadTemplate()


# #### update template
# @app.route('/update_template/<int:id>', methods = ['PUT'])
# def update_Template(id):
#     return updatetemplate(id)

####retrieve rtf template
@app.route('/retrieve_template/<string:Id>', methods=['GET'])
def retrieve_template(Id):
    print("data")
    return temp(Id)

####retrieve all templates
@app.route('/gettemplate',methods=['GET'])
def gettemplates():
    return gettemplate()

# convertpdf
@app.route('/convert_rtf/<string:Id>', methods=['GET'])
def convert_rtf(Id):
    print("sdfghjgvyvb")
    return convertrtf(Id)
 


 

###########Employment
@app.route('/add_employment_details', methods=['POST'])
def add_employment_detailss():
    print("fghjkl;kjh")
    return add_employment_details()



# get employeedetails
# @app.route('/get_employee_details/<id>/<date>', methods=['GET'])
# def get_Employeedetails(id,date):
#     print("getemp",date)
#     return getEmployeedetails(id,date)
@app.route('/get_employee_details/<id>/<date>/<enddate>', methods=['GET'])
def get_Employeedetails(id,date,enddate):
    print("getemp",date)
    return getEmployeedetails(id,date,enddate)

# @app.route('/Search_employee_details/<emp>/<date>/<enddate>', methods=['GET'])
@app.route('/Search_employee_details/<emp>/<date>', methods=['GET'])
def Search_Employeedetails(emp,date):
    print("Employeedetails")
    return SearchEmployeedetails(emp,date)

# get recent record of employee by id
@app.route('/get_emp_detail/<id>', methods=['GET'])
def get_Empdetails(id):
    return getEmpdetails(id)
@app.route('/Search_employee_details/<emp>/<date>/<enddate>', methods=['GET'])
def Search_Employeedetailss(emp,date,enddate):
    print("Employeedetails")
    return SearchEmployeedetailss(emp,date,enddate)
# get all employees
@app.route('/get_emp_details', methods=['GET'])
def get_Employee():
    print("getemp")
    return getEmployee()
@app.route('/get_template_details', methods=['GET'])
def get_template():
    print("getemp")
    return gettemplate()
@app.route('/get_templatesby/<TEMPLATE_ID>', methods=['GET'])
def get_templatess(TEMPLATE_ID):
    return get_temployeeId(TEMPLATE_ID)
@app.route('/get_templateees',methods=['GET'])
def get_templateee():
    print("2345678")
    return gettemplatea()
# @app.route('/get_employement_details/<id>', methods=['GET'])
# def get_Employeement(id):
#     # print("dxfghjkl")
    # return getEmployementdetails(id)
 
# @app.route('/get_employement_detail/<id>/<date>', methods=['GET'])
# def get_Employementdetail(id,date):
#     return getEmployementdetail(id,date)
# @app.route('/get_employement_detail/<id>/<date>/<enddate>', methods=['GET'])
# def get_Employementdetail(id,date,enddate):
#     print("getEmployementdetail")
#     return getEmployementdetail(id,date,enddate)
@app.route('/getdetailss/<emp>/<ESD>/<EDD>', methods=['GET'])
def get_latest_recordss(emp, ESD, EDD):
    return get_latest_records(emp, ESD, EDD)


@app.route('/set_session', methods=['POST'])
def set_session():
    session.permanent_session_lifetime = timedelta(days=1)
    session.permanent = True

    data = request.get_json()
    session['user_id'] = data.get('user_id')
   
    print("session",session)
    return jsonify({'message': 'Session set successfully'}), 200



@app.route('/get_session', methods=['GET'])
def get_session():
    print("session",session)
    user_id = session.get('user_id')
    if user_id:
        return jsonify({'user_id': user_id}), 200
    else:
        return jsonify({'message': 'No session found'}), 404




##empaddres
 
@app.route('/add_employment_address/<int:id>', methods=['POST'])
def add_employment_address(id):
    return add_employee_address(id)
 

  
@app.route('/filess',methods=['POST'])
def filess():
    print("cvbnm,")
    return file_convert()