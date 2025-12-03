from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import Board, BoardMember
from src.db import db
from src.decorators import require_board_access, require_board_owner

boards_bp = Blueprint("boards", __name__, url_prefix="/boards")


@boards_bp.route("/", methods=["GET"])
@jwt_required()
def get_all_boards():
    """Obtener todos los boards del usuario autenticado"""
    current_user_id = get_jwt_identity()

    # Boards donde es owner
    owned_boards = Board.query.filter_by(owner_id=current_user_id).all()

    # Boards donde es miembro
    memberships = BoardMember.query.filter_by(user_id=current_user_id).all()
    member_boards = [m.board for m in memberships]

    # Combinar y eliminar duplicados
    all_boards = owned_boards + [b for b in member_boards if b not in owned_boards]

    return jsonify([board.to_dict() for board in all_boards]), 200


@boards_bp.route("/", methods=["POST"])
@jwt_required()
def create_board():
    """Crear un nuevo board"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    title = data.get("title")
    description = data.get("description", "")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    new_board = Board(title=title, description=description, owner_id=current_user_id)
    db.session.add(new_board)
    db.session.commit()
    return jsonify(new_board.to_dict()), 201


@boards_bp.route("/<int:board_id>", methods=["GET"])
@jwt_required()
@require_board_access
def get_board(board_id):
    """Obtener un board específico"""
    board = Board.query.get(board_id)
    if not board:
        return jsonify({"error": "Board not found"}), 404
    return jsonify(board.to_dict()), 200


@boards_bp.route("/<int:board_id>", methods=["PUT"])
@jwt_required()
@require_board_access
def update_board(board_id):
    """Actualizar un board"""
    data = request.get_json()
    board = Board.query.get(board_id)
    if not board:
        return jsonify({"error": "Board not found"}), 404
    title = data.get("title")
    description = data.get("description")
    if title:
        board.title = title
    if description:
        board.description = description
    db.session.commit()
    return jsonify(board.to_dict()), 200


@boards_bp.route("/<int:member_id>/boards", methods=["GET"])
@jwt_required()
def get_member_boards(member_id):
    """Obtener boards de un usuario (solo si es el mismo usuario autenticado)"""
    current_user_id = get_jwt_identity()

    # Solo permitir ver los propios boards o si se implementa lógica de amigos
    if current_user_id != member_id:
        return jsonify({"error": "Not authorized to view other users' boards"}), 403

    boards = (
        Board.query.join(BoardMember).filter(BoardMember.user_id == member_id).all()
    )
    return jsonify([board.to_dict() for board in boards]), 200


@boards_bp.route("/<int:board_id>/members", methods=["GET"])
@jwt_required()
@require_board_access
def get_board_members(board_id):
    """Obtener miembros de un board"""
    board = Board.query.get(board_id)
    if not board:
        return jsonify({"error": "Board not found"}), 404
    members = [member.to_dict() for member in board.members]
    return jsonify(members), 200


@boards_bp.route("/<int:board_id>/members", methods=["POST"])
@jwt_required()
@require_board_owner
def add_members(board_id):
    """Agregar miembros a un board (solo owner)"""
    data = request.get_json()
    user_ids = data.get("user_ids", [])
    if not user_ids:
        return jsonify({"error": "user_ids list is required"}), 400
    board = Board.query.get(board_id)
    if not board:
        return jsonify({"error": "Board not found"}), 404
    for user_id in user_ids:
        existing_member = BoardMember.query.filter_by(
            board_id=board_id, user_id=user_id
        ).first()
        if not existing_member:
            new_member = BoardMember(board_id=board_id, user_id=user_id)
            db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "Members added successfully"}), 201


@boards_bp.route("/<int:board_id>/members/<int:user_id>", methods=["DELETE"])
@jwt_required()
@require_board_owner
def remove_member(board_id, user_id):
    """Remover un miembro de un board (solo owner)"""
    member = BoardMember.query.filter_by(board_id=board_id, user_id=user_id).first()
    if not member:
        return jsonify({"error": "Member not found"}), 404
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member removed successfully"}), 200


@boards_bp.route("/<int:board_id>/lists", methods=["GET"])
@jwt_required()
@require_board_access
def get_board_lists(board_id):
    """Obtener listas de un board"""
    board = Board.query.get(board_id)
    if not board:
        return {"error": "Board not found"}, 404
    lists = [lst.to_dict() for lst in board.lists]
    return jsonify(lists), 200


@boards_bp.route("/<int:board_id>", methods=["DELETE"])
@jwt_required()
@require_board_owner
def delete_board(board_id):
    """Eliminar un board (solo owner)"""
    board = Board.query.get(board_id)
    if not board:
        return jsonify({"error": "Board not found"}), 404
    db.session.delete(board)
    db.session.commit()
    return jsonify({"message": "Board deleted successfully"}), 200
