from flask import Flask, app
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from src.db import db
from src.routes import boards_bp, auth_bp


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)

    app.register_blueprint(boards_bp)
    app.register_blueprint(auth_bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
