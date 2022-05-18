from flask import Flask
from flask import redirect, render_template, url_for
from flask import request
from flask_sqlalchemy import SQLAlchemy
import product
import warehouse

app = Flask(__name__)
app.config['SECRET_KEY'] = 'red_hot_chili_peppers'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    price = db.Column(db.Float, unique=True)


class Locations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True)
    address = db.Column(db.String(750), unique=True)


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)
    qty = db.Column(db.Integer)


warehouses: list[warehouse.Warehouse]
products: list[product.Product]

warehouses = []
products = []


def getWarehouses():
    """
    :return: List of warehouses
    """
    all_warehouses = Locations.query.all()
    for i in all_warehouses:
        newWarehouse = warehouse.Warehouse(i.id, i.name, i.address)
        warehouses.append(newWarehouse)


def getProducts():
    """
    :return: List of products
    """
    all_products = Product.query.all()
    for i in all_products:
        newProduct = product.Product(i.id, i.name, i.price)
        products.append(newProduct)


def populateWarehouse():
    """
    :return: populates products in warehouses
    """
    all_inventory = Inventory.query.order_by(Inventory.warehouse_id).all()
    for i in warehouses:
        for j in all_inventory:
            if j.warehouse_id == i.warehouse_id:
                i.addProduct(j.product_id, j.qty)
    for i in products:
        for j in warehouses:
            if i.product_id in j.warehouse_products:
                i.product_warehouse[j.warehouse_id] = \
                    j.warehouse_products[i.product_id]
                i.product_qty += j.warehouse_products[i.product_id]


@app.route('/')
def main():
    getWarehouses()
    getProducts()
    populateWarehouse()
    return render_template("home.html")


@app.route('/home')
def home():
    return render_template("home.html")


@app.route('/createProduct')
def addProduct():
    return render_template("addProduct.html", contents=warehouses)


@app.route('/createWarehouse')
def addWarehouse():
    return render_template("addWarehouse.html")


@app.route('/viewProducts')
def viewProducts():
    return render_template("viewProducts.html", contents=products)


@app.route('/viewLocations')
def viewLocations():
    return render_template("viewWarehouse.html", contents=warehouses)


@app.route('/createWarehouse', methods=['POST'])
def createWarehouse():
    name = request.form.get('warehouseName')
    address = request.form.get('warehouseLocation')
    new_location = Locations(name=name, address=address)
    db.session.add(new_location)
    db.session.commit()

    w_id = Locations.query.filter_by(name=name).first()

    warehouses.append(warehouse.Warehouse(w_id.id, name, address))

    return redirect(url_for('createWarehouse'))


@app.route('/createProduct', methods=['POST'])
def createProduct():
    name = str(request.form.get('productName'))
    price = float(request.form.get('productPrice'))
    select_warehouse = int(request.form.get('selected_warehouse'))
    qty = int(request.form.get('productQty'))
    new_product = Product(name=name, price=price)
    db.session.add(new_product)
    p_id = Product.query.filter_by(name=name).first()
    new_inventory = Inventory(warehouse_id=select_warehouse, product_id=p_id.id,
                              qty=qty)
    db.session.add(new_inventory)
    db.session.commit()

    newProduct = product.Product(p_id.id, name, price)
    newProduct.addWarehouse(select_warehouse, qty)
    products.append(newProduct)

    for i in warehouses:
        if i.warehouse_id == select_warehouse:
            i.addProduct(newProduct.product_id, qty)

    return redirect(url_for('createProduct'))


@app.route('/deleteWarehouse/<object_key>')
def deleteWarehouse(object_key):
    Locations.query.filter_by(id=object_key).delete()
    Inventory.query.filter_by(warehouse_id=object_key).delete()
    db.session.commit()
    warehouses.clear()
    products.clear()
    getWarehouses()
    getProducts()
    populateWarehouse()
    return redirect(url_for('viewLocations'))


@app.route('/deleteProduct/<object_key>')
def deleteProduct(object_key):
    Product.query.filter_by(id=object_key).delete()
    Inventory.query.filter_by(product_id=object_key).delete()
    db.session.commit()
    warehouses.clear()
    products.clear()
    getWarehouses()
    getProducts()
    populateWarehouse()
    return redirect(url_for('viewProducts'))


if __name__ == '__main__':
    app.run()
