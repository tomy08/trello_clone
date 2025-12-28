'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { API_URL } from '../constants'

interface EditBoardModalProps {
  isOpen: boolean
  onClose: () => void
  boardId: string | null
  currentTitle: string
  currentDescription: string
  onBoardUpdated: () => void
}

export default function EditBoardModal({
  isOpen,
  onClose,
  boardId,
  currentTitle,
  currentDescription,
  onBoardUpdated,
}: EditBoardModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [title, setTitle] = useState(currentTitle)
  const [description, setDescription] = useState(currentDescription)
  const router = useRouter()

  // Update form fields when props change
  useEffect(() => {
    setTitle(currentTitle)
    setDescription(currentDescription)
  }, [currentTitle, currentDescription, isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    if (!boardId) {
      setError('No board ID provided')
      setIsLoading(false)
      return
    }

    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        throw new Error('No authentication token found. Please log in again.')
      }

      const response = await fetch(`${API_URL}/boards/${boardId}`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title, description }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || 'Error al actualizar el board')
      }

      onBoardUpdated()
      onClose()
    } catch (err) {
      console.error('Error updating board:', err)
      setError(
        err instanceof Error ? err.message : 'Error al actualizar el board'
      )
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!boardId) return

    const confirmed = window.confirm(
      '¿Estás seguro de que quieres eliminar este board? Esta acción no se puede deshacer.'
    )
    if (!confirmed) return

    setIsLoading(true)
    setError('')

    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        throw new Error('No authentication token found. Please log in again.')
      }

      const response = await fetch(`${API_URL}/boards/${boardId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || 'Error al eliminar el board')
      }

      onBoardUpdated()
      onClose()
    } catch (err) {
      console.error('Error deleting board:', err)
      setError(
        err instanceof Error ? err.message : 'Error al eliminar el board'
      )
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-slate-800">Edit Board</h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 transition-colors"
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
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label
              htmlFor="title"
              className="block text-sm font-medium text-slate-700 mb-2"
            >
              Board Title
            </label>
            <input
              type="text"
              id="title"
              name="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-transparent"
              placeholder="e.g., Project Management"
              required
            />
          </div>

          <div className="mb-6">
            <label
              htmlFor="description"
              className="block text-sm font-medium text-slate-700 mb-2"
            >
              Description
            </label>
            <textarea
              id="description"
              name="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-transparent resize-none"
              placeholder="e.g., Tablero para gestión de proyecto"
              rows={3}
              required
            />
          </div>

          <div className="flex gap-3 mb-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors font-medium"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-800 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isLoading}
            >
              {isLoading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>

          <button
            type="button"
            onClick={handleDelete}
            className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={isLoading}
          >
            {isLoading ? 'Deleting...' : 'Delete Board'}
          </button>
        </form>
      </div>
    </div>
  )
}
