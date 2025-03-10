import Image from 'next/image'
import Link from 'next/link'
import { PropertyListing } from '@/lib/supabase-client'

type PropertyCardProps = {
  property: PropertyListing
}

export default function PropertyCard({ property }: PropertyCardProps) {
  // Format price for display
  const formatPrice = (price: string | number) => {
    if (!price) return 'Price on request';
    
    // If price is already a string and contains non-numeric characters, return as is
    if (typeof price === 'string' && isNaN(Number(price.replace(/,/g, '')))) {
      return price;
    }
    
    // Convert to number and format
    const numPrice = typeof price === 'string' ? Number(price.replace(/,/g, '')) : price;
    if (isNaN(numPrice)) return 'Price on request';
    
    // Format in Japanese Yen
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
      maximumFractionDigits: 0
    }).format(numPrice);
  };
  
  // Get first image or placeholder
  const firstImage = Array.isArray(property.images) && property.images.length > 0 
    ? property.images[0] 
    : typeof property.images === 'string' && property.images
      ? property.images
      : '/placeholder-property.jpg';
      
  // Format features for display  
  const formatFeatures = () => {
    if (!property.features) return [];
    
    const features = Array.isArray(property.features) 
      ? property.features 
      : typeof property.features === 'string'
        ? [property.features]
        : [];
        
    return features.slice(0, 3); // Limit to 3 features
  };
  
  return (
    <div className="card overflow-hidden flex flex-col h-full">
      {/* Property Image */}
      <div className="relative h-48 w-full bg-gray-200">
        {firstImage ? (
          <Image 
            src={firstImage}
            alt={property.title || 'Property image'}
            fill
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            className="object-cover"
            onError={(e) => {
              // If image fails to load, replace with placeholder
              const target = e.target as HTMLImageElement;
              target.src = '/placeholder-property.jpg';
            }}
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <span className="text-gray-400">No image available</span>
          </div>
        )}
        
        {/* Source tag */}
        {property.source && (
          <div className="absolute top-2 right-2 bg-jp-navy text-white text-xs px-2 py-1 rounded">
            {property.source}
          </div>
        )}
      </div>
      
      {/* Property Details */}
      <div className="p-4 flex flex-col flex-grow">
        <h3 className="font-bold text-lg mb-2 line-clamp-2">
          {property.title || 'Untitled Property'}
        </h3>
        
        <p className="text-jp-gray text-sm mb-2">
          {property.location || 'Location not specified'}
        </p>
        
        <p className="text-jp-red font-semibold text-xl mb-3">
          {formatPrice(property.price)}
        </p>
        
        <div className="grid grid-cols-2 gap-2 text-sm mb-4">
          {property.size && (
            <div>
              <span className="text-jp-gray">Size:</span> {property.size}㎡
            </div>
          )}
          
          {property.layout && (
            <div>
              <span className="text-jp-gray">Layout:</span> {property.layout}
            </div>
          )}
          
          {property.year_built && (
            <div>
              <span className="text-jp-gray">Built:</span> {property.year_built}
            </div>
          )}
          
          {property.building_type && (
            <div>
              <span className="text-jp-gray">Type:</span> {property.building_type}
            </div>
          )}
        </div>
        
        {/* Features */}
        {formatFeatures().length > 0 && (
          <div className="mb-4">
            <div className="flex flex-wrap gap-1">
              {formatFeatures().map((feature, index) => (
                <span 
                  key={index} 
                  className="bg-jp-light text-jp-navy text-xs px-2 py-1 rounded"
                >
                  {feature}
                </span>
              ))}
            </div>
          </div>
        )}
        
        {/* View button - at the bottom of the card */}
        <div className="mt-auto pt-3">
          <Link 
            href={property.url || '#'} 
            target="_blank" 
            className="btn-primary w-full text-center block"
            rel="noopener noreferrer"
          >
            View Property
          </Link>
        </div>
      </div>
    </div>
  )
}
