from functools import wraps

from flask import Flask
from flask import render_template, request, redirect, url_for, jsonify
import json

from ad import Ad
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
    

@app.route('/api/ads')
def list_ads():
    return jsonify([ad.__dict__ for ad in Ad.all()])

@app.route('/')
def index():
    return redirect('/ads')

@app.route('/ads')
def render_all_ads():
    return render_template('ads.html', ads = Ad.all())


@app.route('/api/ads/<int:id>')
def show_ad(id):
    ad = Ad.find(id)
    return jsonify(ad.__dict__)

@app.route('/ads/<int:id>')
def render_ad(id):
    return render_template('ad.html', ad = Ad.find(id))

@app.route('/ads/<int:id>/edit')
@login_required
def render_ad_edit(id):
    ad = Ad.find(id)
    current_user = get_current_user_data()

    if ad.creator_id != current_user['id']:
        raise ApplicationError("You are not the owner of this ad", 401)
    return render_template('edit_ad.html',ad=ad)

@app.route('/api/ads/<int:id>/edit', methods=['POST'])
@login_required
def edit_ad(id):
    ad = Ad.find(id)
    current_user = get_current_user_data()

    if ad.creator_id != current_user['id']:
        raise ApplicationError("You are not the owner of this ad", 401)

    ad.name = request.form['name']
    ad.description = request.form['description']
    ad.price = request.form['price']
    ad.save()
    return redirect(url_for('render_ad', id=ad.id))

@app.route('/ads/new')
@login_required
def render_ad_form():
    return render_template('new_ad.html')

@app.route('/api/ads/new', methods=['POST'])
@login_required
def new_ad():
    current_user = get_current_user_data()
    Ad(id = None, name = request.form['name'], description = request.form['description'], price = request.form['price'], date_added = None, creator_id = current_user['id']).create()

    return redirect('/')


@app.route('/api/ads/<int:id>/delete', methods=['POST'])
@login_required
def delete_ad(id):
    ad = Ad.find(id)
    current_user = get_current_user_data()

    if current_user is not None:
        if ad.creator_id == current_user['id']:
            ad.delete()
        else:
            return 'You are not the owner',403
        return redirect('/')
    else:
        return 'Need to login', 401  

@app.route('/api/user/ads')
@login_required
def user_ads():
    current_user = User.find(get_current_user_data()['id'])
    ads = current_user.get_ads()
    return jsonify([ad.__dict__ for ad in ads])

@app.route('/user/ads')
@login_required
def render_user_ads():
    current_user = User.find(get_current_user_data()['id'])
    ads = current_user.get_ads()
    return render_template('ads.html', ads = ads)

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
        return ApplicationError("Credentials failed", 401)
            


if __name__ == '__main__':
    app.run()
