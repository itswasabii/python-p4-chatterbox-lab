from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)
db.init_app(app)

# Define the Message model with SQLAlchemy
class Message(db.Model):
    __tablename__ = 'messages'
    __table_args__ = {'extend_existing': True} 
    
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'body': self.body,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

@app.route('/messages', methods=['GET', 'POST'])
def handle_messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        return jsonify([message.to_dict() for message in messages])
    
    if request.method == 'POST':
        data = request.get_json()
        if data and 'body' in data and 'username' in data:
            new_message = Message(body=data['body'], username=data['username'])
            db.session.add(new_message)
            db.session.commit()
            return jsonify(new_message.to_dict()), 201
        else:
            return make_response(jsonify({'error': 'Invalid request data'}), 400)

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def handle_message_by_id(id):
    message = Message.query.get(id)

    if not message:
        return make_response(jsonify({'error': 'Message not found'}), 404)
    
    if request.method == 'GET':
        return jsonify(message.to_dict())

    if request.method == 'PATCH':
        data = request.get_json()
        if data and 'body' in data:
            message.body = data['body']
            message.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify(message.to_dict())
        else:
            return make_response(jsonify({'error': 'Invalid request data'}), 400)
    
    if request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return make_response(jsonify({'message': 'Message deleted successfully'}), 204)

if __name__ == '__main__':
    # Use default port 5555
    app.run(port=5555)
