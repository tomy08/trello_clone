'use client'

import { useState } from 'react'
import { getAccessToken } from '@/app/lib/auth'
import { API_URL } from '@/app/constants'

interface AddListButtonProps {
  boardId: string
  onListCreated: () => void
}

export function AddListButton({ boardId, onListCreated }: AddListButtonProps) {
  const [isAdding, setIsAdding] = useState(false)
  const [title, setTitle] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim() || isLoading) return

    setIsLoading(true)
    try {
      const token = getAccessToken()
      if (!token) return

      const response = await fetch(`${API_URL}/lists/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: title.trim(),
          board_id: parseInt(boardId),
        }),
      })

      if (response.ok) {
        setTitle('')
        setIsAdding(false)
        onListCreated()
      }
    } catch (error) {
      console.error('Error creating list:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (!isAdding) {
    return (
      <button
        onClick={() => setIsAdding(true)}
        className="shrink-0 w-80 bg-white/50 hover:bg-white/80 rounded-lg p-4 transition-colors flex items-center gap-2 text-slate-600 font-medium"
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
        Agregar lista
      </button>
    )
  }

  return (
    <div className="shrink-0 w-80 bg-slate-100 rounded-lg p-4">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Título de la lista"
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500 mb-2"
          autoFocus
        />
        <div className="flex gap-2">
          <button
            type="submit"
            disabled={!title.trim() || isLoading}
            className="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-800 transition-colors disabled:opacity-50"
          >
            {isLoading ? 'Creando...' : 'Agregar'}
          </button>
          <button
            type="button"
            onClick={() => {
              setIsAdding(false)
              setTitle('')
            }}
            className="px-4 py-2 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300 transition-colors"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  )
}
