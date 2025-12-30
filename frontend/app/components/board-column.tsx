'use client'

import { useDroppable } from '@dnd-kit/core'
import {
  SortableContext,
  verticalListSortingStrategy,
  useSortable,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { BoardCard } from './board-card'

interface Card {
  id: number
  title: string
  description: string
  list_id: number
  position: number
  due_date?: string
  archived: boolean
  created_at: string
}

interface BoardColumnProps {
  id: number
  title: string
  cards: Card[]
  onAddCard: (listId: number) => void
  onDeleteList: (listId: number) => void
  onDeleteCard: (cardId: number) => void
}

export function BoardColumn({
  id,
  title,
  cards,
  onAddCard,
  onDeleteList,
  onDeleteCard,
}: BoardColumnProps) {
  const { setNodeRef: setDroppableRef, isOver } = useDroppable({
    id: `droppable-${id}`,
  })

  const {
    attributes,
    listeners,
    setNodeRef: setSortableRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: id,
    data: {
      type: 'column',
      column: { id, title, cards },
    },
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <div
      ref={setSortableRef}
      style={style}
      className={`flex flex-col w-80 rounded-lg p-4 shrink-0 transition-colors ${
        isOver ? 'bg-slate-200' : 'bg-slate-100'
      }`}
    >
      <div
        className="flex items-center justify-between mb-4 cursor-grab active:cursor-grabbing"
        {...attributes}
        {...listeners}
      >
        <h3 className="font-semibold text-slate-800">{title}</h3>
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-500">{cards.length}</span>
          <button
            onClick={() => onDeleteList(id)}
            className="text-slate-400 hover:text-red-600 transition-colors p-1 rounded hover:bg-red-50"
            title="Eliminar lista"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
        </div>
      </div>

      <SortableContext
        items={cards.map((c) => c.id)}
        strategy={verticalListSortingStrategy}
      >
        <div
          ref={setDroppableRef}
          className="flex flex-col gap-2 min-h-[100px] flex-1"
        >
          {cards.map((card) => (
            <BoardCard key={card.id} card={card} onDelete={onDeleteCard} />
          ))}
        </div>
      </SortableContext>

      <button
        onClick={() => onAddCard(id)}
        className="mt-4 w-full py-2 px-4 text-left text-slate-600 hover:bg-slate-200 rounded-lg transition-colors flex items-center gap-2"
      >
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 4v16m8-8H4"
          />
        </svg>
        Agregar tarjeta
      </button>
    </div>
  )
}
