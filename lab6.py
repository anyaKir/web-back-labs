from flask import Blueprint, request, render_template, session, redirect, current_app, url_for

lab6 = Blueprint('lab6', __name__)

@lab6.route('/lab6/')
def main():
    return render_template('lab6/lab6.html')