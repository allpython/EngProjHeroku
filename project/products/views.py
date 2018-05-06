#################
#### imports ####
#################

from flask import redirect, render_template, request, Blueprint
from flask_login import login_user, login_required, logout_user, current_user

from project.models import Product
from project.utils import helper

################
#### config ####
################

products_blueprint = Blueprint(
    'products', __name__,
)


################
#### routes ####
################
@products_blueprint.route("/products")
@login_required
def products_base():
    products = Product.query.order_by(Product.id).all()
    return render_template('products.html', products=products)

@products_blueprint.route('/api/v1/products')
@login_required
def list_products():
    return helper.get_items_list(Product)

@products_blueprint.route('/api/v1/product/save', methods=['POST'])
@login_required
def add_or_update_product():
    #from IPython import embed; embed()
    return helper.add_or_update_items(Product, request)

@products_blueprint.route('/api/v1/product/delete/<int:id>')
@login_required
def delete_product_v1(id):
    return helper.delete_item(Product, id)
