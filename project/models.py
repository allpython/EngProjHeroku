from project import app, db
from flask_login import UserMixin
from datetime import datetime, date
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

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

    def generate_auth_token(self, expiration=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'user': self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        id = data.get('user')
        if id:
            return User.query.get(id)
        return None

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(50), nullable=False)
    features = db.relationship('FeatureRequest', backref='client', lazy=True)

    def __init__(self, client_name):
        self.client_name = client_name

    def to_json(self):
        features = FeatureRequest.query.filter_by(client_id=self.id).order_by(FeatureRequest.priority).all()
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
    target_date = db.Column(db.Date, nullable=False, default=datetime.now().date().strftime('%Y-%m-%d'))

    def __init__(self, title, description, client_id, product_id, priority, target_date):
        self.title = title
        self.description = description
        self.client_id = client_id
        self.product_id = product_id
        self.priority = priority
        self.target_date = target_date

    @classmethod
    def from_json(cls, jsonStr):
        title = jsonStr.get('title')
        description = jsonStr.get('description')
        priority = jsonStr.get('priority')
        client_id = jsonStr.get('clientId')
        product_id = jsonStr.get('productId')
        target_date = datetime.strptime(jsonStr.get('targetDate'), '%Y-%m-%d')
        return cls(title=title, description=description, priority=priority,
        client_id=client_id, product_id=product_id, target_date=target_date)

    def copy_values(self, feature):
        self.title = feature.title
        self.description = feature.description
        self.client_id = feature.client_id
        self.product_id = feature.product_id
        self.priority = feature.priority
        self.target_date = feature.target_date

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "client": self.client.client_name,
            "clientId": self.client.id,
            "product": self.product.product_area,
            "productId": self.product.id,
            "targetDate": self.target_date.strftime('%Y-%m-%d')
        }
