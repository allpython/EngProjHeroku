#################
#### imports ####
#################

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail
import os

################
#### config ####
################

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
mail = Mail(app)

from project.users.views import users_blueprint
from project.home.views import home_blueprint
from project.clients.views import clients_blueprint
from project.products.views import products_blueprint
from project.features.views import features_blueprint

# register our blueprints
app.register_blueprint(home_blueprint)
app.register_blueprint(users_blueprint)
app.register_blueprint(clients_blueprint)
app.register_blueprint(products_blueprint)
app.register_blueprint(features_blueprint)

from project.models import User

login_manager.login_view = "users.login"


@login_manager.user_loader
def load_user(username):
    return User.find_by_username(username)

@app.before_first_request
def create_tables():
    db.create_all()

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
