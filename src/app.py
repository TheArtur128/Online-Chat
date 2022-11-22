from flask import Flask, render_template
from flask_migrate import Migrate

from api import api_blueprint
from models import db
from views import view_blueprint


app = Flask(__name__)
app.config.from_object('config')

app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(view_blueprint)

db.init_app(app)

migrate = Migrate(app, db)


if __name__ == '__main__':
    app.run(port='8048')
