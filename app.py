# app.py
from flask import Flask, render_template, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///robot_tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pickup_location = db.Column(db.String(100), nullable=False)
    delivery_location = db.Column(db.String(100), nullable=False)
    item_description = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='Queued')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Navigation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_location = db.Column(db.String(100), nullable=False)
    target_area = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default='Queued')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def get_robot_status():
    return {
        'battery_level': 85,
    }

def get_active_count(model):
    return model.query.filter_by(status='In Progress').count()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/delivery')
def delivery():
    deliveries = Delivery.query.all()
    robot_status = get_robot_status()
    robot_status['status'] = "Delivery Mode"
    robot_status['active_tasks'] = get_active_count(Delivery)
    return render_template('delivery.html', 
                         tasks=deliveries,
                         robot_status=robot_status,
                         page_type="delivery")

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

@app.route('/api/delivery', methods=['POST'])
def create_delivery():
    data = request.json
    new_task = Delivery(
        pickup_location=data['pickup_location'],
        delivery_location=data['delivery_location'],
        item_description=data['item_description']
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({
        'status': 'success',
        'id': new_task.id,
        'active_tasks': get_active_count(Delivery)
    })

@app.route('/api/navigation', methods=['POST'])
def create_navigation():
    data = request.json
    new_task = Navigation(
        user_location=data['user_location'],
        target_area=data['target_area'],
        user_name=data.get('user_name') 
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({
        'status': 'success',
        'id': new_task.id,
        'active_tasks': get_active_count(Navigation)
    })

@app.route('/api/<task_type>/<int:task_id>/status', methods=['POST'])
def update_task_status(task_type, task_id):
    Model = Delivery if task_type == 'delivery' else Navigation
    task = Model.query.get_or_404(task_id)
    data = request.json
    task.status = data['status']
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'new_status': task.status,
        'active_tasks': get_active_count(Model)
    })


if __name__ == '__main__':
    with app.app_context():
        db.drop_all() # reset the database
        db.create_all()
    app.run(debug=True)