"""Application entry point."""

import os

from dotenv import load_dotenv

from app import create_app

# Load environment variables from .env file
load_dotenv()

# Determine configuration based on environment
config_name = os.environ.get("FLASK_ENV", "development")
app = create_app(config_name)

if __name__ == "__main__":
    debug = config_name == "development"
    app.run(debug=debug)
