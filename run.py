# parking_management_app/run.py

from app import app
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get FLASK_ENV from environment, default to 'development'
FLASK_ENV = os.getenv('FLASK_ENV', 'development')

if __name__ == '__main__':
    # The app.run() function is used to start the Flask development server.
    app.run(
        debug=(FLASK_ENV == 'development'), # Enable debug mode if FLASK_ENV is 'development'
        host='0.0.0.0', # Listen on all public IPs (useful for testing across networks/devices)
        port=5000       # Default Flask port
    )