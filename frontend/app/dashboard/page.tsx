'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import AuthCheck from '../components/auth-check'
import { getCurrentUser, logout, type User } from '../lib/auth'
import { API_URL } from '../constants'
import DashboardCard from '../components/dashboard-card'
import CreateBoardModal from '../components/create-board-modal'
import EditBoardModal from '../components/edit-board-modal'

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null)
  const [boards, setBoards] = useState<
    Array<{ id: string; title: string; cardCount: number; description: string }>
  >([])
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [editingBoard, setEditingBoard] = useState<{
    id: string
    title: string
    description: string
  } | null>(null)
  const router = useRouter()

  useEffect(() => {
    getCurrentUser().then(setUser)
  }, [])

  const fetchBoards = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        console.error('No authentication token found')
        return
      }
      const API_ENDPOINT = API_URL + '/boards'
      const response = await fetch(API_ENDPOINT, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error(`Failed to fetch boards: ${response.status}`)
      }

      const data = await response.json()
      setBoards(data)
    } catch (error) {
      console.error('Error fetching boards:', error)
    }
  }

  useEffect(() => {
    fetchBoards()
  }, [])

  const handleEditBoard = (board: {
    id: string
    title: string
    description: string
  }) => {
    setEditingBoard(board)
    setIsEditModalOpen(true)
  }

  const handleBoardUpdated = () => {
    fetchBoards()
  }

  const handleSignOut = () => {
    logout()
    router.push('/login')
  }

  return (
    <>
      <AuthCheck />
      <div className="min-h-screen bg-linear-to-br from-slate-50 to-slate-100">
        {/* Header */}
        <header className="px-8 py-6 border-b border-slate-200 bg-white/50 backdrop-blur-sm ">
          <div className="flex items-around justify-between">
            <h1 className="text-slate-800 text-3xl font-bold">
              Bienvenido {user?.name || 'Usuario'} a Trello Clone
            </h1>

            {/* User Profile & Sign Out */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center text-white font-semibold">
                  {user?.name?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div className="hidden md:block">
                  <p className="text-sm font-medium text-slate-800">
                    {user?.name || 'Usuario'}
                  </p>
                  <p className="text-xs text-slate-500">{user?.email || ''}</p>
                </div>
              </div>
              <button
                onClick={handleSignOut}
                className="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-800 transition-colors text-sm font-medium"
              >
                Sign Out
              </button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="px-8 py-8">
          <div className="mb-6">
            <h2 className="text-slate-800 text-xl font-semibold mb-2">
              Your Boards
            </h2>
            <p className="text-slate-600 text-sm">
              Click on a board to view and manage tasks
            </p>
          </div>

          {/* Boards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl">
            {boards.map((board) => (
              <DashboardCard
                key={board.id}
                boardId={board.id}
                title={board.title}
                cardCount={board.cardCount}
                link={`/boards/${board.id}`}
                description={board.description}
                onEditClick={() =>
                  handleEditBoard({
                    id: board.id,
                    title: board.title,
                    description: board.description,
                  })
                }
              />
            ))}

            {/* Create New Board */}
            <button
              onClick={() => setIsModalOpen(true)}
              className="border-2 border-dashed border-slate-300 rounded-lg p-6 cursor-pointer hover:border-slate-400 hover:bg-slate-50 transition-all duration-200 flex flex-col items-center justify-center min-h-[180px] bg-white"
            >
              <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mb-3 hover:bg-slate-200 transition-colors">
                <svg
                  className="w-6 h-6 text-slate-600"
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
              </div>
              <p className="text-slate-700 font-medium">Create new board</p>
            </button>
          </div>
        </main>

        {/* Create Board Modal */}
        <CreateBoardModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
        />

        {/* Edit Board Modal */}
        <EditBoardModal
          isOpen={isEditModalOpen}
          onClose={() => {
            setIsEditModalOpen(false)
            setEditingBoard(null)
          }}
          boardId={editingBoard?.id || null}
          currentTitle={editingBoard?.title || ''}
          currentDescription={editingBoard?.description || ''}
          onBoardUpdated={handleBoardUpdated}
        />
      </div>
    </>
  )
}
