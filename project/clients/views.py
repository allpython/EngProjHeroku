#################
#### imports ####
#################

from flask import redirect, render_template, request, Blueprint
from flask_login import login_user, login_required, logout_user, current_user

from project.models import Client
from project.utils import helper

################
#### config ####
################

clients_blueprint = Blueprint(
    'clients', __name__,
)


################
#### routes ####
################

@clients_blueprint.route("/clients")
@login_required
def clients_base():
    clients = Client.query.order_by(Client.id).all()
    return render_template('clients.html', clients=clients)

@clients_blueprint.route('/api/v1/clients')
@login_required
def list_clients():
    return helper.get_items_list(Client)

@clients_blueprint.route('/api/v1/client/save', methods=['POST'])
@login_required
def add_or_update_client():
    #from IPython import embed; embed()
    return helper.add_or_update_items(Client, request)


@clients_blueprint.route('/api/v1/client/delete/<int:id>')
@login_required
def delete_client_v1(id):
    return helper.delete_item(Client, id)
