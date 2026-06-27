from flask import request, flash, redirect, url_for, session
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

    def wrapper(*args , **kwargs): 
        # kwargs is used to pass keyworded, variable-length argument dictionary to the function. It allows you to handle named arguments that you have not defined in advance.
        # and args is used to pass a variable-length argument list to the function. It allows you to handle positional arguments that you have not defined in advance.

        # user is logged in  ?
        if "user_id" not in session:
            flash("Please log in to access this page.", "danger")
            return redirect("/auth/login")
        
        # if its a valid user, check if the user exists in the database
        user = UserModel.query.filter_by(id=session["user_id"]).first()
        if not user:
            flash("User not found.", "danger")
            return redirect("/auth/login")

        # User is logged in, call the original route
        return func(
            *args,
            **kwargs
        )

    # Preserve original function metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__module__ = func.__module__

    return wrapper


def role_required(required_role):
    """
    role_required is a decorator that checks if the logged-in user has the required role to access a specific route.

    useExample:
        @role_required('admin' or UserRole.ADMIN (enums))
        @app.route('/admin')
        def admin_dashboard():
            return render_template('admin_dashboard.html')


    """

    def outer_wrapper(func):

        def inner_wrapper(*args, **kwargs):

            # check if the user in Logged in

            if "user_id" not in session:
                flash("Please log in to access this page.", "danger")
                return redirect("/auth/login")

            # get the logged-in user
            user = UserModel.query.filter_by(id=session["user_id"]).first()

            # if user not found in the database
            if not user:
                flash("User not found.", "danger")
                return redirect("/auth/login")

            # check if the user has the required role
            if user.role != required_role:
                flash("You do not have permission to access this page.", "danger")
                return redirect("/auth/login")  # Redirecting to safe page [home page]

            return func(*args, **kwargs)
        
        
        # Preserve original function metadata
        inner_wrapper.__name__ = func.__name__
        inner_wrapper.__doc__ = func.__doc__
        inner_wrapper.__module__ = func.__module__

        return inner_wrapper



    return outer_wrapper
