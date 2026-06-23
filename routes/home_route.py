from flask import Blueprint, render_template, request 


home_bp = Blueprint("home" , __name__) # BLueprint is a method to organize a group of related routes and other functionality in a Flask application. It allows you to create modular components that can be easily reused and registered with the main application.
# syntax-Menaning of line : 
# home_bp = Blueprint("home" , __name__)
#  menaing of home_bp = Blueprint("home" , __name__) :
# home_bp : This is the name of the Blueprint object being created. It is a variable that will hold the Blueprint instance. You can choose any valid variable name for this, but "home_bp" is a common convention to indicate that this Blueprint is related to the "home" functionality of the application.
# Blueprint("home" , __name__) : This is the constructor for creating a new Blueprint

 

@home_bp.route("/" , methods  = ["GET"])
def home() : 
    if request.method == "GET":
        return render_template("index.html")    