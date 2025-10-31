from flask import Flask, session
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    """Flask application factory — creates and configures the app instance."""
    app = Flask(__name__)

    # Core configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Database configuration
    app.config['DB_HOST'] = os.getenv('DB_HOST')
    app.config['DB_USER'] = os.getenv('DB_USER')
    app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD')
    app.config['DB_NAME'] = os.getenv('DB_NAME')

    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False

    # Initialize database connector
    from . import db_connector
    db_connector.init_app(app)

    # Register Blueprints
    from .routes import bp
    app.register_blueprint(bp)

    @app.before_request
    def restore_mysql_employee_session():
        """Restore MySQL employee session before each request."""
        employee_id = session.get('employee_id')
        if employee_id:
            try:
                db, cursor = db_connector.get_db()
                cursor.execute("SET @current_user_employee_id = %s", (employee_id,))
            except Exception as e:
                print(f"MySQL session restore failed: {e}")

    return app


app = create_app()
