from flask import Flask
from db.db import db  
from config.config import Config
from model.model import *  # importing models before they are creating database tables inside the app context 


#  Routes (Blueprints)
from routes.home_route import home_bp




#creating app
app = Flask(__name__, template_folder="templates", static_folder="static") 
# configuration of using Config class from config.py
app.config.from_object(Config) 
# db.init_app(app) 



#AutoCreation DB_tables and Admin if not present
# with app.app_context() : 
#     db.create_all() 
    
     

   



#registering the All routes(Blueprints) to the APP here
app.register_blueprint(home_bp)


    
    
    
    

if (__name__ == "__main__") :
    app.run(debug = True) 
    