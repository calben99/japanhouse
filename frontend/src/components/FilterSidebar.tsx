'use client'

import { useState, useEffect } from 'react'
import { getSupabaseClient } from '@/lib/supabase-client'

type FilterSidebarProps = {
  filters: {
    location: string
    property_type?: string // Make optional since column doesn't exist
    source?: string       // Add source as alternative filter
    price_range: number[]
    min_size: number
  }
  onFilterChange: (filters: any) => void
}

export default function FilterSidebar({ filters, onFilterChange }: FilterSidebarProps) {
  const [locations, setLocations] = useState<string[]>([])
  const [propertyTypes, setPropertyTypes] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    // Only run on client side
    if (typeof window === 'undefined') return;
    
    async function fetchFilterOptions() {
      setLoading(true)
      try {
        // Get Supabase client
        const supabase = getSupabaseClient();
        
        // Fetch distinct locations
        const { data: locationData, error: locationError } = await supabase
          .from('property_listings')
          .select('location')
          .not('location', 'is', null)
          .order('location')
          
        if (locationError) throw locationError
        
        // Instead of property_type (which doesn't exist), try to fetch sources
        const { data: sourceData, error: sourceError } = await supabase
          .from('property_listings')
          .select('source')
          .not('source', 'is', null)
          .order('source')
          
        // Just log error but don't throw - we'll use default property types
        if (sourceError) {
          console.error('Error fetching sources:', sourceError)
        }
        
        // Extract unique values
        const uniqueLocations = Array.from(new Set(
          locationData
            .map(item => item.location)
            .filter(Boolean)
            .map(loc => {
              // Extract prefecture or first part of location
              const parts = loc.split(/[,，]/)
              return parts[0].trim()
            })
        ))
        
        // Use source data as property type or fallback to defaults
        let uniqueTypes: string[] = [];
        if (sourceData && sourceData.length > 0) {
          uniqueTypes = Array.from(new Set(
            sourceData
              .map(item => item.source)
              .filter(Boolean)
          )) as string[]
        } else {
          // Fallback to default property types
          uniqueTypes = ['rent', 'buy'];
        }
        
        setLocations(uniqueLocations)
        setPropertyTypes(uniqueTypes)
      } catch (error) {
        console.error('Error fetching filter options:', error)
      } finally {
        setLoading(false)
      }
    }
    
    fetchFilterOptions()
  }, [])
  
  const handleLocationChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFilterChange({ location: e.target.value })
  }
  
  const handlePropertyTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    // Use source instead of property_type since that's what we're displaying
    onFilterChange({ source: e.target.value })
  }
  
  const handlePriceRangeChange = (type: 'min' | 'max', value: string) => {
    const numValue = parseInt(value, 10) || 0
    const [min, max] = filters.price_range
    
    if (type === 'min') {
      onFilterChange({ price_range: [numValue, max] })
    } else {
      onFilterChange({ price_range: [min, numValue] })
    }
  }
  
  const handleMinSizeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10) || 0
    onFilterChange({ min_size: value })
  }
  
  const handleResetFilters = () => {
    onFilterChange({
      location: '',
      property_type: '',
      price_range: [0, 100000000],
      min_size: 0
    })
  }
  
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-6">Filters</h2>
      
      {loading ? (
        <div className="animate-pulse space-y-4">
          <div className="h-10 bg-gray-200 rounded"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Location Filter */}
          <div>
            <label className="block text-sm font-medium text-jp-gray mb-2">
              Location
            </label>
            <select
              value={filters.location}
              onChange={handleLocationChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-jp-red focus:ring focus:ring-jp-red focus:ring-opacity-50"
            >
              <option value="">All Locations</option>
              {locations.map(location => (
                <option key={location} value={location}>
                  {location}
                </option>
              ))}
            </select>
          </div>
          
          {/* Property Type Filter */}
          <div>
            <label className="block text-sm font-medium text-jp-gray mb-2">
              Property Type
            </label>
            <select
              value={filters.property_type}
              onChange={handlePropertyTypeChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-jp-red focus:ring focus:ring-jp-red focus:ring-opacity-50"
            >
              <option value="">All Types</option>
              {propertyTypes.map(type => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>
          
          {/* Price Range Filter */}
          <div>
            <label className="block text-sm font-medium text-jp-gray mb-2">
              Price Range (¥)
            </label>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs text-jp-gray mb-1">Min</label>
                <input
                  type="number"
                  min="0"
                  step="1000000"
                  value={filters.price_range[0]}
                  onChange={(e) => handlePriceRangeChange('min', e.target.value)}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-jp-red focus:ring focus:ring-jp-red focus:ring-opacity-50"
                />
              </div>
              <div>
                <label className="block text-xs text-jp-gray mb-1">Max</label>
                <input
                  type="number"
                  min="0"
                  step="1000000"
                  value={filters.price_range[1]}
                  onChange={(e) => handlePriceRangeChange('max', e.target.value)}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-jp-red focus:ring focus:ring-jp-red focus:ring-opacity-50"
                />
              </div>
            </div>
          </div>
          
          {/* Minimum Size Filter */}
          <div>
            <label className="block text-sm font-medium text-jp-gray mb-2">
              Minimum Size (㎡)
            </label>
            <input
              type="number"
              min="0"
              value={filters.min_size}
              onChange={handleMinSizeChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-jp-red focus:ring focus:ring-jp-red focus:ring-opacity-50"
            />
          </div>
          
          {/* Reset Filters Button */}
          <button
            onClick={handleResetFilters}
            className="w-full py-2 px-4 bg-gray-200 text-jp-gray rounded hover:bg-gray-300 transition-colors mt-4"
          >
            Reset Filters
          </button>
        </div>
      )}
    </div>
  )
}
