from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import qrcode
import io
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)

# Database Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/qr_code_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

class QRCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(2048), nullable=False, unique=True)
    qr_code = db.Column(db.LargeBinary, nullable=False)

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)
    user = User(username=username, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200

@app.route('/generate_qr', methods=['POST'])
@jwt_required()
def generate_qr():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Check if the QR code already exists
    existing_qr = QRCode.query.filter_by(url=url).first()
    if existing_qr:
        return jsonify({'message': 'QR code already exists'}), 200

    # Generate QR Code
    qr = qrcode.QRCode(box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_binary = buffer.getvalue()

    # Save QR Code to the database
    qr_code = QRCode(url=url, qr_code=qr_binary)
    db.session.add(qr_code)
    db.session.commit()

    return jsonify({'message': 'QR code generated successfully'}), 201

@app.route('/get_qr', methods=['GET'])
@jwt_required()
def get_qr():
    url = request.args.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    qr_code = QRCode.query.filter_by(url=url).first()
    if not qr_code:
        return jsonify({'error': 'QR code not found'}), 404

    return send_file(io.BytesIO(qr_code.qr_code), mimetype='image/png')

@app.route('/delete_qr', methods=['DELETE'])
@jwt_required()
def delete_qr():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    qr_code = QRCode.query.filter_by(url=url).first()
    if not qr_code:
        return jsonify({'error': 'QR code not found'}), 404

    db.session.delete(qr_code)
    db.session.commit()
    return jsonify({'message': 'QR code deleted successfully'}), 200

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
