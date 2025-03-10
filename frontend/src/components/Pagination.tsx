'use client'

type PaginationProps = {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
}

export default function Pagination({ 
  currentPage, 
  totalPages, 
  onPageChange 
}: PaginationProps) {
  
  // Generate page numbers to display
  const getPageNumbers = () => {
    const pageNumbers: (number | string)[] = []
    
    // Always show first page
    pageNumbers.push(1)
    
    // Add ellipsis if needed
    if (currentPage > 3) {
      pageNumbers.push('...')
    }
    
    // Add pages around current page
    for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
      pageNumbers.push(i)
    }
    
    // Add ellipsis if needed
    if (currentPage < totalPages - 2) {
      pageNumbers.push('...')
    }
    
    // Always show last page if there is more than 1 page
    if (totalPages > 1) {
      pageNumbers.push(totalPages)
    }
    
    return pageNumbers
  }
  
  const pageNumbers = getPageNumbers()
  
  return (
    <div className="flex justify-center items-center space-x-2">
      {/* Previous button */}
      <button
        onClick={() => currentPage > 1 && onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className={`px-3 py-1 rounded ${
          currentPage === 1
            ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
            : 'bg-jp-navy text-white hover:bg-jp-red transition-colors'
        }`}
      >
        &laquo;
      </button>
      
      {/* Page numbers */}
      {pageNumbers.map((page, index) => (
        <button
          key={index}
          onClick={() => typeof page === 'number' && onPageChange(page)}
          disabled={page === '...'}
          className={`px-3 py-1 rounded ${
            page === currentPage
              ? 'bg-jp-red text-white'
              : page === '...'
                ? 'bg-transparent text-jp-gray cursor-default'
                : 'bg-jp-navy text-white hover:bg-jp-red transition-colors'
          }`}
        >
          {page}
        </button>
      ))}
      
      {/* Next button */}
      <button
        onClick={() => currentPage < totalPages && onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages || totalPages === 0}
        className={`px-3 py-1 rounded ${
          currentPage === totalPages || totalPages === 0
            ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
            : 'bg-jp-navy text-white hover:bg-jp-red transition-colors'
        }`}
      >
        &raquo;
      </button>
    </div>
  )
}
