/**
 * Hotel API service
 */

const HOTEL_API_BASE_URL = '/api/hotels';

export interface Hotel {
  hotel_id: string;
  hotel_name: string;
  description?: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  star_rating: number;
  rating?: number;
  total_reviews?: number;
  amenities?: string[] | string;
  phone_number?: string;
  email?: string;
  website?: string;
  available_rooms?: number; // Available rooms for selected dates
  total_available_rooms?: number; // Total available rooms
}

export interface HotelSearchParams {
  city?: string;
  state?: string;
  check_in_date?: string;
  check_out_date?: string;
  min_star_rating?: number;
  max_star_rating?: number;
  min_price?: number;
  max_price?: number;
  amenities?: string;
  num_rooms?: number;
  num_guests?: number;
  sort_by?: string;
  sort_order?: string;
  page?: number;
  page_size?: number;
}

export interface HotelSearchResponse {
  hotels: Hotel[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
  filters_applied?: any;
}

/**
 * Search hotels
 */
export async function searchHotels(params: HotelSearchParams): Promise<HotelSearchResponse> {
  try {
    const queryParams = new URLSearchParams();
    
    if (params.city) queryParams.append('city', params.city);
    if (params.state) queryParams.append('state', params.state);
    if (params.check_in_date) queryParams.append('check_in_date', params.check_in_date);
    if (params.check_out_date) queryParams.append('check_out_date', params.check_out_date);
    if (params.min_star_rating) queryParams.append('min_star_rating', params.min_star_rating.toString());
    if (params.max_star_rating) queryParams.append('max_star_rating', params.max_star_rating.toString());
    if (params.min_price) queryParams.append('min_price', params.min_price.toString());
    if (params.max_price) queryParams.append('max_price', params.max_price.toString());
    if (params.amenities) queryParams.append('amenities', params.amenities);
    if (params.num_rooms) queryParams.append('num_rooms', params.num_rooms.toString());
    if (params.num_guests) queryParams.append('num_guests', params.num_guests.toString());
    if (params.sort_by) queryParams.append('sort_by', params.sort_by);
    if (params.sort_order) queryParams.append('sort_order', params.sort_order);
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.page_size) queryParams.append('page_size', params.page_size.toString());

    const response = await fetch(`${HOTEL_API_BASE_URL}/search?${queryParams.toString()}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to search hotels');
    }

    return await response.json();
  } catch (error) {
    console.error('Hotel search error:', error);
    throw error;
  }
}

/**
 * Get hotel by ID
 */
export async function getHotel(hotelId: string): Promise<Hotel> {
  try {
    const response = await fetch(`${HOTEL_API_BASE_URL}/${hotelId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get hotel');
    }

    return await response.json();
  } catch (error) {
    console.error('Get hotel error:', error);
    throw error;
  }
}

