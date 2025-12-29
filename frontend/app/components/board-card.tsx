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
}

export function BoardCard({ card }: BoardCardProps) {
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
      {...attributes}
      {...listeners}
      className="bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-grab active:cursor-grabbing"
    >
      <h4 className="font-medium text-slate-800 mb-2">{card.title}</h4>
      {card.description && (
        <p className="text-sm text-slate-600 line-clamp-3">
          {card.description}
        </p>
      )}
    </div>
  )
}
