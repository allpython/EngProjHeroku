#################
#### imports ####
#################

from flask import redirect, render_template, request, url_for, Blueprint
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, date

from project import db
from project.models import FeatureRequest, Client, Product
from project.utils import helper

################
#### config ####
################

features_blueprint = Blueprint(
    'features', __name__,
)


################
#### routes ####
################

@features_blueprint.route("/featureRequest", methods=["GET", "POST"])
@login_required
def feature_request():
    #from IPython import embed; embed()
    clients = Client.query.order_by(Client.id).all()
    products = Product.query.order_by(Product.id).all()

    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']
        client_id = int(request.form['client'])
        product_id = int(request.form['product'])
        priority = int(request.form['priority'])
        target_date = datetime.strptime(request.form['targetDate'], '%Y-%m-%d')

        feature = FeatureRequest(title=title, description=description, client_id=client_id,
                        product_id=product_id, priority=priority, target_date=target_date )

        exis_feature = FeatureRequest.query.filter_by(title=title).filter_by(client_id=client_id).filter_by(product_id=product_id).first()
        if exis_feature:
            return render_template('show_feature.html', clients=clients, products=products, feature=exis_feature, error="Feature with the same title already exists for this client!")

        features_list = FeatureRequest.query.filter_by(client_id=client_id).order_by(FeatureRequest.priority).all()

        from IPython import embed; embed()
        features_list = prioritize_features(features_list, feature)
        for feature in features_list:
            db.session.add(feature)
            db.session.commit()
        return redirect(url_for('clients.clients_base'))

    return render_template('feature_request.html', clients=clients, products=products)

@features_blueprint.route("/feature/<int:id>", methods=["GET", "POST"])
@login_required
def get_feature(id):
    feature = FeatureRequest.query.get(id)
    #client = [client for client in clients if client.client_id == id][0]
    if feature:
        clients = Client.query.order_by(Client.id).all()
        products = Product.query.order_by(Product.id).all()

        if request.method == 'POST':
            features_list = []
            if feature.client_id == int(request.form['client']):
                features_list = FeatureRequest.query.filter_by(client_id=feature.client_id).order_by(FeatureRequest.priority).all()
                features_list.remove(feature)
            else:
                exis_feature = FeatureRequest.query.filter_by(title=request.form['title']).filter_by(client_id=int(request.form['client'])).filter_by(product_id=int(request.form['product'])).first()
                if exis_feature:
                    return render_template('show_feature.html', clients=clients, products=products, feature=exis_feature, error="Feature with the same title already exists for this client!")
                features_list = FeatureRequest.query.filter_by(client_id=int(request.form['client'])).order_by(FeatureRequest.priority).all()


            feature.title = request.form['title']
            feature.description = request.form['description']
            feature.client_id = int(request.form['client'])
            feature.product_id = int(request.form['product'])
            feature.priority = int(request.form['priority'])
            feature.target_date = datetime.strptime(request.form['targetDate'], '%Y-%m-%d')

            features_list = prioritize_features(features_list, feature)
            for feature in features_list:
                db.session.add(feature)
                db.session.commit()
            return redirect(url_for('clients.clients_base'))

        feature.target_date = feature.target_date.strftime('%Y-%m-%d')
        return render_template('show_feature.html', clients=clients, products=products, feature=feature)
    return redirect(url_for('home.home'))

@features_blueprint.route("/feature/delete/<int:id>")
@login_required
def delete_feature(id):
    feature = FeatureRequest.query.get(id)
    if feature:
        db.session.delete(feature)
        db.session.commit()
        return redirect(url_for('clients.clients_base'))
    return redirect(url_for('home.home'))

@features_blueprint.route('/api/v1/feature/save', methods=['POST'])
@login_required
def add_or_update_feature():
    #from IPython import embed; embed()
    return helper.add_or_update_items(FeatureRequest, request)

def prioritize_features(features_list, new_feature):
    new_list = []
    from IPython import embed; embed()
    curr_priority = new_feature.priority

    for feature in features_list:

        if feature.priority == curr_priority:
            feature.priority = feature.priority+1
            curr_priority = feature.priority
            new_list.append(feature)

    new_list.append(new_feature)
    return new_list
