#################
#### imports ####
#################

from flask import redirect, render_template, request, url_for, Blueprint, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from .forms import LoginForm, RegisterForm, EmailForm, ResetPasswordForm
from project import app, db
from project.models import User
from project.utils import helper
from itsdangerous import URLSafeTimedSerializer

################
#### config ####
################

users_blueprint = Blueprint(
    'users', __name__,
)


################
#### routes ####
################

@users_blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if User.find_by_username(username=form.username.data):
            return render_template('register.html', form=form, error="User already exits")
        elif User.find_by_email(email=form.email.data):
            return render_template('register.html', form=form, error="User Already exists")

        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('features.feature_request'))
    return render_template('register.html', form=form)

@users_blueprint.route("/login", methods=["GET", "POST"])
def login():
    #from IPython import embed; embed()
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                session['user_id'] = current_user.username
                return redirect(url_for('features.feature_request'))
        return render_template('login.html', form=form, message="Invalid username or password")

    return render_template('login.html', form=form)

@users_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    session['user_id'] = None
    return redirect(url_for('home.root'))

@users_blueprint.route('/forgotPassword', methods=["GET", "POST"])
def forgotPassword():
    form = EmailForm()
    errors = []
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
        except:
            return render_template('forgot_password.html', form=form, message="Invalid email address!")

        if user:
            errors = send_password_reset_email(user.email)
            if len(errors) == 0:
                return render_template('forgot_password.html', form=form, message="Check your email for password reset link")
            else:
                return render_template('forgot_password.html', form=form, message="An Error Occured. Try again in a while.")
        else:
            return render_template('forgot_password.html', form=form, message="User does not exists!")

    return render_template('forgot_password.html', form=form)


@users_blueprint.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    from IPython import embed; embed()
    try:
        password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = password_reset_serializer.loads(token, salt='password-reset-salt', max_age=1800)
    except:
        return render_template('login.html', form=LoginForm(), message="Password reset link is invalid or has expired!")

    form = ResetPasswordForm()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=email).first()
        except:
            return render_template('login.html', form=LoginForm(), message="Invalid Email!")

        user.password = generate_password_hash(form.password.data, method='sha256')
        db.session.add(user)
        db.session.commit()

        return render_template('login.html', form=LoginForm(), message="Your Password has been reset!")

    return render_template('reset_password_with_token.html', form=form, token=token)

def send_password_reset_email(user_email):
    password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    password_reset_url = url_for(
        'users.reset_with_token',
        token = password_reset_serializer.dumps(user_email, salt='password-reset-salt'),
        _external=True)

    html = render_template(
        'email_password_reset.html',
        password_reset_url=password_reset_url)

    return helper.send_email('Password Reset Requested', [user_email], html)
