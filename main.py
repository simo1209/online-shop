from functools import wraps

from flask import Flask
from flask import render_template, request, redirect, url_for, jsonify
import json

from order import Order
from user import User
from errors import register_error_handlers

from flaskext.auth import Auth
from flaskext.auth import login_required

app = Flask(__name__)
auth = Auth(app)

app.secret_key = 'N4BUdSXUzHxNoO8g'

@app.route('/')
def hello_world():
    return redirect("/orders")

@app.route("/users", methods = ["POST"])
def create_user():
    user_data = request.get_json(force=True, silent=True)
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
    

@app.route('/orders')
def list_orders():
    return render_template('orders.html', orders=Order.all())


@app.route('/orders/<int:id>')
def show_order(id):
    order = Order.find(id)

    return render_template('order.html', order=order)


@app.route('/orders/<int:id>/edit', methods=['GET', 'POST'])
def edit_order(id):
    order = Order.find(id)
    if request.method == 'GET':
        return render_template('edit_order.html',order=order)
    elif request.method == 'POST':
        order.name = request.form['name']
        order.description = request.form['description']
        order.content = request.form['price']
        order.active = request.form['active']
        order.save()
        return redirect(url_for('show_order', id=order.id))


@app.route('/orders/new', methods=['GET', 'POST'])
@login_required()
def new_order():
    if request.method == 'GET':
        return render_template('new_order.html')
    elif request.method == 'POST':
        
        Order(id = None, name = request.form['name'], description = request.form['description'], price = request.form['price'], date_added = None).create()

        return redirect('/')


@app.route('/orders/<int:id>/delete', methods=['POST'])
def delete_order(id):
    order = Order.find(id)
    order.delete()

    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        values = (
            None,
            request.form['username'],
            User.hash_password(request.form['password'])
        )
        User(*values).create()

        return redirect('/')


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
