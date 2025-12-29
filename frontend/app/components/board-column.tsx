'use client'

import { useDroppable } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'
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
}

export function BoardColumn({ id, title, cards, onAddCard }: BoardColumnProps) {
  const { setNodeRef, isOver } = useDroppable({
    id: id,
  })

  return (
    <div
      className={`flex flex-col w-80 rounded-lg p-4 shrink-0 transition-colors ${
        isOver ? 'bg-slate-200' : 'bg-slate-100'
      }`}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-slate-800">{title}</h3>
        <span className="text-sm text-slate-500">{cards.length}</span>
      </div>

      <SortableContext
        items={cards.map((c) => c.id)}
        strategy={verticalListSortingStrategy}
      >
        <div
          ref={setNodeRef}
          className="flex flex-col gap-2 min-h-[100px] flex-1"
        >
          {cards.map((card) => (
            <BoardCard key={card.id} card={card} />
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
