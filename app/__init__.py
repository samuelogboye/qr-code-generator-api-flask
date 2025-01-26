import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from sqlalchemy import text
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)

    # Wait for database to be ready
    with app.app_context():
        retry_count = 0
        while retry_count < 5:
            try:
                # Try to create a connection to the database
                db.session.execute(text('SELECT 1'))
                print("Database connection successful!")
                break
            except Exception as e:
                print(f"Database connection failed! Error: {e}")
                retry_count += 1
                time.sleep(5)
                if retry_count == 5:
                    print("Could not connect to database after 5 attempts")
                    raise

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp, url_prefix='/api/v1')

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    return app 