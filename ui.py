# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
from functools import wraps
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from datetime import datetime
import requests
import os
from threading import Thread
from shared import restock_deque, coordinate_dict
# from api import restock_deque, coordinate_dict
from collections import deque

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///robot_tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SECRET_PASSWORD = 'peipei'
NAV_ENDPOINT = "http://127.0.0.1:5001"
SERVER_ENDPOINT = "http://127.0.0.1:5003"
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate
socketio = SocketIO(app)

item = {
    'vase': 'Vase_1',
    'keyboard': 'Keyboard_1',
    'bottle': 'Bottle_1',
    'cup': 'Cup_1',
}
area = {
    'vase': 'Vase Area',
    'keyboard': 'Keyboard Area',
    'bottle': 'Bottle Area',
    'cup': 'Cup Area',
}

class Restock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_area = db.Column(db.String(100), nullable=False)
    target_product = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='Queued')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Navigation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_area = db.Column(db.String(100), nullable=False)
    target_product = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='Queued')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def get_robot_status():
    return {
        'battery_level': 85,
    }

def get_active_count(model):
    return model.query.filter_by(status='In Progress').count()

def requires_password(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            entered_password = request.form.get('password')
            if entered_password == SECRET_PASSWORD:
                return f(*args, **kwargs)
            else:
                return redirect(url_for('enter_password'))
        return redirect(url_for('enter_password'))
    return decorated_function

@app.route('/')
def home():
    if restock_deque:
        product = restock_deque.popleft()
        area = f"{product.split('_')[0]} Area" 
        requests.post(f'http://127.0.0.1:5000/api/restock', json={'target_area': area, 'target_product': product, 'Server': True})
        print("success to send restock request to ui")
        return redirect(url_for('restock'))
    else:
        return render_template('home.html')

@app.route('/enter_password', methods=['GET', 'POST'])
def enter_password():
    return render_template('enter_password.html')
    
@app.route('/restock', methods=['GET', 'POST'])
@requires_password
def restock():
    restock_deque.clear()
    deliveries = Restock.query.all()
    robot_status = get_robot_status()
    robot_status['status'] = "Restocking"
    robot_status['active_tasks'] = get_active_count(Restock)
    return render_template('restock.html', 
                         tasks=deliveries,
                         robot_status=robot_status,
                         page_type="restock")

@app.route('/navigation')
def navigation():
    navigation_tasks = Navigation.query.all()
    robot_status = get_robot_status()
    robot_status['active_tasks'] = get_active_count(Navigation)
    robot_status['status'] = "Navigating"
    return render_template('navigation.html', 
                         tasks=navigation_tasks,
                         robot_status=robot_status,
                         page_type="navigation")

@app.route('/api/restock', methods=['POST'])
def create_restock():
    data = request.json
    new_task = Restock(
        target_area=data['target_area'],
        target_product=data['target_product']
    )
    db.session.add(new_task)

    while restock_deque:
        product = restock_deque.popleft()
        if product != data['target_product']:
            area = f"{product.split('_')[0]} Area"
            new_task = Restock(target_area=area, target_product=product)
            db.session.add(new_task)
    db.session.commit()

    if data.get("Server"):
        try:
            response = requests.post(f"{NAV_ENDPOINT}/navigate2stock", json={"c_stock": coordinate_dict.get("Stock")})
            print("Navigate2stock request success")
            return response.json(), 200
        except Exception as e:
            print(f"Navigate2stock request fail: {str(e)}")
            return {"error": f"product restock error: {str(e)}"}, 500
    socketio.emit('new_task', {'url': '/restock'})
    return jsonify({
        'status': 'success'
    })

@app.route('/api/navigation', methods=['POST'])
def create_navigation():
    data = request.json
    new_task = Navigation(
        target_area=data['target_area'],
        target_product=data['target_product']
    )
    db.session.add(new_task)
    db.session.commit()
    socketio.emit('new_task', {'url': 'navigation'})
    return jsonify({
        'status': 'success'
    })

@app.route('/api/<task_type>/<int:task_id>/status', methods=['POST'])
def update_task_status(task_type, task_id):
    Model = Restock if task_type == 'restock' else Navigation
    task = Model.query.get_or_404(task_id)
    data = request.json
    task.status = data['status']
    db.session.commit()
    id = task.id
    target_area = task.target_area
    target_product = task.target_product

    def send_post_request():
        try:
            requests.post(
                f"{SERVER_ENDPOINT}/api/set_product",
                json={"target_area": target_area, "id": id, "task_type": task_type, "target_product": target_product}
            )
        except Exception as e:
            print(f"Failed to send POST request: {e}")

    if task.status == "In Progress":
        Thread(target=send_post_request).start()

    return jsonify({
        'status': 'success',
        'new_status': task.status,
        'active_tasks': get_active_count(Model)
    })

@app.route('/api/robot/arrived', methods=['POST'])
def robot_arrived():
    data = request.json
    task_id = data['id']
    target_area = data['target_area']
    target_prodict = data['target_product']
    try:
        socketio.emit('robot_arrived', {'taskId': task_id, 'targetArea': target_area, 'targetProduct': target_prodict})
        return jsonify({
            'status': 'success', 
            'message': 'Robot arrived!'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'message': str(e)
        }), 500

@app.route('/api/append_restock_deque', methods=['POST'])
def add_to_restock_deque():
    data = request.json
    product = data['product']
    if product != "None":
        restock_deque.append(product)
        print(f"Successfully appended {product} into restock list via API")
    else:
        print("Product is None. Do nothing")
    return jsonify({"status": "success", "product": product}), 200

if __name__ == '__main__':
    with app.app_context():
        db.drop_all() # reset the database
        db.create_all()
    socketio.run(app)
    # app.run(debug=True)