

from flask  import Flask
from flask_cors import CORS 

app=Flask(__name__)

from app import view

cors=CORS(app, supports_credentials=True)




import config
