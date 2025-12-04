from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.decorators import require_board_access
from src.models import List, Board, Card
from src.db import db
from src.utils.position_helpers import (
    adjust_positions_on_insert,
    validate_position,
    compact_positions_on_delete,
    reorder_on_move,
)

# Crear namespace para lists
lists_ns = Namespace("lists", description="Operaciones de listas")

# Definir modelos para documentación
list_create_model = lists_ns.model(
    "ListCreate",
    {
        "title": fields.String(
            required=True, description="Título de la lista", example="To Do"
        ),
        "board_id": fields.Integer(
            required=True, description="ID del tablero", example=1
        ),
        "position": fields.Float(description="Posición en el tablero", example=1.0),
    },
)

list_update_model = lists_ns.model(
    "ListUpdate",
    {
        "title": fields.String(description="Título de la lista"),
        "board_id": fields.Integer(description="ID del tablero"),
        "position": fields.Float(description="Posición en el tablero"),
    },
)

list_move_model = lists_ns.model(
    "ListMove",
    {
        "board_id": fields.Integer(description="ID del tablero destino"),
        "position": fields.Float(description="Nueva posición"),
    },
)

list_response_model = lists_ns.model(
    "ListResponse",
    {
        "id": fields.Integer(description="ID de la lista"),
        "title": fields.String(description="Título de la lista"),
        "board_id": fields.Integer(description="ID del tablero"),
        "position": fields.Float(description="Posición en el tablero"),
        "created_at": fields.DateTime(description="Fecha de creación"),
    },
)

card_create_in_list_model = lists_ns.model(
    "CardCreateInList",
    {
        "title": fields.String(
            required=True, description="Título de la tarjeta", example="Nueva tarea"
        ),
        "description": fields.String(description="Descripción de la tarjeta"),
        "position": fields.Float(description="Posición en la lista"),
        "due_date": fields.DateTime(description="Fecha de vencimiento"),
    },
)

error_model = lists_ns.model(
    "Error", {"error": fields.String(description="Mensaje de error")}
)


@lists_ns.route("/")
class ListCollection(Resource):
    @lists_ns.doc(
        "create_list",
        description="Crear una nueva lista en un tablero",
        security="Bearer",
    )
    @lists_ns.expect(list_create_model, validate=True)
    @lists_ns.response(201, "Lista creada exitosamente", list_response_model)
    @lists_ns.response(400, "Datos inválidos", error_model)
    @lists_ns.response(401, "No autorizado", error_model)
    @lists_ns.response(404, "Tablero no encontrado", error_model)
    @jwt_required()
    @require_board_access
    def post(self):
        """Crear una nueva lista"""
        data = request.get_json()
        title = data.get("title")
        board_id = data.get("board_id")
        position = data.get("position")

        if not title or board_id is None:
            lists_ns.abort(400, "Title and board_id are required")

        # Verificar que el board existe
        board = Board.query.get(board_id)
        if not board:
            lists_ns.abort(404, "Board not found")

        # Validar y obtener posición
        position = validate_position(List, "board_id", board_id, position)

        # Ajustar posiciones de listas existentes
        adjust_positions_on_insert(List, "board_id", board_id, position)

        new_list = List(title=title, board_id=board_id, position=position)
        db.session.add(new_list)
        db.session.commit()
        return new_list.to_dict(), 201


@lists_ns.route("/<int:list_id>")
@lists_ns.param("list_id", "ID de la lista")
class ListResource(Resource):
    @lists_ns.doc(
        "get_list", description="Obtener una lista específica", security="Bearer"
    )
    @lists_ns.response(200, "Lista obtenida exitosamente", list_response_model)
    @lists_ns.response(401, "No autorizado", error_model)
    @lists_ns.response(404, "Lista no encontrada", error_model)
    @jwt_required()
    @require_board_access
    def get(self, list_id):
        """Obtener una lista específica"""
        current_user_id = get_jwt_identity()
        list_obj = List.query.get(list_id)
        if not list_obj:
            lists_ns.abort(404, "List not found")

        return list_obj.to_dict(), 200

    @lists_ns.doc("update_list", description="Actualizar una lista", security="Bearer")
    @lists_ns.expect(list_update_model)
    @lists_ns.response(200, "Lista actualizada exitosamente", list_response_model)
    @lists_ns.response(401, "No autorizado", error_model)
    @lists_ns.response(404, "Lista o tablero no encontrado", error_model)
    @jwt_required()
    @require_board_access
    def put(self, list_id):
        """Actualizar una lista"""
        list_obj = List.query.get(list_id)
        if not list_obj:
            lists_ns.abort(404, "List not found")

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
                lists_ns.abort(404, "Board not found")

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
        return list_obj.to_dict(), 200

    @lists_ns.doc("delete_list", description="Eliminar una lista", security="Bearer")
    @lists_ns.response(200, "Lista eliminada exitosamente")
    @lists_ns.response(401, "No autorizado", error_model)
    @lists_ns.response(404, "Lista no encontrada", error_model)
    @jwt_required()
    @require_board_access
    def delete(self, list_id):
        """Eliminar una lista"""
        list_obj = List.query.get(list_id)
        if not list_obj:
            lists_ns.abort(404, "List not found")

        board_id = list_obj.board_id
        position = list_obj.position

        db.session.delete(list_obj)
        # Compactar posiciones de las listas restantes
        compact_positions_on_delete(List, "board_id", board_id, position)

        db.session.commit()
        return {"message": "List deleted successfully"}, 200


@lists_ns.route("/<int:list_id>/cards")
@lists_ns.param("list_id", "ID de la lista")
class ListCards(Resource):
    @lists_ns.doc(
        "get_list_cards",
        description="Obtener todas las tarjetas de una lista",
        security="Bearer",
    )
    @lists_ns.response(200, "Lista de tarjetas obtenida exitosamente")
    @lists_ns.response(401, "No autorizado", error_model)
    @lists_ns.response(404, "Lista no encontrada", error_model)
    @jwt_required()
    @require_board_access
    def get(self, list_id):
        """Obtener tarjetas de una lista"""
        current_user_id = get_jwt_identity()
        list_obj = List.query.get(list_id)
        if not list_obj:
            lists_ns.abort(404, "List not found")

        cards = [card.to_dict() for card in list_obj.cards]
        return cards, 200

    @lists_ns.doc(
        "add_card_to_list",
        description="Agregar una tarjeta a una lista",
        security="Bearer",
    )
    @lists_ns.expect(card_create_in_list_model, validate=True)
    @lists_ns.response(201, "Tarjeta creada exitosamente")
    @lists_ns.response(400, "Datos inválidos", error_model)
    @lists_ns.response(401, "No autorizado", error_model)
    @lists_ns.response(404, "Lista no encontrada", error_model)
    @jwt_required()
    @require_board_access
    def post(self, list_id):
        """Agregar tarjeta a una lista"""
        current_user_id = get_jwt_identity()
        list_obj = List.query.get(list_id)
        if not list_obj:
            lists_ns.abort(404, "List not found")

        data = request.get_json()
        title = data.get("title")
        description = data.get("description")
        position = data.get("position")
        due_date = data.get("due_date")

        if not title:
            lists_ns.abort(400, "Title is required")

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
        return new_card.to_dict(), 201


@lists_ns.route("/<int:list_id>/move")
@lists_ns.param("list_id", "ID de la lista")
class ListMove(Resource):
    @lists_ns.doc(
        "move_list",
        description="Mover una lista a otro tablero y/o posición",
        security="Bearer",
    )
    @lists_ns.expect(list_move_model)
    @lists_ns.response(200, "Lista movida exitosamente", list_response_model)
    @lists_ns.response(400, "Datos inválidos", error_model)
    @lists_ns.response(401, "No autorizado", error_model)
    @lists_ns.response(404, "Lista o tablero no encontrado", error_model)
    @jwt_required()
    @require_board_access
    def put(self, list_id):
        """Mover una lista a otro board y/o posición"""
        current_user_id = get_jwt_identity()
        list_obj = List.query.get(list_id)
        if not list_obj:
            lists_ns.abort(404, "List not found")

        data = request.get_json()
        new_board_id = data.get("board_id")
        new_position = data.get("position")

        if new_board_id is None and new_position is None:
            lists_ns.abort(400, "board_id or position is required")

        old_board_id = list_obj.board_id
        old_position = list_obj.position

        # Usar board_id actual si no se proporciona uno nuevo
        if new_board_id is None:
            new_board_id = old_board_id
        else:
            # Verificar que el nuevo board existe
            new_board = Board.query.get(new_board_id)
            if not new_board:
                lists_ns.abort(404, "New board not found")

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
        return list_obj.to_dict(), 200
