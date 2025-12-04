from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from src.models.user import User
from src.db import db
import re

# Crear namespace para auth
auth_ns = Namespace("auth", description="Operaciones de autenticación")

# Definir modelos para documentación
auth_register_model = auth_ns.model(
    "AuthRegister",
    {
        "username": fields.String(
            required=True, description="Nombre de usuario", example="johndoe"
        ),
        "email": fields.String(
            required=True, description="Email del usuario", example="john@example.com"
        ),
        "password": fields.String(
            required=True,
            description="Contraseña (mínimo 6 caracteres)",
            example="password123",
        ),
    },
)

auth_login_model = auth_ns.model(
    "AuthLogin",
    {
        "username": fields.String(
            required=True, description="Nombre de usuario", example="johndoe"
        ),
        "password": fields.String(
            required=True, description="Contraseña", example="password123"
        ),
    },
)

auth_response_model = auth_ns.model(
    "AuthResponse",
    {
        "msg": fields.String(description="Mensaje de respuesta"),
        "access_token": fields.String(description="Token de acceso JWT"),
        "refresh_token": fields.String(description="Token de refresco JWT"),
    },
)

refresh_response_model = auth_ns.model(
    "RefreshResponse",
    {"access_token": fields.String(description="Nuevo token de acceso JWT")},
)

user_response_model = auth_ns.model(
    "UserResponse",
    {
        "id": fields.Integer(description="ID del usuario"),
        "username": fields.String(description="Nombre de usuario"),
        "email": fields.String(description="Email del usuario"),
        "created_at": fields.DateTime(description="Fecha de creación"),
    },
)

error_model = auth_ns.model(
    "Error", {"msg": fields.String(description="Mensaje de error")}
)


def is_valid_email(email):
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email) is not None


def validate_password(password):
    """Validate password length > 5."""
    return len(password) > 5


@auth_ns.route("/register")
class Register(Resource):
    @auth_ns.doc(
        "register_user", description="Registrar un nuevo usuario en el sistema"
    )
    @auth_ns.expect(auth_register_model, validate=True)
    @auth_ns.response(201, "Usuario registrado exitosamente", auth_response_model)
    @auth_ns.response(400, "Datos inválidos", error_model)
    @auth_ns.response(409, "Usuario o email ya existe", error_model)
    @auth_ns.response(500, "Error interno del servidor", error_model)
    def post(self):
        """Registrar un nuevo usuario"""
        data = request.get_json()

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            auth_ns.abort(400, "Missing username, email, or password")

        if not is_valid_email(email):
            auth_ns.abort(400, "Invalid email format")

        if not validate_password(password):
            auth_ns.abort(400, "Password must be longer than 5 characters")

        if User.query.filter(
            (User.username == username) | (User.email == email)
        ).first():
            auth_ns.abort(409, "Username or email already exists")

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()

            access_token = create_access_token(identity=new_user.id)
            refresh_token = create_refresh_token(identity=new_user.id)

            return {
                "msg": "User registered successfully",
                "access_token": access_token,
                "refresh_token": refresh_token,
            }, 201
        except Exception as e:
            db.session.rollback()
            auth_ns.abort(500, f"Error registering user: {str(e)}")


@auth_ns.route("/login")
class Login(Resource):
    @auth_ns.doc("login_user", description="Iniciar sesión con credenciales de usuario")
    @auth_ns.expect(auth_login_model, validate=True)
    @auth_ns.response(200, "Login exitoso", auth_response_model)
    @auth_ns.response(400, "Datos faltantes", error_model)
    @auth_ns.response(401, "Credenciales inválidas", error_model)
    def post(self):
        """Iniciar sesión"""
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            auth_ns.abort(400, "Missing username or password")

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            auth_ns.abort(401, "Invalid username or password")

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return {
            "msg": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, 200


@auth_ns.route("/refresh")
class Refresh(Resource):
    @auth_ns.doc(
        "refresh_token",
        description="Refrescar el token de acceso usando el refresh token",
        security="Bearer",
    )
    @auth_ns.response(200, "Token refrescado exitosamente", refresh_response_model)
    @auth_ns.response(401, "Token inválido o expirado", error_model)
    @jwt_required(refresh=True)
    def post(self):
        """Refrescar token de acceso"""
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user)
        return {"access_token": new_access_token}, 200


@auth_ns.route("/me")
class Me(Resource):
    @auth_ns.doc(
        "get_current_user",
        description="Obtener información del usuario autenticado",
        security="Bearer",
    )
    @auth_ns.response(200, "Usuario obtenido exitosamente", user_response_model)
    @auth_ns.response(401, "No autorizado", error_model)
    @auth_ns.response(404, "Usuario no encontrado", error_model)
    @jwt_required()
    def get(self):
        """Obtener información del usuario actual"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            auth_ns.abort(404, "User not found")

        return user.to_dict(), 200
