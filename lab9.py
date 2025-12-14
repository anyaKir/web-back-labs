from flask import Blueprint, url_for, request, redirect, render_template, abort
lab9 = Blueprint('lab9', __name__)


@lab9.route('/lab9/')
def lab():
    return render_template('lab9/index.html')
