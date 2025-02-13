# run.py

from app import create_app
from app.config import Config  # Import the Config class

app = create_app(Config)  # Use the Config class

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)