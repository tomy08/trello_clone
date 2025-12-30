'use client'

import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

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

interface BoardCardProps {
  card: Card
  onDelete?: (cardId: number) => void
}

export function BoardCard({ card, onDelete }: BoardCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: card.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow group relative"
    >
      <div
        {...attributes}
        {...listeners}
        className="cursor-grab active:cursor-grabbing"
      >
        <h4 className="font-medium text-slate-800 mb-2">{card.title}</h4>
        {card.description && (
          <p className="text-sm text-slate-600 line-clamp-3">
            {card.description}
          </p>
        )}
      </div>
      {onDelete && (
        <button
          onClick={(e) => {
            e.stopPropagation()
            onDelete(card.id)
          }}
          className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity text-slate-400 hover:text-red-600 p-1 rounded hover:bg-red-50"
          title="Eliminar tarjeta"
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
      )}
    </div>
  )
}
