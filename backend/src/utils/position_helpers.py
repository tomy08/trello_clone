"""
Funciones auxiliares para manejar posiciones de cards y lists
"""

from src.db import db
from src.models import Card, List


def adjust_positions_on_insert(model, parent_id_field, parent_id, position):
    """
    Ajusta las posiciones de los elementos existentes cuando se inserta uno nuevo.
    Mueve hacia adelante todos los elementos >= position.

    Args:
        model: El modelo (Card o List)
        parent_id_field: El campo que relaciona con el padre ('list_id' o 'board_id')
        parent_id: El ID del padre
        position: La posición donde se insertará el nuevo elemento
    """
    # Obtener todos los elementos con posición >= a la nueva
    items_to_move = (
        model.query.filter_by(**{parent_id_field: parent_id})
        .filter(model.position >= position)
        .all()
    )

    # Incrementar la posición de cada uno
    for item in items_to_move:
        item.position += 1


def compact_positions_on_delete(model, parent_id_field, parent_id, deleted_position):
    """
    Compacta las posiciones después de eliminar un elemento.
    Mueve hacia atrás todos los elementos > deleted_position.

    Args:
        model: El modelo (Card o List)
        parent_id_field: El campo que relaciona con el padre ('list_id' o 'board_id')
        parent_id: El ID del padre
        deleted_position: La posición del elemento eliminado
    """
    # Obtener todos los elementos con posición > a la eliminada
    items_to_move = (
        model.query.filter_by(**{parent_id_field: parent_id})
        .filter(model.position > deleted_position)
        .all()
    )

    # Decrementar la posición de cada uno
    for item in items_to_move:
        item.position -= 1


def reorder_on_move(
    model,
    parent_id_field,
    item,
    old_parent_id,
    old_position,
    new_parent_id,
    new_position,
):
    """
    Reordena las posiciones cuando se mueve un elemento.
    Maneja tanto movimientos dentro del mismo padre como entre padres diferentes.

    Args:
        model: El modelo (Card o List)
        parent_id_field: El campo que relaciona con el padre ('list_id' o 'board_id')
        item: El elemento que se está moviendo
        old_parent_id: ID del padre original
        old_position: Posición original
        new_parent_id: ID del padre destino
        new_position: Posición destino
    """
    if old_parent_id == new_parent_id:
        # Movimiento dentro del mismo padre
        if new_position > old_position:
            # Moviendo hacia adelante: decrementar posiciones entre old y new
            items_to_move = (
                model.query.filter_by(**{parent_id_field: new_parent_id})
                .filter(model.id != item.id)
                .filter(model.position > old_position)
                .filter(model.position <= new_position)
                .all()
            )
            for i in items_to_move:
                i.position -= 1
        else:
            # Moviendo hacia atrás: incrementar posiciones entre new y old
            items_to_move = (
                model.query.filter_by(**{parent_id_field: new_parent_id})
                .filter(model.id != item.id)
                .filter(model.position >= new_position)
                .filter(model.position < old_position)
                .all()
            )
            for i in items_to_move:
                i.position += 1
    else:
        # Movimiento entre padres diferentes
        # 1. Compactar posiciones en el padre origen
        compact_positions_on_delete(model, parent_id_field, old_parent_id, old_position)

        # 2. Ajustar posiciones en el padre destino
        adjust_positions_on_insert(model, parent_id_field, new_parent_id, new_position)


def get_next_position(model, parent_id_field, parent_id):
    """
    Obtiene la siguiente posición disponible para un nuevo elemento.

    Args:
        model: El modelo (Card o List)
        parent_id_field: El campo que relaciona con el padre ('list_id' o 'board_id')
        parent_id: El ID del padre

    Returns:
        int: La siguiente posición disponible
    """
    max_position = (
        db.session.query(db.func.max(model.position))
        .filter_by(**{parent_id_field: parent_id})
        .scalar()
    )
    return (max_position or -1) + 1


def validate_position(model, parent_id_field, parent_id, position):
    """
    Valida que la posición sea válida.
    Si es None, retorna la siguiente posición disponible.
    Si es negativa, retorna 0.

    Args:
        model: El modelo (Card o List)
        parent_id_field: El campo que relaciona con el padre ('list_id' o 'board_id')
        parent_id: El ID del padre
        position: La posición a validar

    Returns:
        int: La posición validada
    """
    if position is None:
        return get_next_position(model, parent_id_field, parent_id)

    if position < 0:
        return 0

    return position
