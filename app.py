from flask import Flask, request, url_for, render_template, redirect, session, abort, jsonify, json, Response
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret_key'

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

@login_manager.user_loader
def load_user(username):
    return User.find_by_username(username)

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(50), nullable=False)
    features = db.relationship('FeatureRequest', backref='client', lazy=True)

    def __init__(self, client_name):
        self.client_name = client_name

    def to_json(self):
        features = FeatureRequest.query.filter_by(client_id=self.id).all()
        features_json = []
        for feature in features:
            features_json.append(feature.to_json())
        return {
            "id": self.id,
            "clientName": self.client_name,
            "features": features_json
        }
    def copy_values(self, client):
        self.client_name = client.client_name

    @classmethod
    def from_json(cls, jsonStr):
        client_name = jsonStr.get('clientName')
        return cls(client_name=client_name)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_area = db.Column(db.String(30), nullable=False)
    features = db.relationship('FeatureRequest', backref='product', lazy=True)

    def __init__(self, product_area):
        self.product_area = product_area

    def to_json(self):
        return {
            "id": self.id,
            "productArea": self.product_area
        }
    def copy_values(self, product):
        self.product_area = product.product_area

    @classmethod
    def from_json(cls, jsonStr):
        product_area = jsonStr.get('productArea')
        return cls(product_area=product_area)

class FeatureRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    description = db.Column(db.Text)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    priority = db.Column(db.Integer)

    def __init__(self, title, description, client_id, product_id, priority):
        self.title = title
        self.description = description
        self.client_id = client_id
        self.product_id = product_id
        self.priority = priority

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "client": self.client.client_name,
            "product": self.product.product_area
        }

@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/")
def root():
    if current_user.is_authenticated:
        return redirect(url_for('feature_request'))
    return render_template('index.html')

@app.route("/home")
@login_required
def home():
    return redirect(url_for('feature_request'))
    #return render_template('home.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                session['user_id'] = current_user.username
                return redirect(url_for('feature_request'))
        return render_template('login.html', form=form, message="Invalid username or password")

    return render_template('login.html', form=form)

@app.route("/register", methods=["GET", "POST"])
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
        return redirect(url_for('feature_request'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session['email'] = None
    return redirect(url_for('root'))

@app.route("/clients")
@login_required
def clients_base():
    clients = Client.query.order_by(Client.id).all()
    return render_template('clients.html', clients=clients)

@app.route("/products")
@login_required
def products_base():
    products = Product.query.order_by(Product.id).all()
    return render_template('products.html', products=products)

@app.route("/product/<int:id>", methods=["GET", "POST"])
@login_required
def get_product(id):
    product = Product.query.get(id)
    #client = [client for client in clients if client.client_id == id][0]
    if product:
        if request.method == 'POST':
            product.product_area = request.form['productArea']
            db.session.add(product)
            db.session.commit()
    return redirect(url_for('products_base'))

@app.route("/product/delete/<int:id>")
@login_required
def delete_product(id):
    product = Product.query.get(id)
    if product:
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('products_base'))

@app.route("/product/edit/<int:id>")
@login_required
def edit_product(id):
    product = Product.query.get(id)
    if product:
        return render_template('create_products.html', product=product)
    return redirect(url_for('products_base'))


@app.route("/product/new", methods=["GET", "POST"])
@login_required
def new_product():
    if request.method == 'POST':
        product_area = request.form['productArea']
        new_product = Product(product_area)

        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('products_base'))
    return render_template('create_products.html')

@app.route("/client/<int:id>", methods=["GET", "POST"])
@login_required
def get_client(id):
    client = Client.query.get(id)
    #client = [client for client in clients if client.client_id == id][0]
    if client:
        if request.method == 'POST':
            client.client_name = request.form['name']
            db.session.add(client)
            db.session.commit()
            return redirect(url_for('get_client', id=client.id))
        return render_template('show_client.html', client=client)
    return redirect(url_for('clients_base'))


@app.route("/client/delete/<int:id>")
@login_required
def delete_client(id):
    client = Client.query.get(id)
    if client:
        db.session.delete(client)
        db.session.commit()
    return redirect(url_for('clients_base'))

@app.route("/client/edit/<int:id>")
@login_required
def edit_client(id):
    client = Client.query.get(id)
    if client:
        return render_template('create_clients.html', client=client)
    return redirect(url_for('clients_base'))

@app.route("/client/new", methods=["GET", "POST"])
@login_required
def new_client():
    if request.method == 'POST':
        client_name = request.form['name']
        new_client = Client(client_name)

        db.session.add(new_client)
        db.session.commit()

        return redirect(url_for('clients_base'))
    return render_template('create_clients.html')

@app.route("/featureRequest", methods=["GET", "POST"])
@login_required
def feature_request():
    if request.method == 'POST':
        #from IPython import embed; embed()
        title = request.form['title']
        description = request.form['description']
        client_id = request.form['client']
        product_id = request.form['product']
        priority = request.form['priority']
        exis_feature = FeatureRequest.query.filter_by(title=title).filter_by(client_id=client_id).filter_by(product_id=product_id).first()
        if exis_feature:
            return redirect(url_for('get_client', id=client_id))
        features_list = FeatureRequest.query.filter_by(client_id=client_id).filter_by(product_id=product_id).order_by(priority).all()

        flag = False
        for feature in features_list:

            if feature.priority == int(priority):
                flag = True
            if flag:
                feature.priority = feature.priority+1
                db.session.add(feature)
                db.session.commit()

        feature = FeatureRequest(title=title, description=description, client_id=client_id, product_id=product_id, priority=priority)
        db.session.add(feature)
        db.session.commit()


        return redirect(url_for('get_client', id=client_id))

    clients = Client.query.order_by(Client.id).all()
    products = Product.query.order_by(Product.id).all()
    return render_template('feature_request.html', clients=clients, products=products)

@app.route("/feature/<int:id>", methods=["GET", "POST"])
@login_required
def get_feature(id):
    feature = FeatureRequest.query.get(id)
    #client = [client for client in clients if client.client_id == id][0]
    if feature:
        if request.method == 'POST':
            feature.title = request.form['title']
            feature.description = request.form['description']
            feature.client_id = request.form['client']
            feature.product_id = request.form['product']
            feature.priority = request.form['priority']

            db.session.add(feature)
            db.session.commit()
            return redirect(url_for('get_client', id=feature.client_id))

        clients = Client.query.order_by(Client.id).all()
        products = Product.query.order_by(Product.id).all()
        return render_template('show_feature.html', clients=clients, products=products, feature=feature)
    return redirect(url_for('home'))

@app.route("/feature/delete/<int:id>")
def delete_feature(id):
    feature = FeatureRequest.query.get(id)
    if feature:
        db.session.delete(feature)
        db.session.commit()
        return redirect(url_for('get_client', id=feature.client_id))
    return redirect(url_for('home'))

@app.route("/features")
@login_required
def features():
    features = FeatureRequest.query.order_by(FeatureRequest.id).all()
    return render_template("features.html", features=features)

@app.route('/api/v1/clients')
@login_required
def list_clients():
    return get_items_list(Client)

@app.route('/api/v1/client/save', methods=['POST'])
@login_required
def add_or_update_client():
    #from IPython import embed; embed()
    return add_or_update_items(Client, request)


@app.route('/api/v1/client/delete/<int:id>')
@login_required
def delete_client_v1(id):
    return delete_item(Client, id)

@app.route('/api/v1/products')
@login_required
def list_products():
    return get_items_list(Product)

@app.route('/api/v1/product/save', methods=['POST'])
@login_required
def add_or_update_product():
    #from IPython import embed; embed()
    return add_or_update_items(Product, request)

@app.route('/api/v1/product/delete/<int:id>')
@login_required
def delete_product_v1(id):
    return delete_item(Product, id)

"""
@app.route('/api/v1/client/<int:id>')
@login_required
def get_client(id):
    return get_item(Client, id)

@app.route("/v1/clients")
@login_required
def clients():
    #clients_json = json.dumps([ob.json() for ob in clients])
    #from IPython import embed; embed()
    response =  jsonify({'clients': list(map(lambda x: x.to_json(), Client.query.order_by(Client.id).all()))})
    response.status_code = 200
    return response
"""
def response(**kwargs):
    result = {}
    result['json'] = kwargs.get('json', [])
    result['total'] = kwargs.get('total', len(result['json']))
    result['messages'] = kwargs.get('messages', [])
    result['success'] = kwargs.get('success', len(result.get('messages')) == 0)
    status = kwargs.get('status', 200)
    result['status'] = status
    mimetype = kwargs.get('mimetype', 'application/json')

    data = json.dumps(result)

    resp = Response(None, status=status, mimetype=mimetype)
    resp.data = data
    return resp

def get_items_list(cls):
    #from IPython import embed; embed()
    items = cls.query.all()
    json = []
    for item in items:
        json.append(item.to_json())
    return response(json=json)


def add_or_update_items(cls, request):
    messages = []
    try:
        #from IPython import embed; embed()
        items = json.loads(request.data.decode('utf-8'))
        for item in items['list']:
            save_item(cls, item)
    except Exception as e:
        messages.append(e)

    if len(messages) > 0:
        return response(status=500, messages=messages)
    return response()


def save_item(cls, item):
    #from IPython import embed; embed()
    obj = None
    if 'id' in item:
        obj = cls.query.filter_by(id=item.get('id')).first()
        obj.copy_values(cls.from_json(item))
    if obj is None:
        obj = cls.from_json(item)

    try:
        db.session.add(obj)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

def get_item(cls, item_id):
    item = cls.query.filter_by(id=item_id).first()
    if item is None:
        abort(404)
    json = []
    json.append(item.to_json)
    return response(json=json)


def delete_item(cls, item_id):
    item = cls.query.filter_by(id=item_id).first()
    if item is None:
        abort(404)
    db.session.delete(item)
    db.session.commit()
    return response(success=True)


if __name__ == '__main__':
    app.run()
