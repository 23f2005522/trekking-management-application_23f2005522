from flask import render_template


def dashboard():
    return render_template("trekker/dashboard.html")
