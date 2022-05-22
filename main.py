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

current_product = []  # Keeps track of product selected while editing
current_warehouse = []  # Keeps track of warehouse selected while editing


class Product(db.Model):
    """
    Initializes product table and provides better access data from SQL Lite
    Database. It is also used to create a new database.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    price = db.Column(db.Float)


class Locations(db.Model):
    """
    Initializes table locations as id the primary key. Stores data relating to
    warehouses.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True)
    address = db.Column(db.String(750), unique=True)


class Inventory(db.Model):
    """
    Initializes table inventory. It keeps a track of available product inventory
    at respective warehouses.
    """

    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)
    qty = db.Column(db.Integer)


warehouses: list[warehouse.Warehouse]
products: list[product.Product]

warehouses = []  # Keeps a track of all available warehouses throughout the
# program

products = []  # Keeps a track of all available products throughout the program


def getWarehouses():
    """
    Populates the warehouses list from the database.
    :return: None
    """

    all_warehouses = Locations.query.all()
    for i in all_warehouses:
        newWarehouse = warehouse.Warehouse(i.id, i.name, i.address)
        warehouses.append(newWarehouse)


def getProducts():
    """
    Populates the products list from the database.
    :return: None
    """

    all_products = Product.query.all()
    for i in all_products:
        newProduct = product.Product(i.id, i.name, i.price)
        products.append(newProduct)


def populateWarehouse():
    """
    Populates all warehouses with respective products and their inventory
    as from inventory database.
    :return: None
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


def update_everything():
    """
    Updates all data locally including products, inventory, and warehouses.
    :return: None
    """

    warehouses.clear()
    products.clear()
    getWarehouses()
    getProducts()
    populateWarehouse()


@app.route('/')
def main():
    """
    First function called when application is started
    :return: home.html template
    """

    update_everything()
    return render_template("home.html", products=products,
                           warehouses=warehouses)


@app.route('/home')
def home():
    """
    This is the home page. Renders home.html template.
    :return: home.html template
    """

    update_everything()
    return render_template("home.html", products=products,
                           warehouses=warehouses)


@app.route('/createProduct')
def addProduct():
    """
    This is the Create Product page. Renders the addProduct.html template
    :return: addProduct.html template
    """

    update_everything()
    return render_template("addProduct.html", contents=warehouses)


@app.route('/createWarehouse')
def addWarehouse():
    """
    This is the Add Location Page. Renders the addWarehouse.html template
    :return: addWarehouse.html template
    """

    return render_template("addWarehouse.html")


@app.route('/viewProducts')
def viewProducts():
    """
    This is the View and Manage products page. Renders the viewProducts.html
    template.
    :return: viewProducts.html template
    """

    update_everything()
    return render_template("viewProducts.html", contents=products)


@app.route('/viewLocations')
def viewLocations():
    """
    This is the view and manage locations page. Renders the viewWarehouse.html
    template.
    :return: viewWarehouse.html template
    """

    update_everything()
    return render_template("viewWarehouse.html", contents=warehouses)


@app.route('/editProduct/<p_id>')
def editProduct(p_id):
    """
    This function prepares and renders the Edit Product page with the
    appropriate parameters such as the product selected to be edited and
    all of its warehouses and available qty.
    :param p_id: Product ID
    :return: editProduct.html template
    """

    selected_product = None  # Product selected to be edited
    for i in products:
        if i.product_id == int(p_id):
            selected_product = i
    current_product.append(selected_product)  # Keeping track of product
    # selected globally

    p_warehouses = {}  # Warehouses and the product qty at each warehouse
    for w_id, value in selected_product.product_warehouse.items():
        for i in warehouses:
            if i.warehouse_id == w_id:
                p_warehouses[i.warehouse_name] = value
    for i in warehouses:
        if i.warehouse_name not in p_warehouses:
            p_warehouses[i.warehouse_name] = 0

    return render_template("editProduct.html", content=selected_product,
                           p_warehouses=p_warehouses)


@app.route('/editProduct', methods=['POST'])
def updateProduct():
    """
    This function updates the selected Product if any changes to name, price,
    or available qty are made.
    :return: Redirects to View and Manage Products page.
    """

    selected_product = current_product.pop()  # Gets the selected product
    name = request.form.get('p_name')  # Name field from form
    price = float(request.form.get('p_price'))  # Price field from form

    entry = Product.query.filter_by(id=selected_product.product_id).first()

    if name != selected_product.product_name:  # Updates name if changed
        entry.name = name
    if price != selected_product.product_price:  # Updates price if changed
        entry.price = price

    for i in warehouses:
        w_id = i.warehouse_id  # Warehouse ID
        name = i.warehouse_name + '_qty'  # Warehouse qty string builder
        qty = int(request.form.get(name))  # Gets the qty at warehouse
        # If warehouse already exists:
        if w_id in selected_product.product_warehouse:
            loc_entry = Inventory.query.filter_by(product_id=
                                                  selected_product.product_id,
                                                  warehouse_id=w_id).first()
            if selected_product.product_warehouse[w_id] != qty:
                loc_entry.qty = qty
        # If warehouse never had the product before
        elif qty > 0:
            new_inventory = Inventory(warehouse_id=w_id,
                                      product_id=selected_product.product_id,
                                      qty=qty)
            db.session.add(new_inventory)

    # Commits all changes to the database

    db.session.commit()

    # Updates everything

    update_everything()

    return redirect(url_for('viewProducts'))


@app.route('/editWarehouse/<w_id>')
def editWarehouse(w_id):
    """
    This function prepares and renders the Edit Warehouse page with the
    appropriate parameters such as the warehouse selected to be edited and
    all of its products and available qty.
    :param w_id: Warehouse ID
    :return: Renders Edit Warehouse Page
    """

    selected_warehouse = None  # Selected Warehouse

    for i in warehouses:
        if i.warehouse_id == int(w_id):
            selected_warehouse = i
    current_warehouse.append(selected_warehouse)
    w_products = {}  # All products in the warehouse

    for p_id, value in selected_warehouse.warehouse_products.items():
        for i in products:
            if i.product_id == p_id:
                w_products[i.product_name] = value

    return render_template("editWarehouse.html", content=selected_warehouse,
                           w_products=w_products)


@app.route('/editWarehouse', methods=['POST'])
def updateWarehouse():
    """
    This function updates the selected Warehouse if any changes to name,
    address, or available qty are made.
    :return: Redirects to View and Manage Locations
    """

    selected_warehouse: warehouse.Warehouse
    selected_warehouse = current_warehouse.pop()  # Selected warehouse

    name = request.form.get('w_name')  # Name from form
    address = request.form.get('w_address')  # Address from form

    entry = Locations.query.filter_by(
        id=selected_warehouse.warehouse_id).first()  # Gets data from
    # warehouse table

    if name != selected_warehouse.warehouse_name:  # Updates if name is changed
        entry.name = name
    if address != selected_warehouse.warehouse_address:  # Updates if address
        # if changed
        entry.address = address

    w_products = []  # List of all products in the warehouse

    for key in selected_warehouse.warehouse_products.keys():
        for i in products:
            if i.product_id == key:
                w_products.append(i)

    for i in w_products:
        p_id = i.product_id
        name = i.product_name + '_qty'
        qty = int(request.form.get(name))

        loc_entry = Inventory.query.filter_by(product_id=p_id,
                                              warehouse_id=
                                              selected_warehouse.warehouse_id).\
            first()

        if selected_warehouse.warehouse_products[p_id] != qty:  # Updates if
            # qty is updated
            loc_entry.qty = qty

    db.session.commit()     # Commit changes to session

    update_everything()     # Updates Everything

    return redirect(url_for('viewLocations'))


@app.route('/createWarehouse', methods=['POST'])
def createWarehouse():
    """
    Creates a new warehouse from the parameters name, and address.
    :return: Redirects to the Create Warehouse location
    """

    name = request.form.get('warehouseName')  # Gets name from form
    address = request.form.get('warehouseLocation')  # Gets address from form
    new_location = Locations(name=name, address=address)  # Initializes a
    # new location
    db.session.add(new_location)  # Adds to session
    db.session.commit()  # Commit changes

    w_id = Locations.query.filter_by(name=name).first()  # Gets ID
    # of created warehouse from database

    warehouses.append(warehouse.Warehouse(w_id.id, name, address))  # Adds
    # warehouse to global warehouse list

    return redirect(url_for('createWarehouse'))


@app.route('/createProduct', methods=['POST'])
def createProduct():
    """
    Creates a new product from parameters name, price, starting warehouse,
    and qty.
    :return: Redirects to Create Product Page
    """

    name = str(request.form.get('productName'))  # Gets product name
    # from form
    price = float(request.form.get('productPrice'))  # Gets price from form
    select_warehouse = int(request.form.get('selected_warehouse'))  # Gets
    # selected warehouse
    qty = int(request.form.get('productQty'))  # Gets qty
    new_product = Product(name=name, price=price)  # Creates new product
    db.session.add(new_product)  # Adds to the current session
    p_id = Product.query.filter_by(name=name).first()  # Gets assigned
    # product id
    new_inventory = Inventory(warehouse_id=select_warehouse, product_id=p_id.id,
                              qty=qty)  # Creates entry for inventory table
    db.session.add(new_inventory)
    db.session.commit()  # Commit changes

    newProduct = product.Product(p_id.id, name, price)
    newProduct.addWarehouse(select_warehouse, qty)  # Add the warehouse to
    # the product warehouse list.
    products.append(newProduct)  # Adds product to the global products list

    for i in warehouses:
        if i.warehouse_id == select_warehouse:
            i.addProduct(newProduct.product_id, qty)

    return redirect(url_for('createProduct'))


@app.route('/deleteWarehouse/<object_key>')
def deleteWarehouse(object_key):
    """
    Deletes the selected warehouse from the database and its inventory data and
    updates the global parameters.
    :param object_key: Warehouse ID
    :return: Redirects to View and Manage Locations
    """

    Locations.query.filter_by(id=object_key).delete()  # Deletes data from
    # warehouse table
    Inventory.query.filter_by(warehouse_id=object_key).delete()  # Deletes
    # data from inventory table
    db.session.commit()  # Commits all changes made
    update_everything()  # Updates everything
    return redirect(url_for('viewLocations'))


@app.route('/deleteProduct/<object_key>')
def deleteProduct(object_key):
    """
    This function deletes the product from the database and its inventory data
    and updates global parameters.
    :param object_key: Product ID
    :return: Redirects to View and Manage Products Page
    """

    Product.query.filter_by(id=object_key).delete()  # Deletes data from
    # product table
    Inventory.query.filter_by(product_id=object_key).delete()  # Deletes data
    # from inventory table
    db.session.commit()  # Commits all changes made to database
    update_everything()  # Updates Everything
    return redirect(url_for('viewProducts'))


if __name__ == '__main__':
    app.run()
