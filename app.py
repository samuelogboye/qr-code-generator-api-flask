from app import create_app, db

app = create_app()

# Custom error handlers for the blueprint
@app.errorhandler(404)
def handle_404(e):
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested URL was not found on the server.',
        'status_code': 404
    }), 404

@app.errorhandler(405)
def handle_405(e):
    return jsonify({
        'error': 'Method Not Allowed',
        'message': f'The method {request.method} is not allowed for the requested URL.',
        'allowed_methods': e.valid_methods,
        'status_code': 405
    }), 405

if __name__ == '__main__':
    app.run()