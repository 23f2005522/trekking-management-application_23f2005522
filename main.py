from flask import Flask
from db.db import db  
from config.config import Config
from flask_migrate import Migrate
from db.seed_data import master_seed

#  Routes (Blueprints)
from routes.home_route import home_bp




#creating app
app = Flask(__name__, template_folder="templates", static_folder="static") 
# configuration of using Config class from config.py
app.config.from_object(Config) 
db.init_app(app) 

migrate = Migrate(app, db)  # creating migration object to handle migrations

#AutoCreation DB_tables and Admin if not present
with app.app_context() : 
    from model.model import *  # importing models before creating database tables inside the app context 
    db.create_all() 

    master_seed()  
    
     

   



#registering the All routes(Blueprints) to the APP here
app.register_blueprint(home_bp)


    
    
    
    

if (__name__ == "__main__") :
    app.run(debug = True) 
    