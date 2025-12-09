/**
 * Unified Search API
 * Calls the search service to get aggregated results from flights, hotels, and cars
 */

const SEARCH_API_BASE_URL = '/api/search';

export interface UnifiedSearchParams {
  query?: string;
  search_type?: 'flight' | 'hotel' | 'car';
  city?: string;
  check_in?: string;
  check_out?: string;
  departure_airport?: string;
  arrival_airport?: string;
  min_price?: number;
  max_price?: number;
  page?: number;
  page_size?: number;
}

export interface UnifiedSearchResponse {
  flights: any[];
  hotels: any[];
  cars: any[];
  total_results: number;
  query: string | null;
  filters: Record<string, any>;
}

export async function unifiedSearch(params: UnifiedSearchParams): Promise<UnifiedSearchResponse> {
  const queryParams = new URLSearchParams();
  
  if (params.query) queryParams.append('query', params.query);
  if (params.search_type) queryParams.append('search_type', params.search_type);
  if (params.city) queryParams.append('city', params.city);
  if (params.check_in) queryParams.append('check_in', params.check_in);
  if (params.check_out) queryParams.append('check_out', params.check_out);
  if (params.departure_airport) queryParams.append('departure_airport', params.departure_airport);
  if (params.arrival_airport) queryParams.append('arrival_airport', params.arrival_airport);
  if (params.min_price !== undefined) queryParams.append('min_price', params.min_price.toString());
  if (params.max_price !== undefined) queryParams.append('max_price', params.max_price.toString());
  if (params.page) queryParams.append('page', params.page.toString());
  if (params.page_size) queryParams.append('page_size', params.page_size.toString());

  try {
    const response = await fetch(`${SEARCH_API_BASE_URL}/search?${queryParams.toString()}`);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Search failed: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Unified search error:', error);
    throw error;
  }
}

