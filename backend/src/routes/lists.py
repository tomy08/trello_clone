from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import List, Board, Card, BoardMember
from src.db import db

lists_bp = Blueprint("lists", __name__, url_prefix="/lists")


def verify_board_access(board_id, user_id):
    """Helper para verificar acceso a un board"""
    board = Board.query.get(board_id)
    if not board:
        return False, "Board not found"

    is_owner = board.owner_id == user_id
    is_member = (
        BoardMember.query.filter_by(board_id=board_id, user_id=user_id).first()
        is not None
    )

    if not (is_owner or is_member):
        return False, "You do not have permission to access this board"

    return True, None


@lists_bp.route("/<int:list_id>", methods=["GET"])
@jwt_required()
def get_list(list_id):
    """Obtener una lista específica"""
    current_user_id = get_jwt_identity()
    list_obj = List.query.get(list_id)
    if not list_obj:
        return jsonify({"error": "List not found"}), 404

    # Verificar acceso al board
    has_access, error = verify_board_access(list_obj.board_id, current_user_id)
    if not has_access:
        return jsonify({"error": error}), 403

    return jsonify(list_obj.to_dict()), 200


@lists_bp.route("/", methods=["POST"])
@jwt_required()
def create_list():
    """Crear una nueva lista"""
    data = request.get_json()
    title = data.get("title")
    board_id = data.get("board_id")
    position = data.get("position")

    if not title or board_id is None:
        return jsonify({"error": "Title and board_id are required"}), 400

    # Verificar que el board existe
    board = Board.query.get(board_id)
    if not board:
        return jsonify({"error": "Board not found"}), 404

    # Si no se proporciona posición, colocar al final
    if position is None:
        max_position = (
            db.session.query(db.func.max(List.position))
            .filter_by(board_id=board_id)
            .scalar()
        )
        position = (max_position or -1) + 1

    new_list = List(title=title, board_id=board_id, position=position)
    db.session.add(new_list)
    db.session.commit()
    return jsonify(new_list.to_dict()), 201


@lists_bp.route("/<int:list_id>", methods=["PUT"])
def update_list(list_id):
    list_obj = List.query.get(list_id)
    if not list_obj:
        return jsonify({"error": "List not found"}), 404

    data = request.get_json()

    if "title" in data:
        list_obj.title = data["title"]
    if "position" in data:
        list_obj.position = data["position"]
    if "board_id" in data:
        # Verificar que el nuevo board existe
        new_board = Board.query.get(data["board_id"])
        if not new_board:
            return jsonify({"error": "Board not found"}), 404
        list_obj.board_id = data["board_id"]

    db.session.commit()
    return jsonify(list_obj.to_dict()), 200


@lists_bp.route("/<int:list_id>", methods=["DELETE"])
def delete_list(list_id):
    list_obj = List.query.get(list_id)
    if not list_obj:
        return jsonify({"error": "List not found"}), 404

    db.session.delete(list_obj)
    db.session.commit()
    return jsonify({"message": "List deleted successfully"}), 200


@lists_bp.route("/<int:list_id>/cards", methods=["GET"])
@jwt_required()
def get_list_cards(list_id):
    """Obtener tarjetas de una lista"""
    current_user_id = get_jwt_identity()
    list_obj = List.query.get(list_id)
    if not list_obj:
        return jsonify({"error": "List not found"}), 404

    # Verificar acceso al board
    has_access, error = verify_board_access(list_obj.board_id, current_user_id)
    if not has_access:
        return jsonify({"error": error}), 403

    cards = [card.to_dict() for card in list_obj.cards]
    return jsonify(cards), 200


@lists_bp.route("/<int:list_id>/cards", methods=["POST"])
@jwt_required()
def add_card_to_list(list_id):
    """Agregar tarjeta a una lista"""
    current_user_id = get_jwt_identity()
    list_obj = List.query.get(list_id)
    if not list_obj:
        return jsonify({"error": "List not found"}), 404

    # Verificar acceso al board
    has_access, error = verify_board_access(list_obj.board_id, current_user_id)
    if not has_access:
        return jsonify({"error": error}), 403

    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    position = data.get("position")
    due_date = data.get("due_date")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    # Si no se proporciona posición, colocar al final
    if position is None:
        max_position = (
            db.session.query(db.func.max(Card.position))
            .filter_by(list_id=list_id)
            .scalar()
        )
        position = (max_position or -1) + 1

    new_card = Card(
        title=title,
        description=description,
        list_id=list_id,
        position=position,
        due_date=due_date,
    )
    db.session.add(new_card)
    db.session.commit()
    return jsonify(new_card.to_dict()), 201


@lists_bp.route("/<int:list_id>/move", methods=["PUT"])
@jwt_required()
def move_list(list_id):
    """Mover una lista a otro board y/o posición"""
    current_user_id = get_jwt_identity()
    list_obj = List.query.get(list_id)
    if not list_obj:
        return jsonify({"error": "List not found"}), 404

    # Verificar acceso al board actual
    has_access, error = verify_board_access(list_obj.board_id, current_user_id)
    if not has_access:
        return jsonify({"error": error}), 403

    data = request.get_json()
    new_board_id = data.get("board_id")
    new_position = data.get("position")

    if new_board_id is None and new_position is None:
        return jsonify({"error": "board_id or position is required"}), 400

    if new_board_id is not None:
        # Verificar acceso al nuevo board
        has_access_new, error_new = verify_board_access(new_board_id, current_user_id)
        if not has_access_new:
            return jsonify({"error": error_new}), 403
        list_obj.board_id = new_board_id

    if new_position is not None:
        list_obj.position = new_position

    db.session.commit()
    return jsonify(list_obj.to_dict()), 200
