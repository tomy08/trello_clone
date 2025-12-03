from flask import Blueprint, request, jsonify
from src.models import Board, BoardMember
from src.db import db

boards_bp = Blueprint("boards", __name__, url_prefix="/boards")


@boards_bp.route("/", methods=["GET"])
def get_all_boards():
    boards = Board.query.all()
    return jsonify([board.to_dict() for board in boards]), 200


@boards_bp.route("/", methods=["POST"])
def create_board():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    owner_id = data.get("owner_id")
    if not title or not owner_id:
        return jsonify({"error": "Title and owner_id are required"}), 400
    new_board = Board(title=title, description=description, owner_id=owner_id)
    db.session.add(new_board)
    db.session.commit()
    return jsonify(new_board.to_dict()), 201


@boards_bp.route("/<int:board_id>", methods=["GET"])
def get_board(board_id):
    board = Board.query.get(board_id)
    if not board:
        return jsonify({"error": "Board not found"}), 404
    return jsonify(board.to_dict()), 200


@boards_bp.route("/<int:board_id>", methods=["PUT"])
def update_board(board_id):
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
def get_member_boards(member_id):
    boards = (
        Board.query.join(BoardMember).filter(BoardMember.user_id == member_id).all()
    )
    return jsonify([board.to_dict() for board in boards]), 200


@boards_bp.route("/<int:board_id>/members", methods=["GET"])
def get_board_members(board_id):
    board = Board.query.get(board_id)
    if not board:
        return jsonify({"error": "Board not found"}), 404
    members = [member.to_dict() for member in board.members]
    return jsonify(members), 200


@boards_bp.route("/<int:board_id>/members", methods=["POST"])
def add_members(board_id):
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
def remove_member(board_id, user_id):
    member = BoardMember.query.filter_by(board_id=board_id, user_id=user_id).first()
    if not member:
        return jsonify({"error": "Member not found"}), 404
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member removed successfully"}), 200


@boards_bp.route("/<int:board_id>/lists", methods=["GET"])
def get_board_lists(board_id):
    board = Board.query.get(board_id)
    if not board:
        return {"error": "Board not found"}, 404
    lists = [lst.to_dict() for lst in board.lists]
    return jsonify(lists), 200


@boards_bp.route("/<int:board_id>", methods=["DELETE"])
def delete_board(board_id):
    board = Board.query.get(board_id)
    if not board:
        return jsonify({"error": "Board not found"}), 404
    db.session.delete(board)
    db.session.commit()
    return jsonify({"message": "Board deleted successfully"}), 200
