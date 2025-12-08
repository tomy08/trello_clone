from functools import wraps
from flask import request
from flask_jwt_extended import get_jwt_identity
from werkzeug.exceptions import BadRequest, NotFound, Forbidden
from src.models import BoardMember, Board, List, Card


def require_board_access(f):
    """Check if the current user has access to the board (as owner or member)."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        board_id = kwargs.get("board_id") or kwargs.get("id")

        # Si no está en kwargs, intentar obtenerlo de los query params
        if not board_id:
            board_id = request.args.get("board_id", type=int)

        # Si no está en query params, intentar obtenerlo del request body
        if not board_id:
            data = request.get_json(silent=True)
            if data:
                board_id = data.get("board_id")

        # Si aún no hay board_id, intentar obtenerlo de list_id
        if not board_id:
            list_id = kwargs.get("list_id")
            if not list_id and data:
                list_id = data.get("list_id")

            if list_id:
                list_obj = List.query.get(list_id)
                if list_obj:
                    board_id = list_obj.board_id

        # Si aún no hay board_id, intentar obtenerlo de card_id
        if not board_id:
            card_id = kwargs.get("card_id")
            if card_id:
                card_obj = Card.query.get(card_id)
                if card_obj and card_obj.list:
                    board_id = card_obj.list.board_id

        if not board_id:
            raise BadRequest("Board ID required")

        board = Board.query.get(board_id)
        if not board:
            raise NotFound("Board not found")

        is_owner = board.owner_id == current_user_id
        is_member = (
            BoardMember.query.filter_by(
                board_id=board_id, user_id=current_user_id
            ).first()
            is not None
        )

        if not (is_owner or is_member):
            raise Forbidden("You do not have permission to access this board")

        return f(*args, **kwargs)

    return decorated_function


def require_board_owner(f):
    """Check if the current user is the owner of the board."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        board_id = kwargs.get("board_id") or kwargs.get("id")

        # Si no está en kwargs, intentar obtenerlo del request body
        if not board_id:
            data = request.get_json(silent=True)
            if data:
                board_id = data.get("board_id")

        if not board_id:
            raise BadRequest("Board ID required")

        board = Board.query.get(board_id)
        if not board:
            raise NotFound("Board not found")

        is_owner = board.owner_id == current_user_id

        if not is_owner:
            raise Forbidden("You do not have permission to access this route")

        return f(*args, **kwargs)

    return decorated_function
