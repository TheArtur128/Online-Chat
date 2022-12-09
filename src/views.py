from flask import Blueprint, render_template


view_blueprint = Blueprint('views', __name__)


@view_blueprint.route('/')
def index():
    return render_template('index.html')


@view_blueprint.route('/registration')
def registration():
    pass


@view_blueprint.route('/login')
def authorization():
    pass