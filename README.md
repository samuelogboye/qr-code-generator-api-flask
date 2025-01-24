# QR Code Generator API

A Flask-based REST API for generating and managing QR codes.

## Features

- User authentication with JWT
- QR code generation
- QR code management (create, read, delete)
- User-specific QR code storage
- Secure password hashing
- Error handling
- Input validation

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate # On Windows: 
venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
```

4. Run the application:
```bash
flask run
```

5. Access the API:
```bash
http://127.0.0.1:5000/
```

## Testing

To run tests, use:
```bash
pytest
```


