from flask import request,Blueprint,render_template,redirect,flash,session

admin_bp = Blueprint("admin_routes", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard", methods=["GET"])
def dashboard():
    if request.method == "GET":
        return render_template("admin/dashboard.html")