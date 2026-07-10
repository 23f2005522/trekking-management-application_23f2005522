from flask import Blueprint
from utils.authentication import is_logged_in, role_required
from model.model import UserRole
from controller import admin_controller as admin_ctrl

admin_bp = Blueprint("admin_routes", __name__, url_prefix="/admin")

# Dashboard route
@admin_bp.route("/dashboard", methods=["GET"])
@is_logged_in
@role_required(UserRole.ADMIN)
def dashboard():
    return admin_ctrl.dashboard()


# Manage staff route


# show all staff route
@admin_bp.route("/manage_staff", methods=["GET"])
@is_logged_in
@role_required(UserRole.ADMIN)
def manage_staff():
    return admin_ctrl.manage_staff()


# Create staff route
@admin_bp.route("/create_staff", methods=["POST"])
@is_logged_in
@role_required(UserRole.ADMIN)
def create_staff():
    return admin_ctrl.create_staff()


# Approve staff route
@admin_bp.route("/manage_staff/approve_staff/<int:user_id>", methods=["POST", "PATCH"])
@is_logged_in
@role_required(UserRole.ADMIN)
def approve_staff(user_id):
    return admin_ctrl.approve_staff(user_id)

# Reject staff route
@admin_bp.route("/manage_staff/reject_staff/<int:user_id>", methods=["POST", "PATCH"])
@is_logged_in
@role_required(UserRole.ADMIN)
def reject_staff(user_id):
    return admin_ctrl.reject_staff(user_id)

# Blacklist staff route
@admin_bp.route("/manage_staff/blacklist_staff/<int:user_id>", methods=["POST"])
@is_logged_in
@role_required(UserRole.ADMIN)
def blacklist_staff(user_id):
    return admin_ctrl.blacklist_staff(user_id)

# Deblacklist staff route
@admin_bp.route("/manage_staff/deblacklist_staff/<int:user_id>", methods=["POST"])
@is_logged_in
@role_required(UserRole.ADMIN)
def deblacklist_staff(user_id):
    return admin_ctrl.deblacklist_staff(user_id)

# Permanently delete blacklisted staff route
@admin_bp.route("/manage_staff/delete_staff/<int:user_id>", methods=["POST"])
@is_logged_in
@role_required(UserRole.ADMIN)
def delete_staff_permanently(user_id):
    return admin_ctrl.delete_staff_permanently(user_id)

# Manage treks route
@admin_bp.route("/manage_treks", methods=["GET"])
@is_logged_in
@role_required(UserRole.ADMIN)
def manage_treks():
    return admin_ctrl.manage_treks()

# Trek Routes

# Create trek route
@admin_bp.route("/manage_treks/create", methods=["POST"])
@is_logged_in
@role_required(UserRole.ADMIN)
def create_trek():
    return admin_ctrl.create_trek()

# Edit trek route
@admin_bp.route("/edittrek/<int:trek_id>", methods=["GET", "POST"])
@is_logged_in
@role_required(UserRole.ADMIN)
def edit_trek(trek_id):
    return admin_ctrl.edit_trek(trek_id)

# Delete trek route
@admin_bp.route("/manage_treks/delete/<int:trek_id>", methods=["POST"])
@is_logged_in
@role_required(UserRole.ADMIN)
def delete_trek(trek_id):
    return admin_ctrl.delete_trek(trek_id)

# Manage trekkers route

# Deactivate trekker route
@admin_bp.route("/manage_trekkers", methods=["GET"])
@is_logged_in
@role_required(UserRole.ADMIN)
def manage_trekkers():
    return admin_ctrl.manage_trekkers()

# Reactivate trekker route
@admin_bp.route("/manage_trekkers/deactivate/<int:user_id>", methods=["POST"])
@is_logged_in
@role_required(UserRole.ADMIN)
def deactivate_trekker(user_id):
    return admin_ctrl.deactivate_trekker(user_id)

# Manage bookings route
@admin_bp.route("/manage_trekkers/reactivate/<int:user_id>", methods=["POST"])
@is_logged_in
@role_required(UserRole.ADMIN)
def reactivate_trekker(user_id):
    return admin_ctrl.reactivate_trekker(user_id)


@admin_bp.route("/manage_trekkers/blacklist/<int:user_id>", methods=["POST"])
@is_logged_in
@role_required(UserRole.ADMIN)
def blacklist_trekker(user_id):
    return admin_ctrl.blacklist_trekker(user_id)


@admin_bp.route("/manage_trekkers/deblacklist/<int:user_id>", methods=["POST"])
@is_logged_in
@role_required(UserRole.ADMIN)
def deblacklist_trekker(user_id):
    return admin_ctrl.deblacklist_trekker(user_id)


# Bookings route
@admin_bp.route("/bookings", methods=["GET"])
@is_logged_in
@role_required(UserRole.ADMIN)
def manage_bookings():
    return admin_ctrl.manage_bookings()

# Search page route
@admin_bp.route("/search", methods=["GET"])
@is_logged_in
@role_required(UserRole.ADMIN)
def search_page():
    return admin_ctrl.search_page()

# Reports route
@admin_bp.route("/reports", methods=["GET"])
@is_logged_in
@role_required(UserRole.ADMIN)
def generate_report():
    return admin_ctrl.generate_report()
