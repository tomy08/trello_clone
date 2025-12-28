type DashboardCardProps = {
  title?: string
  cardCount?: number
  link?: string
  boardId?: string
  description?: string
  onEditClick?: () => void
}

export default function DashboardCard({
  title,
  cardCount,
  link,
  boardId,
  description,
  onEditClick,
}: DashboardCardProps) {
  const handleEditClick = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (onEditClick) {
      onEditClick()
    }
  }

  return (
    <div className="bg-white rounded-lg p-6 hover:shadow-lg transition-all duration-200 hover:-translate-y-1 border border-slate-200 shadow-sm relative">
      <a href={link} className="block cursor-pointer">
        <h3 className="text-slate-800 text-xl font-semibold mb-16">{title}</h3>
        <p className="text-slate-500 text-sm">{cardCount} cards</p>
      </a>
      <button
        onClick={handleEditClick}
        className="absolute top-4 right-4"
        title="Edit board"
      >
        <svg
          className="w-6 h-6 text-slate-400 cursor-pointer hover:text-slate-600 transition-colors"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 6v.01M12 12v.01M12 18v.01"
          />
        </svg>
      </button>
    </div>
  )
}
