# app.py
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///deliveries.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pickup_location = db.Column(db.String(100), nullable=False)
    delivery_location = db.Column(db.String(100), nullable=False)
    item_description = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='Queued')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def get_active_deliveries_count():
    return Delivery.query.filter_by(status='In Progress').count()

@app.route('/')
def dashboard():
    deliveries = Delivery.query.all()
    robot_status = {
        'battery_level': 85,
        'status': 'Active',
        'active_deliveries': get_active_deliveries_count()  # Dynamic count
    }
    return render_template('dashboard.html', 
                         deliveries=deliveries,
                         robot_status=robot_status)

@app.route('/api/delivery', methods=['POST'])
def create_delivery():
    data = request.json
    new_delivery = Delivery(
        pickup_location=data['pickup_location'],
        delivery_location=data['delivery_location'],
        item_description=data['item_description']
    )
    db.session.add(new_delivery)
    db.session.commit()
    
    # Return updated delivery count along with success message
    return jsonify({
        'status': 'success', 
        'id': new_delivery.id,
        'active_deliveries': get_active_deliveries_count()
    })

@app.route('/api/delivery/<int:delivery_id>/status', methods=['POST'])
def update_delivery_status(delivery_id):
    delivery = Delivery.query.get_or_404(delivery_id)
    data = request.json
    delivery.status = data['status']
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'new_status': delivery.status,
        'active_deliveries': get_active_deliveries_count()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)