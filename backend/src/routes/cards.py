from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from decorators.board import require_board_access
from src.models import Card, List
from src.db import db
from src.utils.position_helpers import (
    adjust_positions_on_insert,
    validate_position,
    compact_positions_on_delete,
    reorder_on_move,
)

cards_bp = Blueprint("cards", __name__, url_prefix="/cards")


@cards_bp.route("/<int:card_id>", methods=["GET"])
@jwt_required()
@require_board_access
def get_card(card_id):
    """Obtener una tarjeta específica"""
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    return jsonify(card.to_dict()), 200


@cards_bp.route("/", methods=["POST"])
@jwt_required()
@require_board_access
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

    # Validar y obtener posición
    position = validate_position(Card, "list_id", list_id, position)

    # Ajustar posiciones de cards existentes
    adjust_positions_on_insert(Card, "list_id", list_id, position)

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
@jwt_required()
@require_board_access
def update_card(card_id):
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    data = request.get_json()
    old_list_id = card.list_id
    old_position = card.position

    if "title" in data:
        card.title = data["title"]
    if "description" in data:
        card.description = data["description"]
    if "due_date" in data:
        card.due_date = data["due_date"]
    if "archived" in data:
        card.archived = data["archived"]

    # Manejar cambios de lista y/o posición
    new_list_id = data.get("list_id", old_list_id)
    new_position = data.get("position")

    if "list_id" in data:
        # Verificar que la nueva lista existe
        new_list = List.query.get(data["list_id"])
        if not new_list:
            return jsonify({"error": "New list not found"}), 404

    # Si cambió la lista o la posición, reordenar
    if new_list_id != old_list_id or (
        new_position is not None and new_position != old_position
    ):
        if new_position is None:
            new_position = validate_position(Card, "list_id", new_list_id, None)
        else:
            new_position = validate_position(Card, "list_id", new_list_id, new_position)

        reorder_on_move(
            Card, "list_id", card, old_list_id, old_position, new_list_id, new_position
        )
        card.list_id = new_list_id
        card.position = new_position

    db.session.commit()
    return jsonify(card.to_dict()), 200


@cards_bp.route("/<int:card_id>", methods=["DELETE"])
@jwt_required()
@require_board_access
def delete_card(card_id):
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    list_id = card.list_id
    position = card.position

    db.session.delete(card)
    # Compactar posiciones de las cards restantes
    compact_positions_on_delete(Card, "list_id", list_id, position)

    db.session.commit()
    return jsonify({"message": "Card deleted successfully"}), 200


@cards_bp.route("/<int:card_id>/archive", methods=["PUT"])
@jwt_required()
@require_board_access
def archive_card(card_id):
    """Archivar una tarjeta"""
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    card.archived = True
    db.session.commit()
    return jsonify(card.to_dict()), 200


@cards_bp.route("/<int:card_id>/unarchive", methods=["PUT"])
@jwt_required()
@require_board_access
def unarchive_card(card_id):
    """Desarchivar una tarjeta"""
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    card.archived = False
    db.session.commit()
    return jsonify(card.to_dict()), 200


@cards_bp.route("/<int:card_id>/move", methods=["PUT"])
@jwt_required()
@require_board_access
def move_card(card_id):
    """Mover una tarjeta a otra lista y/o posición"""
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    data = request.get_json()
    new_list_id = data.get("list_id")
    new_position = data.get("position")

    if new_list_id is None and new_position is None:
        return jsonify({"error": "list_id or position is required"}), 400

    old_list_id = card.list_id
    old_position = card.position

    # Usar list_id actual si no se proporciona uno nuevo
    if new_list_id is None:
        new_list_id = old_list_id
    else:
        # Verificar que la nueva lista existe
        new_list = List.query.get(new_list_id)
        if not new_list:
            return jsonify({"error": "New list not found"}), 404

    # Validar y obtener posición
    new_position = validate_position(Card, "list_id", new_list_id, new_position)

    # Solo reordenar si realmente cambia algo
    if new_list_id != old_list_id or new_position != old_position:
        reorder_on_move(
            Card, "list_id", card, old_list_id, old_position, new_list_id, new_position
        )
        card.list_id = new_list_id
        card.position = new_position

    db.session.commit()
    return jsonify(card.to_dict()), 200
