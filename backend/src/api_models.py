"""
API models for Flask-RESTX documentation
"""

from flask_restx import fields, Model


def get_api_models(api):
    """Define all API models for Swagger documentation"""

    # Auth models
    auth_register = api.model(
        "AuthRegister",
        {
            "username": fields.String(
                required=True, description="Username", example="johndoe"
            ),
            "email": fields.String(
                required=True, description="Email address", example="john@example.com"
            ),
            "password": fields.String(
                required=True,
                description="Password (min 6 characters)",
                example="password123",
            ),
        },
    )

    auth_login = api.model(
        "AuthLogin",
        {
            "username": fields.String(
                required=True, description="Username", example="johndoe"
            ),
            "password": fields.String(
                required=True, description="Password", example="password123"
            ),
        },
    )

    auth_response = api.model(
        "AuthResponse",
        {
            "msg": fields.String(description="Response message"),
            "access_token": fields.String(description="JWT access token"),
            "refresh_token": fields.String(description="JWT refresh token"),
        },
    )

    refresh_response = api.model(
        "RefreshResponse",
        {"access_token": fields.String(description="New JWT access token")},
    )

    # User model
    user_model = api.model(
        "User",
        {
            "id": fields.Integer(description="User ID"),
            "username": fields.String(description="Username"),
            "email": fields.String(description="Email address"),
            "created_at": fields.DateTime(description="Creation timestamp"),
        },
    )

    # Board models
    board_create = api.model(
        "BoardCreate",
        {
            "title": fields.String(
                required=True, description="Board title", example="My Project Board"
            ),
            "description": fields.String(
                description="Board description", example="Project management board"
            ),
        },
    )

    board_update = api.model(
        "BoardUpdate",
        {
            "title": fields.String(description="Board title"),
            "description": fields.String(description="Board description"),
        },
    )

    board_member = api.model(
        "BoardMember",
        {
            "id": fields.Integer(description="Member ID"),
            "user_id": fields.Integer(description="User ID"),
            "board_id": fields.Integer(description="Board ID"),
            "role": fields.String(description="Member role"),
            "added_at": fields.DateTime(description="When member was added"),
        },
    )

    board_model = api.model(
        "Board",
        {
            "id": fields.Integer(description="Board ID"),
            "title": fields.String(description="Board title"),
            "description": fields.String(description="Board description"),
            "owner_id": fields.Integer(description="Owner user ID"),
            "created_at": fields.DateTime(description="Creation timestamp"),
            "updated_at": fields.DateTime(description="Last update timestamp"),
        },
    )

    add_members = api.model(
        "AddMembers",
        {
            "user_ids": fields.List(
                fields.Integer,
                required=True,
                description="List of user IDs to add",
                example=[1, 2, 3],
            )
        },
    )

    # List models
    list_create = api.model(
        "ListCreate",
        {
            "title": fields.String(
                required=True, description="List title", example="To Do"
            ),
            "board_id": fields.Integer(
                required=True, description="Board ID", example=1
            ),
            "position": fields.Float(description="Position in board", example=1.0),
        },
    )

    list_update = api.model(
        "ListUpdate",
        {
            "title": fields.String(description="List title"),
            "board_id": fields.Integer(description="Board ID"),
            "position": fields.Float(description="Position in board"),
        },
    )

    list_model = api.model(
        "List",
        {
            "id": fields.Integer(description="List ID"),
            "title": fields.String(description="List title"),
            "board_id": fields.Integer(description="Board ID"),
            "position": fields.Float(description="Position in board"),
            "created_at": fields.DateTime(description="Creation timestamp"),
        },
    )

    # Card models
    card_create = api.model(
        "CardCreate",
        {
            "title": fields.String(
                required=True,
                description="Card title",
                example="Implement login feature",
            ),
            "description": fields.String(
                description="Card description",
                example="Create login form and API endpoint",
            ),
            "list_id": fields.Integer(required=True, description="List ID", example=1),
            "position": fields.Float(description="Position in list", example=1.0),
            "due_date": fields.DateTime(description="Due date"),
        },
    )

    card_update = api.model(
        "CardUpdate",
        {
            "title": fields.String(description="Card title"),
            "description": fields.String(description="Card description"),
            "list_id": fields.Integer(description="List ID"),
            "position": fields.Float(description="Position in list"),
            "due_date": fields.DateTime(description="Due date"),
            "archived": fields.Boolean(description="Archive status"),
        },
    )

    card_model = api.model(
        "Card",
        {
            "id": fields.Integer(description="Card ID"),
            "title": fields.String(description="Card title"),
            "description": fields.String(description="Card description"),
            "list_id": fields.Integer(description="List ID"),
            "position": fields.Float(description="Position in list"),
            "due_date": fields.DateTime(description="Due date"),
            "archived": fields.Boolean(description="Archive status"),
            "created_at": fields.DateTime(description="Creation timestamp"),
        },
    )

    # Error model
    error_model = api.model(
        "Error",
        {
            "error": fields.String(description="Error message"),
            "msg": fields.String(description="Error message"),
        },
    )

    return {
        "auth_register": auth_register,
        "auth_login": auth_login,
        "auth_response": auth_response,
        "refresh_response": refresh_response,
        "user_model": user_model,
        "board_create": board_create,
        "board_update": board_update,
        "board_member": board_member,
        "board_model": board_model,
        "add_members": add_members,
        "list_create": list_create,
        "list_update": list_update,
        "list_model": list_model,
        "card_create": card_create,
        "card_update": card_update,
        "card_model": card_model,
        "error_model": error_model,
    }
