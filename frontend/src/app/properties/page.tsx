'use client'

import { useState, useEffect } from 'react'
import { PropertyListing } from '@/lib/supabase-client'
import PropertyCard from '@/components/PropertyCard'
import FilterSidebar from '@/components/FilterSidebar'
import Pagination from '@/components/Pagination'
import SortingControls, { SortField, SortOrder, SortingState } from '@/components/SortingControls'

export default function PropertiesPage() {
  const [properties, setProperties] = useState<PropertyListing[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [totalCount, setTotalCount] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [filters, setFilters] = useState({
    location: '',
    property_type: '',
    price_range: [0, 100000000],
    min_size: 0,
  })
  
  // Sorting state - default to newest listings first
  const [sorting, setSorting] = useState<SortingState>({
    field: 'created_at',
    order: 'desc'
  })
  
  const itemsPerPage = 20
  
  useEffect(() => {
    // Only run on client side to avoid Vercel build errors
    if (typeof window !== 'undefined') {
      fetchProperties()
    }
  }, [currentPage, filters, sorting])
  
  async function fetchProperties() {
    setLoading(true)
    setError(null) // Clear previous errors
    try {
      console.log('Fetching properties with filters:', filters)
      
      // Build query parameters for the API call
      const offset = (currentPage - 1) * itemsPerPage
      const params = new URLSearchParams({
        limit: itemsPerPage.toString(),
        offset: offset.toString(),
        sortBy: sorting.field,
        sortOrder: sorting.order
      })
      
      // Add filters to query parameters
      if (filters.location) params.append('location', filters.location)
      if (filters.property_type) params.append('property_type', filters.property_type)
      if (filters.min_size) params.append('min_size', filters.min_size.toString())
      if (filters.price_range && filters.price_range.length === 2) {
        params.append('min_price', filters.price_range[0].toString())
        params.append('max_price', filters.price_range[1].toString())
      }
      
      console.log(`Fetching page ${currentPage} (offset: ${offset}, limit: ${itemsPerPage}) with params:`, Object.fromEntries(params))
      
      // Call the server-side API endpoint
      const response = await fetch(`/api/properties?${params}`)
      
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}: ${response.statusText}`)
      }
      
      const result = await response.json()
      
      console.log('API response:', { 
        hasData: !!result.data, 
        dataCount: result.data?.length || 0, 
        totalCount: result.count, 
        hasError: !!result.error 
      })
      
      if (result.error) {
        throw new Error(result.error)
      }
      
      const data = result.data || []
      const count = result.count || 0
      
      if (data.length === 0) {
        console.log('No data returned from API')
      } else {
        console.log('First property:', data[0])
      }
      
      setProperties(data)
      setTotalCount(count)
    } catch (err: any) {
      setError(`Error fetching properties: ${err.message}`)
      console.error('Error fetching properties:', err)
    } finally {
      setLoading(false)
    }
  }
  
  function handleFilterChange(newFilters: any) {
    setFilters(prevFilters => ({
      ...prevFilters,
      ...newFilters
    }))
    setCurrentPage(1) // Reset to first page on filter change
  }
  
  function handlePageChange(page: number) {
    setCurrentPage(page)
  }
  
  function handleSortChange(newSorting: SortingState) {
    console.log('Changing sort to:', newSorting)
    setSorting(newSorting)
    // Reset to first page when sort changes
    setCurrentPage(1)
  }
  
  const totalPages = Math.ceil(totalCount / itemsPerPage)
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Japanese Property Listings</h1>
      
      <div className="flex flex-col md:flex-row gap-8">
        {/* Sidebar with filters */}
        <div className="w-full md:w-1/4">
          <FilterSidebar filters={filters} onFilterChange={handleFilterChange} />
        </div>
        
        {/* Main content area */}
        <div className="w-full md:w-3/4">
          {/* Visible sorting controls above results */}
          {!loading && properties.length > 0 && (
            <div className="mb-4 bg-gray-50 p-4 rounded-lg border border-gray-200 shadow-sm">
              <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
                <h3 className="text-lg font-medium text-gray-700">Sort Properties</h3>
                <SortingControls
                  sorting={sorting}
                  onSortChange={handleSortChange}
                />
              </div>
            </div>
          )}

          {/* Results summary */}
          <div className="mb-6">
            {loading ? (
              <p>Loading properties...</p>
            ) : error ? (
              <p className="text-red-500">Error: {error}</p>
            ) : (
              <p className="text-jp-gray">
                Showing {properties.length} of {totalCount} properties
              </p>
            )}
          </div>
          
          {/* Property grid */}
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="bg-gray-100 animate-pulse rounded-lg h-64"></div>
              ))}
            </div>
          ) : properties.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {properties.map(property => (
                <PropertyCard key={property.id} property={property} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-xl text-jp-gray mb-4">
                {error ? (
                  <span className="text-red-500">{error}</span>
                ) : (
                  "No properties found matching your criteria"
                )}
              </p>
              
              {error && (
                <div className="bg-amber-50 border border-amber-200 p-4 rounded-md mb-6 text-left">
                  <h3 className="font-bold text-amber-800 mb-2">Database Access Issue Detected</h3>
                  <p className="text-sm text-amber-700 mb-2">
                    The application is having trouble accessing the property listing data.
                    We're now using a server-side API with elevated permissions to bypass any Row Level Security restrictions.
                  </p>
                  <p className="text-sm text-amber-700">
                    <strong>If you're still seeing this error:</strong>
                    <ol className="list-decimal pl-5 mt-1 space-y-1">
                      <li>Check your server logs for more details</li>
                      <li>Verify that your environment variables are set correctly</li>
                      <li>Ensure the property_listings table exists in your Supabase database</li>
                      <li>Check that the server has proper network connectivity to Supabase</li>
                    </ol>
                  </p>
                </div>
              )}
              
              <button 
                onClick={() => {
                  setFilters({
                    location: '',
                    property_type: '',
                    price_range: [0, 100000000],
                    min_size: 0,
                  })
                }}
                className="btn-secondary"
              >
                Clear Filters
              </button>
            </div>
          )}
          
          {/* Pagination */}
          {!loading && properties.length > 0 && (
            <div className="mt-8">
              <Pagination 
                currentPage={currentPage} 
                totalPages={totalPages} 
                onPageChange={handlePageChange} 
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
