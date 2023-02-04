from flask import Flask, Config
from flask_middlewares import MultipleMiddlewareRegistrar
from flask_migrate import Migrate
from flask_pack import config_from

from api import api_blueprint
from orm import db
from views import view_blueprint


app = Flask(__name__)
app.config.from_object("config")

app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(view_blueprint)

db.init_app(app)
migrate = Migrate(app, db)

middleware_config = config_from("middlewares.config")

MultipleMiddlewareRegistrar.from_config(middleware_config).init_app(app)

if __name__ == "__main__":
    app.run(port='8048')
