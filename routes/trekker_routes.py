from flask import request,Blueprint,render_template,redirect,flash,session

trekker_bp = Blueprint("trekker_routes", __name__, url_prefix="/trekker")


@trekker_bp.route("/dashboard")
def dashboard():
    if request.method == "GET":
        return render_template("trekker/dashboard.html")