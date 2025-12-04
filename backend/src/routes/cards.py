from flask import request
from flask_restx import Namespace, Resource, fields
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

# Crear namespace para cards
cards_ns = Namespace("cards", description="Operaciones de tarjetas")

# Definir modelos para documentación
card_create_model = cards_ns.model(
    "CardCreate",
    {
        "title": fields.String(
            required=True,
            description="Título de la tarjeta",
            example="Implementar login",
        ),
        "description": fields.String(
            description="Descripción de la tarjeta",
            example="Crear formulario y endpoint de autenticación",
        ),
        "list_id": fields.Integer(
            required=True, description="ID de la lista", example=1
        ),
        "position": fields.Float(description="Posición en la lista", example=1.0),
        "due_date": fields.DateTime(description="Fecha de vencimiento"),
    },
)

card_update_model = cards_ns.model(
    "CardUpdate",
    {
        "title": fields.String(description="Título de la tarjeta"),
        "description": fields.String(description="Descripción de la tarjeta"),
        "list_id": fields.Integer(description="ID de la lista"),
        "position": fields.Float(description="Posición en la lista"),
        "due_date": fields.DateTime(description="Fecha de vencimiento"),
        "archived": fields.Boolean(description="Estado archivado"),
    },
)

card_move_model = cards_ns.model(
    "CardMove",
    {
        "list_id": fields.Integer(description="ID de la lista destino"),
        "position": fields.Float(description="Nueva posición"),
    },
)

card_response_model = cards_ns.model(
    "CardResponse",
    {
        "id": fields.Integer(description="ID de la tarjeta"),
        "title": fields.String(description="Título de la tarjeta"),
        "description": fields.String(description="Descripción de la tarjeta"),
        "list_id": fields.Integer(description="ID de la lista"),
        "position": fields.Float(description="Posición en la lista"),
        "due_date": fields.DateTime(description="Fecha de vencimiento"),
        "archived": fields.Boolean(description="Estado archivado"),
        "created_at": fields.DateTime(description="Fecha de creación"),
    },
)

error_model = cards_ns.model(
    "Error", {"error": fields.String(description="Mensaje de error")}
)


@cards_ns.route("/")
class CardCollection(Resource):
    @cards_ns.doc(
        "create_card",
        description="Crear una nueva tarjeta en una lista",
        security="Bearer",
    )
    @cards_ns.expect(card_create_model, validate=True)
    @cards_ns.response(201, "Tarjeta creada exitosamente", card_response_model)
    @cards_ns.response(400, "Datos inválidos", error_model)
    @cards_ns.response(401, "No autorizado", error_model)
    @cards_ns.response(404, "Lista no encontrada", error_model)
    @jwt_required()
    @require_board_access
    def post(self):
        """Crear una nueva tarjeta"""
        data = request.get_json()
        title = data.get("title")
        description = data.get("description")
        list_id = data.get("list_id")
        position = data.get("position")
        due_date = data.get("due_date")

        if not title or list_id is None:
            cards_ns.abort(400, "Title and list_id are required")

        # Verificar que la lista existe
        list_obj = List.query.get(list_id)
        if not list_obj:
            cards_ns.abort(404, "List not found")

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


@cards_ns.route("/<int:card_id>")
@cards_ns.param("card_id", "ID de la tarjeta")
class CardResource(Resource):
    @cards_ns.doc(
        "get_card", description="Obtener una tarjeta específica", security="Bearer"
    )
    @cards_ns.response(200, "Tarjeta obtenida exitosamente", card_response_model)
    @cards_ns.response(401, "No autorizado", error_model)
    @cards_ns.response(404, "Tarjeta no encontrada", error_model)
    @jwt_required()
    @require_board_access
    def get(self, card_id):
        """Obtener una tarjeta específica"""
        card = Card.query.get(card_id)
        if not card:
            cards_ns.abort(404, "Card not found")

        return card.to_dict(), 200

    @cards_ns.doc(
        "update_card", description="Actualizar una tarjeta", security="Bearer"
    )
    @cards_ns.expect(card_update_model)
    @cards_ns.response(200, "Tarjeta actualizada exitosamente", card_response_model)
    @cards_ns.response(401, "No autorizado", error_model)
    @cards_ns.response(404, "Tarjeta o lista no encontrada", error_model)
    @jwt_required()
    @require_board_access
    def put(self, card_id):
        """Actualizar una tarjeta"""
        card = Card.query.get(card_id)
        if not card:
            cards_ns.abort(404, "Card not found")

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
                cards_ns.abort(404, "New list not found")

        # Si cambió la lista o la posición, reordenar
        if new_list_id != old_list_id or (
            new_position is not None and new_position != old_position
        ):
            if new_position is None:
                new_position = validate_position(Card, "list_id", new_list_id, None)
            else:
                new_position = validate_position(
                    Card, "list_id", new_list_id, new_position
                )

            reorder_on_move(
                Card,
                "list_id",
                card,
                old_list_id,
                old_position,
                new_list_id,
                new_position,
            )
            card.list_id = new_list_id
            card.position = new_position

        db.session.commit()
        return card.to_dict(), 200

    @cards_ns.doc("delete_card", description="Eliminar una tarjeta", security="Bearer")
    @cards_ns.response(200, "Tarjeta eliminada exitosamente")
    @cards_ns.response(401, "No autorizado", error_model)
    @cards_ns.response(404, "Tarjeta no encontrada", error_model)
    @jwt_required()
    @require_board_access
    def delete(self, card_id):
        """Eliminar una tarjeta"""
        card = Card.query.get(card_id)
        if not card:
            cards_ns.abort(404, "Card not found")

        list_id = card.list_id
        position = card.position

        db.session.delete(card)
        # Compactar posiciones de las cards restantes
        compact_positions_on_delete(Card, "list_id", list_id, position)

        db.session.commit()
        return {"message": "Card deleted successfully"}, 200


@cards_ns.route("/<int:card_id>/archive")
@cards_ns.param("card_id", "ID de la tarjeta")
class CardArchive(Resource):
    @cards_ns.doc("archive_card", description="Archivar una tarjeta", security="Bearer")
    @cards_ns.response(200, "Tarjeta archivada exitosamente", card_response_model)
    @cards_ns.response(401, "No autorizado", error_model)
    @cards_ns.response(404, "Tarjeta no encontrada", error_model)
    @jwt_required()
    @require_board_access
    def put(self, card_id):
        """Archivar una tarjeta"""
        card = Card.query.get(card_id)
        if not card:
            cards_ns.abort(404, "Card not found")

        card.archived = True
        db.session.commit()
        return card.to_dict(), 200


@cards_ns.route("/<int:card_id>/unarchive")
@cards_ns.param("card_id", "ID de la tarjeta")
class CardUnarchive(Resource):
    @cards_ns.doc(
        "unarchive_card", description="Desarchivar una tarjeta", security="Bearer"
    )
    @cards_ns.response(200, "Tarjeta desarchivada exitosamente", card_response_model)
    @cards_ns.response(401, "No autorizado", error_model)
    @cards_ns.response(404, "Tarjeta no encontrada", error_model)
    @jwt_required()
    @require_board_access
    def put(self, card_id):
        """Desarchivar una tarjeta"""
        card = Card.query.get(card_id)
        if not card:
            cards_ns.abort(404, "Card not found")

        card.archived = False
        db.session.commit()
        return card.to_dict(), 200


@cards_ns.route("/<int:card_id>/move")
@cards_ns.param("card_id", "ID de la tarjeta")
class CardMove(Resource):
    @cards_ns.doc(
        "move_card",
        description="Mover una tarjeta a otra lista y/o posición",
        security="Bearer",
    )
    @cards_ns.expect(card_move_model)
    @cards_ns.response(200, "Tarjeta movida exitosamente", card_response_model)
    @cards_ns.response(400, "Datos inválidos", error_model)
    @cards_ns.response(401, "No autorizado", error_model)
    @cards_ns.response(404, "Tarjeta o lista no encontrada", error_model)
    @jwt_required()
    @require_board_access
    def put(self, card_id):
        """Mover una tarjeta a otra lista y/o posición"""
        card = Card.query.get(card_id)
        if not card:
            cards_ns.abort(404, "Card not found")

        data = request.get_json()
        new_list_id = data.get("list_id")
        new_position = data.get("position")

        if new_list_id is None and new_position is None:
            cards_ns.abort(400, "list_id or position is required")

        old_list_id = card.list_id
        old_position = card.position

        # Usar list_id actual si no se proporciona uno nuevo
        if new_list_id is None:
            new_list_id = old_list_id
        else:
            # Verificar que la nueva lista existe
            new_list = List.query.get(new_list_id)
            if not new_list:
                cards_ns.abort(404, "New list not found")

        # Validar y obtener posición
        new_position = validate_position(Card, "list_id", new_list_id, new_position)

        # Solo reordenar si realmente cambia algo
        if new_list_id != old_list_id or new_position != old_position:
            reorder_on_move(
                Card,
                "list_id",
                card,
                old_list_id,
                old_position,
                new_list_id,
                new_position,
            )
            card.list_id = new_list_id
            card.position = new_position

        db.session.commit()
        return card.to_dict(), 200
