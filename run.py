
import os

from app import create_app

if __name__ == '__main__':
    os.environ.setdefault('APP_ENV', 'development')
    app = create_app()
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', '5000'))
    debug = os.environ.get('FLASK_DEBUG', '0').lower() in {'1', 'true', 'yes', 'on'}
    app.run(host=host, port=port, debug=debug)
else:
    app = create_app()
