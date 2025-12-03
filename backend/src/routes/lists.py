from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from decorators.board import require_board_access
from src.models import List, Board, Card, BoardMember
from src.db import db
from src.utils.position_helpers import (
    adjust_positions_on_insert,
    validate_position,
    compact_positions_on_delete,
    reorder_on_move,
)

lists_bp = Blueprint("lists", __name__, url_prefix="/lists")


@lists_bp.route("/<int:list_id>", methods=["GET"])
@jwt_required()
@require_board_access
def get_list(list_id):
    """Obtener una lista específica"""
    current_user_id = get_jwt_identity()
    list_obj = List.query.get(list_id)
    if not list_obj:
        return jsonify({"error": "List not found"}), 404

    return jsonify(list_obj.to_dict()), 200


@lists_bp.route("/", methods=["POST"])
@jwt_required()
@require_board_access
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

    # Validar y obtener posición
    position = validate_position(List, "board_id", board_id, position)

    # Ajustar posiciones de listas existentes
    adjust_positions_on_insert(List, "board_id", board_id, position)

    new_list = List(title=title, board_id=board_id, position=position)
    db.session.add(new_list)
    db.session.commit()
    return jsonify(new_list.to_dict()), 201


@lists_bp.route("/<int:list_id>", methods=["PUT"])
@jwt_required()
@require_board_access
def update_list(list_id):
    list_obj = List.query.get(list_id)
    if not list_obj:
        return jsonify({"error": "List not found"}), 404

    data = request.get_json()
    old_board_id = list_obj.board_id
    old_position = list_obj.position

    if "title" in data:
        list_obj.title = data["title"]

    # Manejar cambios de board y/o posición
    new_board_id = data.get("board_id", old_board_id)
    new_position = data.get("position")

    if "board_id" in data:
        # Verificar que el nuevo board existe
        new_board = Board.query.get(data["board_id"])
        if not new_board:
            return jsonify({"error": "Board not found"}), 404

    # Si cambió el board o la posición, reordenar
    if new_board_id != old_board_id or (
        new_position is not None and new_position != old_position
    ):
        if new_position is None:
            new_position = validate_position(List, "board_id", new_board_id, None)
        else:
            new_position = validate_position(
                List, "board_id", new_board_id, new_position
            )

        reorder_on_move(
            List,
            "board_id",
            list_obj,
            old_board_id,
            old_position,
            new_board_id,
            new_position,
        )
        list_obj.board_id = new_board_id
        list_obj.position = new_position

    db.session.commit()
    return jsonify(list_obj.to_dict()), 200


@lists_bp.route("/<int:list_id>", methods=["DELETE"])
@jwt_required()
@require_board_access
def delete_list(list_id):
    list_obj = List.query.get(list_id)
    if not list_obj:
        return jsonify({"error": "List not found"}), 404

    board_id = list_obj.board_id
    position = list_obj.position

    db.session.delete(list_obj)
    # Compactar posiciones de las listas restantes
    compact_positions_on_delete(List, "board_id", board_id, position)

    db.session.commit()
    return jsonify({"message": "List deleted successfully"}), 200


@lists_bp.route("/<int:list_id>/cards", methods=["GET"])
@jwt_required()
@require_board_access
def get_list_cards(list_id):
    """Obtener tarjetas de una lista"""
    current_user_id = get_jwt_identity()
    list_obj = List.query.get(list_id)
    if not list_obj:
        return jsonify({"error": "List not found"}), 404

    cards = [card.to_dict() for card in list_obj.cards]
    return jsonify(cards), 200


@lists_bp.route("/<int:list_id>/cards", methods=["POST"])
@jwt_required()
@require_board_access
def add_card_to_list(list_id):
    """Agregar tarjeta a una lista"""
    current_user_id = get_jwt_identity()
    list_obj = List.query.get(list_id)
    if not list_obj:
        return jsonify({"error": "List not found"}), 404

    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    position = data.get("position")
    due_date = data.get("due_date")

    if not title:
        return jsonify({"error": "Title is required"}), 400

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


@lists_bp.route("/<int:list_id>/move", methods=["PUT"])
@jwt_required()
@require_board_access
def move_list(list_id):
    """Mover una lista a otro board y/o posición"""
    current_user_id = get_jwt_identity()
    list_obj = List.query.get(list_id)
    if not list_obj:
        return jsonify({"error": "List not found"}), 404

    data = request.get_json()
    new_board_id = data.get("board_id")
    new_position = data.get("position")

    if new_board_id is None and new_position is None:
        return jsonify({"error": "board_id or position is required"}), 400

    old_board_id = list_obj.board_id
    old_position = list_obj.position

    # Usar board_id actual si no se proporciona uno nuevo
    if new_board_id is None:
        new_board_id = old_board_id
    else:
        # Verificar que el nuevo board existe
        new_board = Board.query.get(new_board_id)
        if not new_board:
            return jsonify({"error": "New board not found"}), 404

    # Validar y obtener posición
    new_position = validate_position(List, "board_id", new_board_id, new_position)

    # Solo reordenar si realmente cambia algo
    if new_board_id != old_board_id or new_position != old_position:
        reorder_on_move(
            List,
            "board_id",
            list_obj,
            old_board_id,
            old_position,
            new_board_id,
            new_position,
        )
        list_obj.board_id = new_board_id
        list_obj.position = new_position

    db.session.commit()
    return jsonify(list_obj.to_dict()), 200
