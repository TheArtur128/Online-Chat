from flask import Blueprint, render_template


view_blueprint = Blueprint('views', __name__)


@view_blueprint.route('/')
def index():
    return render_template('index.html')
