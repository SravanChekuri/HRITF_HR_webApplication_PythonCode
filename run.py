from app import app

if __name__=='__main__':
    # app.run(debug=True)
    app.run(debug=True, host='localhost', threaded=True)
