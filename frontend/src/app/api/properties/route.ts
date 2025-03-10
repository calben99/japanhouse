import { createClient } from '@supabase/supabase-js';
import { NextResponse } from 'next/server';

// Use service key to bypass RLS
const supabaseUrl = process.env.SUPABASE_URL || '';
const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY || '';

if (!supabaseUrl || !supabaseServiceKey) {
  console.error('Missing Supabase credentials');
}

// Create a Supabase client with the service key (only on server)
const supabase = createClient(supabaseUrl, supabaseServiceKey);

export async function GET(request: Request) {
  try {
    // Parse URL and query parameters
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '20', 10);
    const offset = parseInt(searchParams.get('offset') || '0', 10);
    const sortBy = searchParams.get('sortBy') || 'created_at';
    const sortOrder = searchParams.get('sortOrder') || 'desc';
    
    // Parse filters
    const location = searchParams.get('location') || '';
    const property_type = searchParams.get('property_type') || '';
    const min_size = searchParams.get('min_size') || '';
    const min_price = searchParams.get('min_price') || '';
    const max_price = searchParams.get('max_price') || '';
    
    console.log('API: Fetching properties with params:', { 
      limit, offset, sortBy, sortOrder, 
      location, property_type, min_size, min_price, max_price 
    });

    // Build the Supabase query
    // Validate sortBy field to ensure it's a valid column name
    const validSortFields = ['created_at', 'price', 'size', 'land_area'];
    const sanitizedSortBy = validSortFields.includes(sortBy) ? sortBy : 'created_at';
    
    console.log(`API: Sorting by ${sanitizedSortBy} in ${sortOrder} order`);
    
    let query = supabase
      .from('property_listings')
      .select('*', { count: 'exact' })
      .order(sanitizedSortBy, { ascending: sortOrder === 'asc' })
      .range(offset, offset + limit - 1);
    
    // Apply filters
    if (location) {
      query = query.ilike('location', `%${location}%`);
    }
    
    if (property_type) {
      // Try to use source field if property_type doesn't exist
      query = query.eq('source', property_type);
    }
    
    if (min_size) {
      query = query.gte('size', parseFloat(min_size));
    }
    
    if (min_price && max_price) {
      query = query.gte('price', parseFloat(min_price)).lte('price', parseFloat(max_price));
    } else if (min_price) {
      query = query.gte('price', parseFloat(min_price));
    } else if (max_price) {
      query = query.lte('price', parseFloat(max_price));
    }
    
    // Execute the query
    const { data, error, count } = await query;
    
    if (error) {
      console.error('API: Supabase query error:', error);
      return NextResponse.json({ error: error.message }, { status: 500 });
    }
    
    // Parse any JSON strings in the data
    const parsedData = data?.map(item => {
      const parsed = { ...item };
      
      // Parse images if it's a string
      if (typeof parsed.images === 'string') {
        try {
          parsed.images = JSON.parse(parsed.images);
        } catch (e) {
          // If parsing fails, keep as is
        }
      }
      
      // Parse features if it's a string
      if (typeof parsed.features === 'string') {
        try {
          parsed.features = JSON.parse(parsed.features);
        } catch (e) {
          // If parsing fails, keep as is
        }
      }
      
      return parsed;
    }) || [];
    
    console.log(`API: Found ${parsedData.length} properties out of ${count || 0} total`);
    
    // Return the data
    return NextResponse.json({ 
      data: parsedData, 
      count: count || 0 
    });
    
  } catch (err: any) {
    console.error('API: Unexpected error:', err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
