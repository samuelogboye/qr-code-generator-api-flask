import os
from typing import Optional
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
import io
from app import db
from app.models import User, QRCode
from app.errors import APIError
from app.utils import generate_qr_code

bp = Blueprint('main', __name__)

# Routes
@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            raise APIError('No data provided', status_code=400)
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            raise APIError('Username and password are required', status_code=400)
        print("27")
        if User.query.filter_by(username=username).first():
            raise APIError('Username already exists', status_code=409)
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'message': 'User registered successfully'}), 201
    except APIError as e:
        print(e)
        raise e
    except Exception as e:
        print(e)
        raise APIError('Internal server error', status_code=500)

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            raise APIError('No data provided', status_code=400)
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            raise APIError('Username and password are required', status_code=400)
        
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            raise APIError('Invalid username or password', status_code=401)
        
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token}), 200
    except APIError as e:
        raise e
    except Exception as e:
        raise APIError('Internal server error', status_code=500)

@bp.route('/generate_qr', methods=['POST'])
@jwt_required()
def generate_qr():
    try:
        current_user = User.query.filter_by(username=get_jwt_identity()).first()
        data = request.get_json()
        if not data:
            raise APIError('No data provided', status_code=400)
        
        url = data.get('url')
        if not url:
            raise APIError('URL is required', status_code=400)

        existing_qr = QRCode.query.filter_by(url=url, user_id=current_user.id).first()
        if existing_qr:
            return jsonify({'message': 'QR code already exists for this user'}), 200

        qr_binary = generate_qr_code(url)
        if not qr_binary:
            raise APIError('Failed to generate QR code', status_code=500)

        qr_code = QRCode(url=url, qr_code=qr_binary, user_id=current_user.id)
        db.session.add(qr_code)
        db.session.commit()

        return jsonify({
            'message': 'QR code generated successfully',
            'qr_code_id': qr_code.id
        }), 201
    except APIError as e:
        raise e
    except Exception as e:
        raise APIError('Internal server error', status_code=500)

@bp.route('/get_qr', methods=['GET'])
@jwt_required()
def get_qr():
    try:
        current_user = User.query.filter_by(username=get_jwt_identity()).first()
        url = request.args.get('url')

        if not url:
            raise APIError('URL is required', status_code=400)

        qr_code = QRCode.query.filter_by(url=url, user_id=current_user.id).first()
        if not qr_code:
            raise APIError('QR code not found', status_code=404)

        return send_file(
            io.BytesIO(qr_code.qr_code),
            mimetype='image/png',
            as_attachment=False,
            download_name=f"qr_code_{qr_code.id}.png"
        )
    except APIError as e:
        raise e
    except Exception as e:
        raise APIError('Internal server error', status_code=500)

@bp.route('/delete_qr', methods=['DELETE'])
@jwt_required()
def delete_qr():
    try:
        current_user = User.query.filter_by(username=get_jwt_identity()).first()
        data = request.get_json()
        if not data:
            raise APIError('No data provided', status_code=400)

        url = data.get('url')
        if not url:
            raise APIError('URL is required', status_code=400)

        qr_code = QRCode.query.filter_by(url=url, user_id=current_user.id).first()
        if not qr_code:
            raise APIError('QR code not found', status_code=404)

        db.session.delete(qr_code)
        db.session.commit()
        return jsonify({'message': 'QR code deleted successfully'}), 200
    except APIError as e:
        raise e
    except Exception as e:
        raise APIError('Internal server error', status_code=500)

@bp.route('/list_qr_codes', methods=['GET'])
@jwt_required()
def list_qr_codes():
    try:
        current_user = User.query.filter_by(username=get_jwt_identity()).first()
        qr_codes = QRCode.query.filter_by(user_id=current_user.id).all()
        
        return jsonify({
            'qr_codes': [{
                'id': qr.id,
                'url': qr.url,
                'created_at': qr.created_at.isoformat()
            } for qr in qr_codes]
        }), 200
    except Exception as e:
        raise APIError('Internal server error', status_code=500)

@bp.route('/test-db', methods=['GET'])
def test_db():
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({'message': 'Database connection successful'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
