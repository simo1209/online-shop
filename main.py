from functools import wraps

from flask import Flask
from flask import render_template, request, redirect, url_for, jsonify
import json

from order import Order
from user import User

app = Flask(__name__)

def require_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.cookies.get('token')
        if not token or not User.verify_token(token):
            return redirect('/login')
        return func(*args, **kwargs)
    return wrapper


@app.route('/')
def hello_world():
    return redirect("/orders")


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
@require_login
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
        data = json.loads(request.data.decode('ascii'))
        username = data['username']
        password = data['password']
        user = User.find_by_username(username)
        if not user or not user.verify_password(password):
            return jsonify({'token': None})
        token = user.generate_token()
        return jsonify({'token': token.decode('ascii')})


if __name__ == '__main__':
    app.run()
