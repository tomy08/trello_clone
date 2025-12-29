'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter, useParams } from 'next/navigation'
import {
  DndContext,
  DragEndEvent,
  DragOverEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import { arrayMove } from '@dnd-kit/sortable'
import AuthCheck from '@/app/components/auth-check'
import { getCurrentUser, getAccessToken, type User } from '@/app/lib/auth'
import { API_URL } from '@/app/constants'
import { BoardColumn } from '@/app/components/board-column'
import { BoardCard } from '@/app/components/board-card'
import { AddListButton } from '@/app/components/add-list-button'

interface Board {
  id: string
  title: string
  description: string
  owner_id: string
  created_at: string
}

interface List {
  id: number
  title: string
  board_id: number
  position: number
  created_at: string
}

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

interface Column {
  id: number
  title: string
  cards: Card[]
}

export default function BoardPage() {
  const router = useRouter()
  const params = useParams()
  const boardId = params.id as string

  const [user, setUser] = useState<User | null>(null)
  const [board, setBoard] = useState<Board | null>(null)
  const [columns, setColumns] = useState<Column[]>([])
  const [activeCard, setActiveCard] = useState<Card | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isAuthorized, setIsAuthorized] = useState(false)
  const [showAddCardModal, setShowAddCardModal] = useState(false)
  const [selectedListId, setSelectedListId] = useState<number | null>(null)
  const [newCardTitle, setNewCardTitle] = useState('')
  const [newCardDescription, setNewCardDescription] = useState('')

  // Configurar sensores para drag & drop
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  )

  useEffect(() => {
    getCurrentUser().then(setUser)
  }, [])

  // Validar acceso al board
  const validateAccess = useCallback(async () => {
    try {
      const token = getAccessToken()
      if (!token) {
        setError('No estás autenticado')
        router.push('/login')
        return false
      }

      const API_ENDPOINT = `${API_URL}/boards/${boardId}`
      const response = await fetch(API_ENDPOINT, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.status === 404) {
        setError('Board no encontrado')
        return false
      }

      if (response.status === 403) {
        setError('No tienes permiso para acceder a este board')
        return false
      }

      if (!response.ok) {
        setError('Error al cargar el board')
        return false
      }

      const boardData = await response.json()
      setBoard(boardData)
      setIsAuthorized(true)
      return true
    } catch (error) {
      console.error('Error validating access:', error)
      setError('Error al validar el acceso')
      return false
    }
  }, [boardId, router])

  // Cargar listas y tarjetas del board
  const fetchListsAndCards = useCallback(async () => {
    try {
      const token = getAccessToken()
      if (!token) return

      // Obtener todas las listas del board
      const listsResponse = await fetch(`${API_URL}/boards/${boardId}/lists`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!listsResponse.ok) {
        console.error('Error al cargar listas')
        return
      }

      const allLists: List[] = await listsResponse.json()

      // Obtener todas las tarjetas del board
      const cardsResponse = await fetch(`${API_URL}/boards/${boardId}/cards`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!cardsResponse.ok) {
        console.error('Error al cargar tarjetas')
        return
      }

      const allCards: Card[] = await cardsResponse.json()

      // Crear columnas con todas las listas (incluso las vacías)
      const columnsWithCards = allLists.map((list) => ({
        id: list.id,
        title: list.title,
        cards: allCards
          .filter((card) => card.list_id === list.id)
          .sort((a, b) => a.position - b.position),
      }))

      // Ordenar columnas por posición de lista
      setColumns(
        columnsWithCards.sort((a, b) => {
          const aList = allLists.find((l) => l.id === a.id)
          const bList = allLists.find((l) => l.id === b.id)
          return (aList?.position || 0) - (bList?.position || 0)
        })
      )
    } catch (error) {
      console.error('Error fetching lists and cards:', error)
    }
  }, [boardId])

  // Handlers para drag & drop
  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event
    const card = columns
      .flatMap((col) => col.cards)
      .find((c) => c.id === active.id)
    setActiveCard(card || null)
  }

  const handleDragOver = (event: DragOverEvent) => {
    const { active, over } = event
    if (!over) return

    const activeId = active.id as number
    const overId = over.id as number

    // Encontrar columnas
    const activeColumn = columns.find((col) =>
      col.cards.some((card) => card.id === activeId)
    )
    const overColumn = columns.find(
      (col) => col.id === overId || col.cards.some((card) => card.id === overId)
    )

    if (!activeColumn || !overColumn) return
    if (activeColumn.id === overColumn.id) return

    setColumns((cols) => {
      const activeCards = [...activeColumn.cards]
      const overCards = [...overColumn.cards]
      const activeIndex = activeCards.findIndex((c) => c.id === activeId)
      const overIndex = overCards.findIndex((c) => c.id === overId)

      const [movedCard] = activeCards.splice(activeIndex, 1)
      movedCard.list_id = overColumn.id

      if (overId === overColumn.id) {
        overCards.push(movedCard)
      } else {
        overCards.splice(overIndex, 0, movedCard)
      }

      return cols.map((col) => {
        if (col.id === activeColumn.id) return { ...col, cards: activeCards }
        if (col.id === overColumn.id) return { ...col, cards: overCards }
        return col
      })
    })
  }

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event
    setActiveCard(null)

    if (!over) return

    const activeId = active.id as number
    const overId = over.id as number

    const activeColumn = columns.find((col) =>
      col.cards.some((card) => card.id === activeId)
    )
    const overColumn = columns.find(
      (col) => col.id === overId || col.cards.some((card) => card.id === overId)
    )

    if (!activeColumn || !overColumn) return

    const activeCard = activeColumn.cards.find((c) => c.id === activeId)
    if (!activeCard) return

    // Si se movió a otra columna
    if (activeColumn.id !== overColumn.id) {
      const newPosition = overColumn.cards.length
      await moveCardToList(activeId, overColumn.id, newPosition)
    } else {
      // Reordenar dentro de la misma columna
      const activeIndex = activeColumn.cards.findIndex((c) => c.id === activeId)
      const overIndex = activeColumn.cards.findIndex((c) => c.id === overId)

      if (activeIndex !== overIndex) {
        setColumns((cols) => {
          const updatedCards = arrayMove(
            activeColumn.cards,
            activeIndex,
            overIndex
          )
          return cols.map((col) =>
            col.id === activeColumn.id ? { ...col, cards: updatedCards } : col
          )
        })
        // Actualizar posición en la API
        await moveCardToList(activeId, activeColumn.id, overIndex)
      }
    }
  }

  const handleAddCard = (listId: number) => {
    setSelectedListId(listId)
    setShowAddCardModal(true)
  }

  const createCard = async () => {
    if (!newCardTitle.trim() || !selectedListId) return

    try {
      const token = getAccessToken()
      if (!token) return

      const response = await fetch(`${API_URL}/lists/${selectedListId}/cards`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: newCardTitle,
          description: newCardDescription,
        }),
      })

      if (response.ok) {
        setNewCardTitle('')
        setNewCardDescription('')
        setShowAddCardModal(false)
        await fetchListsAndCards()
      }
    } catch (error) {
      console.error('Error creating card:', error)
    }
  }

  const moveCardToList = async (
    cardId: number,
    listId: number,
    position: number
  ) => {
    try {
      const token = getAccessToken()
      if (!token) return

      await fetch(`${API_URL}/cards/${cardId}/move`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          list_id: listId,
          position,
        }),
      })
    } catch (error) {
      console.error('Error moving card:', error)
    }
  }

  useEffect(() => {
    const loadBoardData = async () => {
      setLoading(true)
      const hasAccess = await validateAccess()

      if (hasAccess) {
        await fetchListsAndCards()
      }

      setLoading(false)
    }

    if (boardId) {
      loadBoardData()
    }
  }, [boardId, validateAccess, fetchListsAndCards])

  if (loading) {
    return (
      <>
        <AuthCheck />
        <div className="min-h-screen bg-linear-to-br from-slate-50 to-slate-100 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-700 mx-auto"></div>
            <p className="mt-4 text-slate-600">Cargando board...</p>
          </div>
        </div>
      </>
    )
  }

  if (error || !isAuthorized) {
    return (
      <>
        <AuthCheck />
        <div className="min-h-screen bg-linear-to-br from-slate-50 to-slate-100 flex items-center justify-center">
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-md">
            <div className="text-center">
              <svg
                className="mx-auto h-12 w-12 text-red-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              <h2 className="mt-4 text-xl font-semibold text-slate-800">
                Acceso Denegado
              </h2>
              <p className="mt-2 text-slate-600">
                {error || 'No tienes acceso a este board'}
              </p>
              <button
                onClick={() => router.push('/dashboard')}
                className="mt-6 px-6 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-800 transition-colors"
              >
                Volver al Dashboard
              </button>
            </div>
          </div>
        </div>
      </>
    )
  }

  return (
    <>
      <AuthCheck />
      <div className="min-h-screen bg-linear-to-br from-slate-50 to-slate-100">
        {/* Header */}
        <header className="px-8 py-6 border-b border-slate-200 bg-white/50 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/dashboard')}
                className="text-slate-600 hover:text-slate-800 transition-colors"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
              </button>
              <div>
                <h1 className="text-slate-800 text-3xl font-bold">
                  {board?.title}
                </h1>
                {board?.description && (
                  <p className="text-slate-600 text-sm mt-1">
                    {board.description}
                  </p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center text-white font-semibold">
                {user?.name?.charAt(0).toUpperCase() || 'U'}
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="p-8">
          <DndContext
            sensors={sensors}
            onDragStart={handleDragStart}
            onDragOver={handleDragOver}
            onDragEnd={handleDragEnd}
          >
            <div className="flex gap-6 overflow-x-auto pb-4">
              {columns.map((column) => (
                <BoardColumn
                  key={column.id}
                  id={column.id}
                  title={column.title}
                  cards={column.cards}
                  onAddCard={handleAddCard}
                />
              ))}

              <AddListButton
                boardId={boardId}
                onListCreated={fetchListsAndCards}
              />
            </div>

            <DragOverlay>
              {activeCard ? <BoardCard card={activeCard} /> : null}
            </DragOverlay>
          </DndContext>
        </main>

        {/* Modal para agregar tarjeta */}
        {showAddCardModal && (
          <div
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={() => setShowAddCardModal(false)}
          >
            <div
              className="bg-white rounded-lg p-6 w-full max-w-md"
              onClick={(e) => e.stopPropagation()}
            >
              <h2 className="text-xl font-semibold text-slate-800 mb-4">
                Nueva Tarjeta
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Título
                  </label>
                  <input
                    type="text"
                    value={newCardTitle}
                    onChange={(e) => setNewCardTitle(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500"
                    placeholder="Título de la tarjeta"
                    autoFocus
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Descripción (opcional)
                  </label>
                  <textarea
                    value={newCardDescription}
                    onChange={(e) => setNewCardDescription(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500 resize-none"
                    placeholder="Descripción de la tarjeta"
                    rows={3}
                  />
                </div>
              </div>
              <div className="flex gap-2 mt-6">
                <button
                  onClick={createCard}
                  disabled={!newCardTitle.trim()}
                  className="flex-1 px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Crear
                </button>
                <button
                  onClick={() => {
                    setShowAddCardModal(false)
                    setNewCardTitle('')
                    setNewCardDescription('')
                  }}
                  className="px-4 py-2 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300 transition-colors"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
