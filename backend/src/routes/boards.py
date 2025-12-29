from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import Board, BoardMember, List, Card
from src.db import db
from src.decorators import require_board_access, require_board_owner

# Crear namespace para boards
boards_ns = Namespace("boards", description="Operaciones de tableros")

# Definir modelos para documentación
board_create_model = boards_ns.model(
    "BoardCreate",
    {
        "title": fields.String(
            required=True, description="Título del tablero", example="Mi Proyecto"
        ),
        "description": fields.String(
            description="Descripción del tablero",
            example="Tablero para gestión de proyecto",
        ),
    },
)

board_update_model = boards_ns.model(
    "BoardUpdate",
    {
        "title": fields.String(description="Título del tablero"),
        "description": fields.String(description="Descripción del tablero"),
    },
)

board_response_model = boards_ns.model(
    "BoardResponse",
    {
        "id": fields.Integer(description="ID del tablero"),
        "title": fields.String(description="Título del tablero"),
        "description": fields.String(description="Descripción del tablero"),
        "owner_id": fields.Integer(description="ID del propietario"),
        "created_at": fields.DateTime(description="Fecha de creación"),
        "updated_at": fields.DateTime(description="Fecha de actualización"),
    },
)

add_members_model = boards_ns.model(
    "AddMembers",
    {
        "user_ids": fields.List(
            fields.Integer,
            required=True,
            description="Lista de IDs de usuarios",
            example=[1, 2, 3],
        )
    },
)

member_response_model = boards_ns.model(
    "MemberResponse",
    {
        "id": fields.Integer(description="ID del miembro"),
        "user_id": fields.Integer(description="ID del usuario"),
        "board_id": fields.Integer(description="ID del tablero"),
        "role": fields.String(description="Rol del miembro"),
        "added_at": fields.DateTime(description="Fecha de adición"),
    },
)

error_model = boards_ns.model(
    "Error",
    {
        "error": fields.String(description="Mensaje de error"),
        "message": fields.String(description="Mensaje de error"),
    },
)


@boards_ns.route("/")
class BoardList(Resource):
    @boards_ns.doc(
        "get_all_boards",
        description="Obtener todos los tableros del usuario autenticado",
        security="Bearer",
    )
    @boards_ns.response(
        200, "Lista de tableros obtenida exitosamente", [board_response_model]
    )
    @boards_ns.response(401, "No autorizado", error_model)
    @jwt_required()
    def get(self):
        """Obtener todos los boards del usuario autenticado"""
        current_user_id = int(get_jwt_identity())

        # Boards donde es owner
        owned_boards = Board.query.filter_by(owner_id=current_user_id).all()

        # Boards donde es miembro
        memberships = BoardMember.query.filter_by(user_id=current_user_id).all()
        member_boards = [m.board for m in memberships]

        # Combinar y eliminar duplicados
        all_boards = owned_boards + [b for b in member_boards if b not in owned_boards]

        return [board.to_dict() for board in all_boards], 200

    @boards_ns.doc(
        "create_board", description="Crear un nuevo tablero", security="Bearer"
    )
    @boards_ns.expect(board_create_model, validate=True)
    @boards_ns.response(201, "Tablero creado exitosamente", board_response_model)
    @boards_ns.response(400, "Datos inválidos", error_model)
    @boards_ns.response(401, "No autorizado", error_model)
    @jwt_required()
    def post(self):
        """Crear un nuevo board"""
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        title = data.get("title")
        description = data.get("description", "")

        if not title:
            boards_ns.abort(400, "Title is required")

        new_board = Board(
            title=title, description=description, owner_id=current_user_id
        )
        db.session.add(new_board)
        db.session.commit()
        return new_board.to_dict(), 201


@boards_ns.route("/<int:board_id>")
@boards_ns.param("board_id", "ID del tablero")
class BoardResource(Resource):
    @boards_ns.doc(
        "get_board", description="Obtener un tablero específico", security="Bearer"
    )
    @boards_ns.response(200, "Tablero obtenido exitosamente", board_response_model)
    @boards_ns.response(401, "No autorizado", error_model)
    @boards_ns.response(404, "Tablero no encontrado", error_model)
    @jwt_required()
    @require_board_access
    def get(self, board_id):
        """Obtener un board específico"""
        board = Board.query.get(board_id)
        if not board:
            boards_ns.abort(404, "Board not found")
        return board.to_dict(), 200

    @boards_ns.doc(
        "update_board", description="Actualizar un tablero", security="Bearer"
    )
    @boards_ns.expect(board_update_model)
    @boards_ns.response(200, "Tablero actualizado exitosamente", board_response_model)
    @boards_ns.response(401, "No autorizado", error_model)
    @boards_ns.response(404, "Tablero no encontrado", error_model)
    @jwt_required()
    @require_board_access
    def put(self, board_id):
        """Actualizar un board"""
        data = request.get_json()
        board = Board.query.get(board_id)
        if not board:
            boards_ns.abort(404, "Board not found")
        title = data.get("title")
        description = data.get("description")
        if title:
            board.title = title
        if description:
            board.description = description
        db.session.commit()
        return board.to_dict(), 200

    @boards_ns.doc(
        "delete_board",
        description="Eliminar un tablero (solo propietario)",
        security="Bearer",
    )
    @boards_ns.response(200, "Tablero eliminado exitosamente")
    @boards_ns.response(401, "No autorizado", error_model)
    @boards_ns.response(
        403, "Prohibido - solo el propietario puede eliminar", error_model
    )
    @boards_ns.response(404, "Tablero no encontrado", error_model)
    @jwt_required()
    @require_board_owner
    def delete(self, board_id):
        """Eliminar un board (solo owner)"""
        board = Board.query.get(board_id)
        if not board:
            boards_ns.abort(404, "Board not found")
        db.session.delete(board)
        db.session.commit()
        return {"message": "Board deleted successfully"}, 200


@boards_ns.route("/<int:member_id>/boards")
@boards_ns.param("member_id", "ID del miembro")
class MemberBoards(Resource):
    @boards_ns.doc(
        "get_member_boards",
        description="Obtener tableros de un usuario (solo el mismo usuario)",
        security="Bearer",
    )
    @boards_ns.response(
        200, "Lista de tableros obtenida exitosamente", [board_response_model]
    )
    @boards_ns.response(401, "No autorizado", error_model)
    @boards_ns.response(
        403, "Prohibido - no puedes ver tableros de otros usuarios", error_model
    )
    @jwt_required()
    def get(self, member_id):
        """Obtener boards de un usuario (solo si es el mismo usuario autenticado)"""
        current_user_id = int(get_jwt_identity())

        # Solo permitir ver los propios boards o si se implementa lógica de amigos
        if current_user_id != member_id:
            boards_ns.abort(403, "Not authorized to view other users' boards")

        boards = (
            Board.query.join(BoardMember).filter(BoardMember.user_id == member_id).all()
        )
        return [board.to_dict() for board in boards], 200


@boards_ns.route("/<int:board_id>/lists")
@boards_ns.param("board_id", "ID del tablero")
class BoardLists(Resource):
    @boards_ns.doc(
        "get_board_lists",
        description="Obtener todas las listas y tarjetas de un tablero",
        security="Bearer",
    )
    @boards_ns.response(200, "Listas y tarjetas obtenidas exitosamente")
    @boards_ns.response(401, "No autorizado", error_model)
    @boards_ns.response(404, "Tablero no encontrado", error_model)
    @jwt_required()
    @require_board_access
    def get(self, board_id):
        """Obtener todas las listas y sus tarjetas de un board"""
        board = Board.query.get(board_id)
        if not board:
            boards_ns.abort(404, "Board not found")
        
        # Obtener todas las listas del board ordenadas por posición
        lists = List.query.filter_by(board_id=board_id).order_by(List.position).all()
        
        # Para cada lista, obtener sus tarjetas
        lists_with_cards = []
        for lst in lists:
            list_dict = lst.to_dict()
            # Obtener tarjetas de esta lista ordenadas por posición
            cards = Card.query.filter_by(list_id=lst.id).order_by(Card.position).all()
            list_dict['cards'] = [card.to_dict() for card in cards]
            lists_with_cards.append(list_dict)
        
        return lists_with_cards, 200


@boards_ns.route("/<int:board_id>/members")
@boards_ns.param("board_id", "ID del tablero")
class BoardMembers(Resource):
    @boards_ns.doc(
        "get_board_members",
        description="Obtener miembros de un tablero",
        security="Bearer",
    )
    @boards_ns.response(
        200, "Lista de miembros obtenida exitosamente", [member_response_model]
    )
    @boards_ns.response(401, "No autorizado", error_model)
    @boards_ns.response(404, "Tablero no encontrado", error_model)
    @jwt_required()
    @require_board_access
    def get(self, board_id):
        """Obtener miembros de un board"""
        board = Board.query.get(board_id)
        if not board:
            boards_ns.abort(404, "Board not found")
        members = [member.to_dict() for member in board.members]
        return members, 200

    @boards_ns.doc(
        "add_members",
        description="Agregar miembros a un tablero (solo propietario)",
        security="Bearer",
    )
    @boards_ns.expect(add_members_model, validate=True)
    @boards_ns.response(201, "Miembros agregados exitosamente")
    @boards_ns.response(400, "Datos inválidos", error_model)
    @boards_ns.response(401, "No autorizado", error_model)
    @boards_ns.response(
        403, "Prohibido - solo el propietario puede agregar miembros", error_model
    )
    @boards_ns.response(404, "Tablero no encontrado", error_model)
    @jwt_required()
    @require_board_owner
    def post(self, board_id):
        """Agregar miembros a un board (solo owner)"""
        data = request.get_json()
        user_ids = data.get("user_ids", [])
        if not user_ids:
            boards_ns.abort(400, "user_ids list is required")
        board = Board.query.get(board_id)
        if not board:
            boards_ns.abort(404, "Board not found")
        for user_id in user_ids:
            existing_member = BoardMember.query.filter_by(
                board_id=board_id, user_id=user_id
            ).first()
            if not existing_member:
                new_member = BoardMember(board_id=board_id, user_id=user_id)
                db.session.add(new_member)
        db.session.commit()
        return {"message": "Members added successfully"}, 201


@boards_ns.route("/<int:board_id>/members/<int:user_id>")
@boards_ns.param("board_id", "ID del tablero")
@boards_ns.param("user_id", "ID del usuario")
class BoardMemberResource(Resource):
    @boards_ns.doc(
        "remove_member",
        description="Remover un miembro de un tablero (solo propietario)",
        security="Bearer",
    )
    @boards_ns.response(200, "Miembro removido exitosamente")
    @boards_ns.response(401, "No autorizado", error_model)
    @boards_ns.response(
        403, "Prohibido - solo el propietario puede remover miembros", error_model
    )
    @boards_ns.response(404, "Miembro no encontrado", error_model)
    @jwt_required()
    @require_board_owner
    def delete(self, board_id, user_id):
        """Remover un miembro de un board (solo owner)"""
        member = BoardMember.query.filter_by(board_id=board_id, user_id=user_id).first()
        if not member:
            boards_ns.abort(404, "Member not found")
        db.session.delete(member)
        db.session.commit()
        return {"message": "Member removed successfully"}, 200


@boards_ns.route("/<int:board_id>/cards")
@boards_ns.param("board_id", "ID del tablero")
class BoardCards(Resource):
    @boards_ns.doc(
        "get_board_cards",
        description="Obtener todas las tarjetas de un tablero",
        security="Bearer",
    )
    @boards_ns.response(200, "Lista de tarjetas obtenida exitosamente")
    @boards_ns.response(401, "No autorizado", error_model)
    @boards_ns.response(404, "Tablero no encontrado", error_model)
    @jwt_required()
    @require_board_access
    def get(self, board_id):
        """Obtener todas las tarjetas de un board"""
        board = Board.query.get(board_id)
        if not board:
            boards_ns.abort(404, "Board not found")
        
        # Obtener todas las listas del board
        lists = List.query.filter_by(board_id=board_id).all()
        list_ids = [lst.id for lst in lists]
        
        # Obtener todas las tarjetas de esas listas
        cards = Card.query.filter(Card.list_id.in_(list_ids)).order_by(Card.position).all()
        
        return [card.to_dict() for card in cards], 200
