#################
#### imports ####
#################
from flask import redirect, render_template, request, url_for, Blueprint
from flask_login import login_required, current_user

from project import db

################
#### config ####
################

home_blueprint = Blueprint(
    'home', __name__,
)


################
#### routes ####
################

# use decorators to link the function to a url
@home_blueprint.route("/")
def root():
    if current_user.is_authenticated:
        return redirect(url_for('features.feature_request'))
    return render_template('index.html')

@home_blueprint.route("/home")
@login_required
def home():
    return redirect(url_for('features.feature_request'))
    #return render_template('home.html')
