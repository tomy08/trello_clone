'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import AuthCheck from '@/app/components/auth-check'
import { getCurrentUser, getAccessToken, type User } from '@/app/lib/auth'
import { API_URL } from '@/app/constants'

interface Board {
  id: string
  title: string
  description: string
  owner_id: string
  created_at: string
}

interface Card {
  id: string
  title: string
  description: string
  position: number
  board_id: string
}

export default function BoardPage() {
  const router = useRouter()
  const params = useParams()
  const boardId = params.id as string

  const [user, setUser] = useState<User | null>(null)
  const [board, setBoard] = useState<Board | null>(null)
  const [cards, setCards] = useState<Card[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isAuthorized, setIsAuthorized] = useState(false)

  useEffect(() => {
    getCurrentUser().then(setUser)
  }, [])

  // Validar acceso al board
  const validateAccess = async () => {
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
  }

  // Cargar las cards del board
  const fetchCards = async () => {
    try {
      const token = getAccessToken()
      if (!token) return

      const API_ENDPOINT = `${API_URL}/boards/${boardId}/cards`
      const response = await fetch(API_ENDPOINT, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setCards(data)
      }
    } catch (error) {
      console.error('Error fetching cards:', error)
    }
  }

  useEffect(() => {
    const loadBoardData = async () => {
      setLoading(true)
      const hasAccess = await validateAccess()

      if (hasAccess) {
        await fetchCards()
      }

      setLoading(false)
    }

    if (boardId) {
      loadBoardData()
    }
  }, [boardId])

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
          <div className="max-w-7xl mx-auto">
            <div className="mb-6 flex justify-between items-center">
              <h2 className="text-2xl font-semibold text-slate-800">
                Cards ({cards.length})
              </h2>
              <button className="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-800 transition-colors">
                + Agregar Card
              </button>
            </div>

            {/* Cards Grid */}
            {cards.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-slate-500 text-lg">
                  No hay cards en este board todavía
                </p>
                <p className="text-slate-400 text-sm mt-2">
                  ¡Crea tu primera card para comenzar!
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {cards.map((card) => (
                  <div
                    key={card.id}
                    className="bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-all duration-200 border border-slate-200"
                  >
                    <h3 className="font-semibold text-slate-800 mb-2">
                      {card.title}
                    </h3>
                    {card.description && (
                      <p className="text-slate-600 text-sm">
                        {card.description}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    </>
  )
}
