from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restx import Api
from config import Config
from src.db import db
from flask_jwt_extended import JWTManager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configuración de CORS más permisiva
    CORS(app, 
         resources={r"/*": {
             "origins": ["http://localhost:3000"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "expose_headers": ["Content-Type", "Authorization"],
             "max_age": 3600
         }})

    # Configuración para Flask-RESTX
    app.config["RESTX_MASK_SWAGGER"] = False
    app.config["ERROR_404_HELP"] = False
    app.url_map.strict_slashes = False  # Evita redirects por trailing slash

    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)

    # Inicializar API con documentación Swagger
    api = Api(
        app,
        version="1.0",
        title="Trello Clone API",
        description="API REST completa para un clon de Trello con autenticación JWT",
        doc="/docs",
        authorizations={
            "Bearer": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": 'JWT Authorization header. Example: "Bearer {token}"',
            }
        },
        security="Bearer",
    )

    # Importar y registrar namespaces
    from src.routes.auth import auth_ns
    from src.routes.boards import boards_ns
    from src.routes.lists import lists_ns
    from src.routes.cards import cards_ns

    api.add_namespace(auth_ns, path="/auth")
    api.add_namespace(boards_ns, path="/boards")
    api.add_namespace(lists_ns, path="/lists")
    api.add_namespace(cards_ns, path="/cards")

    # Manejar explícitamente las peticiones OPTIONS (preflight)
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,PATCH')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    # Health check endpoint
    @app.route("/health", methods=["GET"])
    def health_check():
        return {"status": "ok"}, 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
