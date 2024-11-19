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

# Robot status simulation
robot_status = {
    'battery_level': 85,
    'status': 'Active',
    'active_deliveries': 0
}

@app.route('/')
def dashboard():
    deliveries = Delivery.query.all()
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
    return jsonify({'status': 'success', 'id': new_delivery.id})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)