import { Fragment } from 'react'
import { Menu, Transition } from '@headlessui/react'
import { ChevronDownIcon, ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/20/solid'

// Fallback icons in case the imported ones don't work
const FallbackChevronDown = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
  </svg>
)

const FallbackArrowUp = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
  </svg>
)

const FallbackArrowDown = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
  </svg>
)

// Define the sorting options
export type SortField = 'created_at' | 'price' | 'size' | 'land_area'
export type SortOrder = 'asc' | 'desc'

interface SortOption {
  value: SortField
  label: string
}

const sortOptions: SortOption[] = [
  { value: 'created_at', label: 'Date Listed' },
  { value: 'price', label: 'Price' },
  { value: 'size', label: 'House Area' },
  { value: 'land_area', label: 'Land Area' },
]

export interface SortingState {
  field: SortField
  order: SortOrder
}

interface SortingControlsProps {
  sorting: SortingState
  onSortChange: (newSorting: SortingState) => void
}

export default function SortingControls({ sorting, onSortChange }: SortingControlsProps) {
  const currentSort = sortOptions.find(option => option.value === sorting.field) || sortOptions[0]
  
  const toggleOrder = () => {
    onSortChange({
      ...sorting,
      order: sorting.order === 'asc' ? 'desc' : 'asc'
    })
  }
  
  const selectSortField = (field: SortField) => {
    onSortChange({
      field,
      order: sorting.order
    })
  }
  
  // Log to see if component is rendering
  console.log('SortingControls rendering with', sorting)
  
  return (
    <div className="flex items-center space-x-2 bg-white p-2 rounded-md" data-testid="sorting-controls">
      <span className="text-sm text-gray-500 font-medium">Sort by:</span>
      
      <Menu as="div" className="relative inline-block text-left">
        <div>
          <Menu.Button className="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500">
            {currentSort.label}
            <span className="-mr-1 ml-2 h-5 w-5">
              {ChevronDownIcon ? <ChevronDownIcon aria-hidden="true" /> : <FallbackChevronDown />}
            </span>
          </Menu.Button>
        </div>

        <Transition
          as={Fragment}
          enter="transition ease-out duration-100"
          enterFrom="transform opacity-0 scale-95"
          enterTo="transform opacity-100 scale-100"
          leave="transition ease-in duration-75"
          leaveFrom="transform opacity-100 scale-100"
          leaveTo="transform opacity-0 scale-95"
        >
          <Menu.Items className="absolute right-0 z-10 mt-2 w-40 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
            <div className="py-1">
              {sortOptions.map((option) => (
                <Menu.Item key={option.value}>
                  {({ active }) => (
                    <button
                      type="button"
                      className={`
                        ${active ? 'bg-gray-100 text-gray-900' : 'text-gray-700'}
                        ${sorting.field === option.value ? 'font-medium text-jp-indigo' : ''}
                        block w-full px-4 py-2 text-left text-sm
                      `}
                      onClick={() => selectSortField(option.value)}
                    >
                      {option.label}
                    </button>
                  )}
                </Menu.Item>
              ))}
            </div>
          </Menu.Items>
        </Transition>
      </Menu>
      
      <button
        type="button"
        onClick={toggleOrder}
        className="inline-flex items-center rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-jp-indigo"
      >
        {sorting.order === 'asc' ? (
          <span className="h-5 w-5 text-gray-500">
            {ArrowUpIcon ? <ArrowUpIcon aria-hidden="true" /> : <FallbackArrowUp />}
          </span>
        ) : (
          <span className="h-5 w-5 text-gray-500">
            {ArrowDownIcon ? <ArrowDownIcon aria-hidden="true" /> : <FallbackArrowDown />}
          </span>
        )}
        <span className="sr-only">
          {sorting.order === 'asc' ? 'Sort ascending' : 'Sort descending'}
        </span>
      </button>
    </div>
  )
}
