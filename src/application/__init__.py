from flask import Flask, request, g
from config import configure_app
from flask_session import Session
from application.modules.utils import create_redis_client

def create_app():
    """Application factory function."""
    # Initialize Flask application
    app = Flask(__name__)

    # Configure the app
    configure_app(app)

    # Initialize Flask-Session
    Session(app)

    # Initialize Redis client and store it in app.extensions
    redis_client = create_redis_client()
    app.extensions['redis_client'] = redis_client

    # Provide a reusable function for Redis client access
    def get_redis_client():
        """Retrieve the Redis client from the app context."""
        if not hasattr(g, 'redis_client'):
            g.redis_client = app.extensions['redis_client']
        return g.redis_client

    # Attach get_redis_client function to app for global access
    app.get_redis_client = get_redis_client

    # Error handlers
    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f'Internal Server Error: {error}, Path: {request.path}')
        return 'Internal Server Error', 500

    @app.errorhandler(404)
    def page_not_found(error):
        app.logger.error(f'Page Not Found: {error}, Path: {request.path}')
        return 'Page Not Found', 404

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        app.logger.error(f'Unhandled Exception: {error}, Path: {request.path}')
        return 'Unhandled Exception', 500

    # Register blueprints
    from application.views import v1
    app.register_blueprint(v1.mod)

    from application.views import v1create
    app.register_blueprint(v1create.mod)

    from application.views import v1delete
    app.register_blueprint(v1delete.mod)

    from application.views import v1get
    app.register_blueprint(v1get.mod)

    from application.views import v1query
    app.register_blueprint(v1query.mod)

    from application.views import v1ui
    app.register_blueprint(v1ui.mod)

    from application.views import v1update
    app.register_blueprint(v1update.mod)

    from application.views import v1execute
    app.register_blueprint(v1execute.mod)
    return app

