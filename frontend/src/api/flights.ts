/**
 * Flight API service
 */

const FLIGHT_API_BASE_URL = '/api/flights';

export interface Flight {
  flight_id: string;
  airline_name: string;
  departure_airport: string;
  arrival_airport: string;
  departure_datetime: string;
  arrival_datetime: string;
  flight_class: string;
  base_price: number;
  available_seats: number;
  total_seats: number;
  duration_minutes?: number;
  stops?: number;
  rating?: number;
}

export interface FlightSearchParams {
  departure_airport?: string;
  arrival_airport?: string;
  departure_date?: string;
  return_date?: string;
  flight_class?: string;
  min_price?: number;
  max_price?: number;
  airline_name?: string;
  min_departure_time?: string;
  max_departure_time?: string;
  num_passengers?: number;
  sort_by?: string;
  sort_order?: string;
  page?: number;
  page_size?: number;
}

export interface FlightSearchResponse {
  flights: Flight[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
  filters_applied?: any;
}

/**
 * Search flights
 */
export async function searchFlights(params: FlightSearchParams): Promise<FlightSearchResponse> {
  try {
    const queryParams = new URLSearchParams();
    
    if (params.departure_airport) queryParams.append('departure_airport', params.departure_airport);
    if (params.arrival_airport) queryParams.append('arrival_airport', params.arrival_airport);
    if (params.departure_date) queryParams.append('departure_date', params.departure_date);
    if (params.return_date) queryParams.append('return_date', params.return_date);
    if (params.flight_class) queryParams.append('flight_class', params.flight_class);
    if (params.min_price) queryParams.append('min_price', params.min_price.toString());
    if (params.max_price) queryParams.append('max_price', params.max_price.toString());
    if (params.airline_name) queryParams.append('airline_name', params.airline_name);
    if (params.min_departure_time) queryParams.append('min_departure_time', params.min_departure_time);
    if (params.max_departure_time) queryParams.append('max_departure_time', params.max_departure_time);
    if (params.num_passengers) queryParams.append('num_passengers', params.num_passengers.toString());
    if (params.sort_by) queryParams.append('sort_by', params.sort_by);
    if (params.sort_order) queryParams.append('sort_order', params.sort_order);
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.page_size) queryParams.append('page_size', params.page_size.toString());

    const response = await fetch(`${FLIGHT_API_BASE_URL}/search?${queryParams.toString()}`);

    if (!response.ok) {
      const error = await response.json();
      // Handle nested error detail structure
      const errorMessage = error.detail?.message || error.detail || error.message || 'Failed to search flights';
      
      // If error is "Flight not found" or "NOT_FOUND", return empty result instead of throwing
      if (errorMessage.toLowerCase().includes('not found') || error.detail?.error_code === 'NOT_FOUND') {
        return {
          flights: [],
          total_count: 0,
          page: params.page || 1,
          page_size: params.page_size || 20,
          total_pages: 0
        };
      }
      
      throw new Error(errorMessage);
    }

    const data = await response.json();
    
    // Ensure response has the expected structure
    if (data && typeof data === 'object' && 'flights' in data) {
      return data;
    }
    
    // If response doesn't have flights array, return empty result
    return {
      flights: [],
      total_count: 0,
      page: params.page || 1,
      page_size: params.page_size || 20,
      total_pages: 0
    };
  } catch (error) {
    console.error('Flight search error:', error);
    throw error;
  }
}

/**
 * Get flight by ID
 */
export async function getFlight(flightId: string): Promise<Flight> {
  try {
    const response = await fetch(`${FLIGHT_API_BASE_URL}/${flightId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get flight');
    }

    return await response.json();
  } catch (error) {
    console.error('Get flight error:', error);
    throw error;
  }
}

