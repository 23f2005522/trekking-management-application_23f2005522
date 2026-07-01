from flask import request,Blueprint,render_template,redirect,flash,session
from utils.authentication import *
from model.model import *
admin_bp = Blueprint("admin_routes", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard", methods=["GET"])
@is_logged_in
@role_required(UserRole.ADMIN)
def dashboard():
    if request.method == "GET":
        # fetch adminUser
        admin_user = UserModel.query.filter_by(id=session["user_id"]).first()
        
        # fetch Dashboard stats
        total_trekkers = UserModel.query.filter_by(role=UserRole.TREKKER).count()
        total_staff = UserModel.query.filter_by(role=UserRole.STAFF).count()
        total_bookings = BookingModel.query.count()
        total_treks  = TrekModel.query.count()
                
        # some recent bookings for the dashboard
        fresh_bookings = BookingModel.query.order_by(BookingModel.booking_date.desc()).limit(6).all()
        
         
        return render_template("admin/dashboard.html", admin_user=admin_user , total_trekkers=total_trekkers, total_staff=total_staff, total_bookings=total_bookings, total_treks=total_treks, fresh_bookings=fresh_bookings)

    
    
    
# Mange Staff Routes 
   
@admin_bp.route("/manage_staff" , methods=["GET"])
@is_logged_in
@role_required(UserRole.ADMIN)
def manage_staff():
    if request.method == "GET":
        
        # Fetch all staff members from the database
        staff_members = UserModel.query.filter_by(role = UserRole.STAFF).all()
        
        # pending staff members
        pending_staff_members = [staff for staff in staff_members if staff.staff_profile.Profile_status == StaffStatus.PENDING]
        
        # approved staff members
        approved_staff_members = [staff for staff in staff_members if staff.staff_profile.Profile_status == StaffStatus.APPROVED]
        
        # blacklisted staff members
        blacklisted_staff_members = [staff for staff in staff_members if staff.staff_profile.Profile_status == StaffStatus.BLACKLISTED]
        
        return render_template("admin/manage_staff.html", staff_members=staff_members, pending_staff_members=pending_staff_members, approved_staff_members=approved_staff_members, blacklisted_staff_members=blacklisted_staff_members)

@admin_bp.route("/manage_staff/approve_staff/<int:user_id>" , methods=["POST", "PATCH"])
@is_logged_in
@role_required(UserRole.ADMIN)
def approve_staff(user_id):
    if request.method == "PATCH" or request.method == "POST":
       staff  = UserModel.query.get(user_id) 
       
       if staff and staff.role == UserRole.STAFF:
              staff.is_approved = True
              staff.staff_profile.Profile_status = StaffStatus.APPROVED
              db.session.commit()
              flash("Staff approved successfully.", "success")
              return redirect("/admin/manage_staff")
        
       else:
                flash("Staff not found or not a staff member.", "danger")
                return redirect("/admin/manage_staff")
            
            
    else : 
        flash("Invalid request method.", "danger")
        return redirect("/admin/manage_staff")
            
@admin_bp.route("/manage_staff/reject_staff/<int:user_id>" , methods=["POST", "PATCH"])
@is_logged_in
@role_required(UserRole.ADMIN)
def reject_staff(user_id):
    if request.method == "PATCH" or request.method == "POST":
       staff  = UserModel.query.get(user_id)
       if staff and staff.role == UserRole.STAFF:
              staff.is_approved = False
              staff.staff_profile.Profile_status = StaffStatus.REJECTED
              db.session.commit()
              flash("Staff rejected successfully.", "success")
              return redirect("/admin/manage_staff")
       else:
                flash("Staff not found or not a staff member.", "danger")
                return redirect("/admin/manage_staff")
        
    else : 
        flash("Invalid request method.", "danger")
        return redirect("/admin/manage_staff")   
    