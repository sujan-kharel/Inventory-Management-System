"""
TODO ->
"""
from flask import Flask, redirect, request, render_template
from flask_sqlalchemy import SQLAlchemy
from Host.host import host_inv
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    upc = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(200), nullable=False)


class insertItem:
    def __init__(self, upc, name, price, quantity, department):
        self.upc = upc
        self.name = name
        self.price = price
        self.quantity = quantity
        self.department = department

        if not int(upc) and str(name) and float(price) and int(quantity) and str(department):
            pass
        else:
            inv = Inventory(upc=upc, name=name, price=price, quantity=quantity, department=department)
            db.session.add(inv)
            db.session.commit()
            db.session.close()


# main menu
@app.route("/")
def index():
    # Main menu page

    return render_template("index.html")


# main menu options, sends requests -- > redirects to a page
@app.route("/requestPage", methods=["POST"])
def getInfo():
    # Renders template based on users' click
    if request.method == "POST":
        if request.form.get("order"):
            return redirect("/order")
        elif request.form.get("add"):
            return redirect("/add")
        elif request.form.get("viewInventory"):
            return redirect("/viewInventory")
        else:
            return render_template("index.html")


# allows to insert an item to the inventory
@app.route("/insert", methods=["post"])
def insert():
    if request.method == "POST":
        try:
            upc = int(request.form.get("upc"))
            price = float(request.form.get("price"))
            quantity = int(request.form.get("quantity"))
        except ValueError:
            return render_template("add.html", errMessage="One or more field has incorrect data")

        name = request.form.get("name")
        department = request.form.get("department")

        existingItem = Inventory.query.filter_by(upc=upc).first()
        if existingItem is None:
            insertItem(upc, name, price, quantity, department)
        else:
            return render_template("add.html", errMessage="An item with barcode:" + str(upc)
                                                          + " already exists in the system!")

    return redirect("/viewInventory")


# takes in order from host then inserts to data base
@app.route("/order", methods=["post"])
def placeOrder():
    if request.method == "POST":

        for upc, name, price, quantity, department in list(zip(request.form.getlist('upc'),
                                                               request.form.getlist('name'),
                                                               request.form.getlist('price'),

                                                               request.form.getlist('quantity'),
                                                               request.form.getlist('department')
                                                               )):
            if quantity != '' and int(quantity) > 0:
                existingItem = Inventory.query.filter_by(upc=int(upc)).first()
                if existingItem is None:
                    insertItem(int(upc), name, float(price), int(quantity), department)

                else:
                    existingItem.quantity = int(quantity) + existingItem.quantity
                    db.session.commit()

    return redirect("/invoice")


# renders host page, shows all the available products to add it to inventory
@app.route("/order")
def loadOrder():
    return render_template("order.html", host_inv=host_inv)


# renders ad.html page based on the request made by users
@app.route("/add")
def add():
    return render_template("add.html")


# upon request, Displays all the products in the inventory
@app.route("/viewInventory")
def viewInventory():
    inventory = Inventory.query.all()

    return render_template("viewInventory.html", inventory=inventory)


@app.route("/update-item", methods=["POST"])
def getUpdateItem():
    if request.method == "POST":
        try:
            upc = int(request.form.get("update"))
        except ValueError:
            return redirect("/viewInventory")
        itemObject = Inventory.query.filter_by(upc=upc).first()
        return render_template("update.html", itemObject=itemObject)


@app.route("/add/subtract/remove", methods=["POST"])
def updateItem():
    if request.method == "POST":

        action_type = request.form.get("update-action")
        upc = None
        objectToUpdate = None

        try:
            upc = int(request.form.get("upc"))
            objectToUpdate = Inventory.query.filter_by(upc=upc).first()
        except ValueError:
            redirect("/viewInventory")

        if action_type == "remove":
            db.session.delete(objectToUpdate)
            db.session.commit()
        elif action_type == "pull":
            try:
                qty = int(request.form.get("quantity"))
                objectToUpdate.quantity = objectToUpdate.quantity - qty
                db.session.commit()
            except ValueError:
                redirect("/viewInventory")
        elif action_type == "put":
            try:
                qty = int(request.form.get("quantity"))
                objectToUpdate.quantity = objectToUpdate.quantity + qty
                db.session.commit()
            except ValueError:
                redirect("/viewInventory")

    return redirect("/viewInventory")


@app.route("/search-items", methods=["POST"])
def search():
    inventory_objects = []
    if request.method == "POST":
        try:
            search_name = str(request.form.get("search")).lower()
            print(search_name)
            inventory = Inventory.query.all()

            for item in inventory:
                if str(item.name).lower().__contains__(search_name):
                    inventory_objects.append(item)

        except ValueError:
            return redirect("/viewInventory")

    if len(inventory_objects) <= 0:
        return redirect("/viewInventory")

    return render_template("viewInventory.html", inventory=inventory_objects)


if __name__ == "__main__":
    app.run(debug=True)
