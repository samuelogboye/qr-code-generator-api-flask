import pytest
from app import app, db
from app.models import User, QRCode

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_register(client):
    response = client.post('/register', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 201
    assert b'registered successfully' in response.data

def test_generate_qr(client):
    # First register and login
    client.post('/register', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    token = response.json['access_token']
    
    # Test QR generation
    response = client.post('/generate_qr', 
        json={'url': 'https://example.com'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 201
    assert b'generated successfully' in response.data 