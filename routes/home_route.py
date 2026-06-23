from flask import Blueprint, render_template, request 


home_bp = Blueprint("home" , __name__)


@home_bp.route("/" , methods  = ["GET"])
def home() : 
    if request.method == "GET":
        return render_template("base.html")    