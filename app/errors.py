from flask import Blueprint, jsonify

bp = Blueprint('errors', __name__)

class APIError(Exception):
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@bp.app_errorhandler(APIError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@bp.app_errorhandler(404)
def not_found_error(error):
    return jsonify({'message': 'Resource not found'}), 404

@bp.app_errorhandler(500)
def internal_error(error):
    print(error)
    return jsonify({'message': 'Internal server error'}), 500 