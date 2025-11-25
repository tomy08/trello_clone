from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from src.models.user import User
from src.db import db
import re

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def is_valid_email(email):
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email) is not None


def validate_password(password):
    """Validate password length > 5."""
    return len(password) > 5


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"msg": "Missing username, email, or password"}), 400

    if not is_valid_email(email):
        return jsonify({"msg": "Invalid email format"}), 400

    if not validate_password(password):
        return jsonify({"msg": "Password must be longer than 5 characters"}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"msg": "Username or email already exists"}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()

        access_token = create_access_token(identity=new_user.id)
        refresh_token = create_refresh_token(identity=new_user.id)

        return (
            jsonify(
                {
                    "msg": "User registered successfully",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error registering user", "error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"msg": "Invalid username or password"}), 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return (
        jsonify(
            {
                "msg": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        ),
        200,
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({"access_token": new_access_token}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify(user.to_dict()), 200
