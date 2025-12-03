from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import Card, List, Board, BoardMember
from src.db import db

cards_bp = Blueprint("cards", __name__, url_prefix="/cards")


def verify_list_access(list_id, user_id):
    """Helper para verificar acceso a una lista a través del board"""
    list_obj = List.query.get(list_id)
    if not list_obj:
        return False, "List not found"

    board = list_obj.board
    if not board:
        return False, "Board not found"

    is_owner = board.owner_id == user_id
    is_member = (
        BoardMember.query.filter_by(board_id=board.id, user_id=user_id).first()
        is not None
    )

    if not (is_owner or is_member):
        return False, "You do not have permission to access this board"

    return True, None


@cards_bp.route("/<int:card_id>", methods=["GET"])
@jwt_required()
def get_card(card_id):
    """Obtener una tarjeta específica"""
    current_user_id = get_jwt_identity()
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    # Verificar acceso a través de la lista
    has_access, error = verify_list_access(card.list_id, current_user_id)
    if not has_access:
        return jsonify({"error": error}), 403

    return jsonify(card.to_dict()), 200


@cards_bp.route("/", methods=["POST"])
@jwt_required()
def create_card():
    """Crear una nueva tarjeta"""
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    list_id = data.get("list_id")
    position = data.get("position")
    due_date = data.get("due_date")

    if not title or list_id is None:
        return jsonify({"error": "Title and list_id are required"}), 400

    # Verificar que la lista existe
    list_obj = List.query.get(list_id)
    if not list_obj:
        return jsonify({"error": "List not found"}), 404

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


@cards_bp.route("/<int:card_id>", methods=["PUT"])
def update_card(card_id):
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    data = request.get_json()

    if "title" in data:
        card.title = data["title"]
    if "description" in data:
        card.description = data["description"]
    if "position" in data:
        card.position = data["position"]
    if "due_date" in data:
        card.due_date = data["due_date"]
    if "archived" in data:
        card.archived = data["archived"]
    if "list_id" in data:
        # Verificar que la nueva lista existe
        new_list = List.query.get(data["list_id"])
        if not new_list:
            return jsonify({"error": "New list not found"}), 404
        card.list_id = data["list_id"]

    db.session.commit()
    return jsonify(card.to_dict()), 200


@cards_bp.route("/<int:card_id>", methods=["DELETE"])
def delete_card(card_id):
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    db.session.delete(card)
    db.session.commit()
    return jsonify({"message": "Card deleted successfully"}), 200


@cards_bp.route("/<int:card_id>/archive", methods=["PUT"])
@jwt_required()
def archive_card(card_id):
    """Archivar una tarjeta"""
    current_user_id = get_jwt_identity()
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    # Verificar acceso
    has_access, error = verify_list_access(card.list_id, current_user_id)
    if not has_access:
        return jsonify({"error": error}), 403

    card.archived = True
    db.session.commit()
    return jsonify(card.to_dict()), 200


@cards_bp.route("/<int:card_id>/unarchive", methods=["PUT"])
@jwt_required()
def unarchive_card(card_id):
    """Desarchivar una tarjeta"""
    current_user_id = get_jwt_identity()
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    # Verificar acceso
    has_access, error = verify_list_access(card.list_id, current_user_id)
    if not has_access:
        return jsonify({"error": error}), 403

    card.archived = False
    db.session.commit()
    return jsonify(card.to_dict()), 200


@cards_bp.route("/<int:card_id>/move", methods=["PUT"])
@jwt_required()
def move_card(card_id):
    """Mover una tarjeta a otra lista y/o posición"""
    current_user_id = get_jwt_identity()
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    # Verificar acceso a la lista actual
    has_access, error = verify_list_access(card.list_id, current_user_id)
    if not has_access:
        return jsonify({"error": error}), 403

    data = request.get_json()
    new_list_id = data.get("list_id")
    new_position = data.get("position")

    if new_list_id is None and new_position is None:
        return jsonify({"error": "list_id or position is required"}), 400

    if new_list_id is not None:
        # Verificar acceso a la nueva lista
        has_access_new, error_new = verify_list_access(new_list_id, current_user_id)
        if not has_access_new:
            return jsonify({"error": error_new}), 403
        card.list_id = new_list_id

    if new_position is not None:
        card.position = new_position

    db.session.commit()
    return jsonify(card.to_dict()), 200
