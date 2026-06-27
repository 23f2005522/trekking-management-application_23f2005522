from flask import request , flash , redirect , url_for , session 
from functools import wraps
from model.model import *



def is_logged_in(func):
    """
    Checks whether the user is logged in before allowing access
    to the decorated route.
    
    useExample:
        @is_logged_in
        @app.route('/dashboard')
        def dashboard():
            return render_template('dashboard.html')
    """

    def wrapper(*args):

        #user is logged in  ? 
        if "user_id" not in session:
            flash("Please log in to access this page.", "danger")
            return redirect("/login")

        # User is logged in, call the original route
        return func(*args,)

    return wrapper

def role_required(required_role) : 
    """
        role_required is a decorator that checks if the logged-in user has the required role to access a specific route.
        
        useExample:
            @role_required('admin' or UserRole.ADMIN (enums))
            @app.route('/admin')    
            def admin_dashboard():
                return render_template('admin_dashboard.html')

    
    """
    def outer_wrapper(func) : 
        
        def inner_wrapper(*args):
            
            # check if the user in Logged in
            
            if "user_id" not in session:
                flash("Please log in to access this page.", "danger")
                return redirect("/login")
            
            # get the logged-in user
            user = UserModel.query.filter_by(id=session["user_id"]).first()
            
            #if user not found in the database
            if not user:
                flash("User not found.", "danger")
                return redirect("/login")
            
            # check if the user has the required role
            if user.role != required_role:
                flash("You do not have permission to access this page.", "danger")
                return redirect("/")  # Redirecting to safe page [home page]
            
            
            return func(*args)
        
        return inner_wrapper
    
    return outer_wrapper