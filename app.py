# app.py
from flask import Flask, render_template, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///robot_tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate
socketio = SocketIO(app)

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

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/restock')
def restock():
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
    db.session.commit()
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
    
    return jsonify({
        'status': 'success',
        'new_status': task.status,
        'active_tasks': get_active_count(Model)
    })

@app.route('/api/robot/arrived', methods=['POST'])
def robot_arrived():
    data = request.get_json()
    task_id = data['task_id']
    target_area = data['target_area']
    target_prodict = data['target_product']
    
    if not task_id:
        return jsonify({'error': 'Task ID is required'}), 400
    
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


if __name__ == '__main__':
    with app.app_context():
        db.drop_all() # reset the database
        db.create_all()
    socketio.run(app, debug=True)
    # app.run(debug=True)