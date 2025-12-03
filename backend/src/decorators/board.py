from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from src.models import BoardMember, Board


def require_board_access(f):
    """Check if the current user has access to the board (as owner or member)."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        board_id = kwargs.get("board_id") or kwargs.get("id")

        if not board_id:
            return jsonify({"error": "Board ID required"}), 400

        board = Board.query.get(board_id)
        if not board:
            return jsonify({"error": "Board not found"}), 404

        is_owner = board.owner_id == current_user_id
        is_member = (
            BoardMember.query.filter_by(
                board_id=board_id, user_id=current_user_id
            ).first()
            is not None
        )

        if not (is_owner or is_member):
            return (
                jsonify({"error": "You do not have permission to access this board"}),
                403,
            )

        return f(*args, **kwargs)

    return decorated_function


def require_board_owner(f):
    """Check if the current user is the owner of the board."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        board_id = kwargs.get("board_id") or kwargs.get("id")

        if not board_id:
            return jsonify({"error": "Board ID required"}), 400

        board = Board.query.get(board_id)
        if not board:
            return jsonify({"error": "Board not found"}), 404

        is_owner = board.owner_id == current_user_id

        if not (is_owner):
            return (
                jsonify({"error": "You do not have permission to access this route"}),
                403,
            )

        return f(*args, **kwargs)

    return decorated_function
