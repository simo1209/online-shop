from functools import wraps

from flask import Flask
from flask import render_template, request, redirect, url_for, jsonify
import json

from order import Order
from user import User
from errors import register_error_handlers, ApplicationError

from auth import Auth, login_required, get_current_user_data

app = Flask(__name__)
register_error_handlers(app)
auth = Auth(app, 'login')

app.secret_key = 'N4BUdSXUzHxNoO8g'

@app.route("/users", methods = ["POST"])
def create_user():
    user_data = request.form
    if user_data == None:
        return "Bad request", 400
    user = User(user_data["email"], user_data["password"], user_data["username"], user_data["address"], user_data["phone"])
    user.save()
    return json.dumps(user.to_dict()), 201
    

@app.route("/users/<user_id>", methods = ["GET"])
def find_user(user_id):
    user = User.find(user_id)

    return json.dumps(user.to_dict()), 201

@app.route("/users", methods = ["GET"])
def list_users():
    return User.all()

@app.route("/users/<user_id>", methods=["PATCH"])
def edit_user(user_id):
    user = User.find(user_id)
    user.username = request.form["username"]
    user.address = request.form["addresss"]
    user.phone = request.form["phone"]
    user.save()
    
    return json.dumps(user.to_dict()), 201
    
@app.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    User.delete(user_id)

    return redirect('/')
    

@app.route('/api/orders')
def list_orders():
    return jsonify([order.__dict__ for order in Order.all()])

@app.route('/')
def index():
    return redirect('/orders')

@app.route('/orders')
def render_all_orders():
    return render_template('orders.html', orders = Order.all())


@app.route('/api/orders/<int:id>')
def show_order(id):
    order = Order.find(id)
    return jsonify(order.__dict__)

@app.route('/orders/<int:id>')
def render_order(id):
    return render_template('order.html', order = Order.find(id))

@app.route('/orders/<int:id>/edit')
@login_required
def render_order_edit(id):
    order = Order.find(id)
    current_user = get_current_user_data()

    if order.creator_id != current_user['id']:
        raise ApplicationError("You are not the owner of this order", 401)
    return render_template('edit_order.html',order=order)

@app.route('/api/orders/<int:id>/edit', methods=['POST'])
@login_required
def edit_order(id):
    order = Order.find(id)
    current_user = get_current_user_data()

    if order.creator_id != current_user['id']:
        raise ApplicationError("You are not the owner of this order", 401)

    order.name = request.form['name']
    order.description = request.form['description']
    order.price = request.form['price']
    order.save()
    return redirect(url_for('show_order', id=order.id))

@app.route('/orders/new')
@login_required
def render_order_form():
    return render_template('new_order.html')

@app.route('/api/orders/new', methods=['POST'])
@login_required
def new_order():
    current_user = get_current_user_data()
    Order(id = None, name = request.form['name'], description = request.form['description'], price = request.form['price'], date_added = None, creator_id = current_user['id']).create()

    return redirect('/')


@app.route('/api/orders/<int:id>/delete', methods=['POST'])
@login_required
def delete_order(id):
    order = Order.find(id)
    current_user = get_current_user_data()

    if current_user is not None:
        if order.creator_id == current_user['id']:
            order.delete()
        else:
            return 'You are not the owner',403
        return redirect('/')
    else:
        return 'Need to login', 401  


@app.route('/register', methods=['GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        data = dict(request.form)
        username = data['username']
        password = data['password']
        user = User.find_by_username(username)
        if user is not None:
            if user.authenticate(password.encode('utf-8')):
                return redirect('/')
        return "Failure", 401
            


if __name__ == '__main__':
    app.run()
