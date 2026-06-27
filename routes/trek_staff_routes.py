from flask import request,Blueprint,render_template,redirect,flash,session

trek_staff_bp = Blueprint("trekk_staff_routes", __name__, url_prefix="/trekstaff")


@trek_staff_bp.route("/dashboard")
def dashboard():
    if request.method == "GET":
        return render_template("trekStaff/dashboard.html")