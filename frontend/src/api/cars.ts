/**
 * Car API service
 */

const CAR_API_BASE_URL = '/api/cars';

export interface Car {
  car_id: string;
  provider_name: string;
  car_type: string;
  make: string;
  model: string;
  year: number;
  city: string;
  state: string;
  daily_rental_price: number; // Match backend field name
  is_available: boolean; // Match backend field name
  transmission_type?: string;
  seats?: number;
  doors?: number;
  rating?: number;
  total_reviews?: number;
  features?: string[];
}

export interface CarSearchParams {
  city?: string;
  car_type?: string;
  min_price?: number;
  max_price?: number;
  provider_name?: string;
  page?: number;
  page_size?: number;
}

export interface CarSearchResponse {
  cars: Car[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
  filters_applied?: any;
}

/**
 * Search cars
 */
export async function searchCars(params: CarSearchParams): Promise<CarSearchResponse> {
  try {
    const queryParams = new URLSearchParams();
    
    if (params.city) queryParams.append('city', params.city);
    if (params.car_type) queryParams.append('car_type', params.car_type);
    if (params.min_price) queryParams.append('min_price', params.min_price.toString());
    if (params.max_price) queryParams.append('max_price', params.max_price.toString());
    if (params.provider_name) queryParams.append('provider_name', params.provider_name);
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.page_size) queryParams.append('page_size', params.page_size.toString());

    const response = await fetch(`${CAR_API_BASE_URL}/search?${queryParams.toString()}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to search cars');
    }

    return await response.json();
  } catch (error) {
    console.error('Car search error:', error);
    throw error;
  }
}

/**
 * Get car by ID
 */
export async function getCar(carId: string): Promise<Car> {
  try {
    const response = await fetch(`${CAR_API_BASE_URL}/${carId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get car');
    }

    return await response.json();
  } catch (error) {
    console.error('Get car error:', error);
    throw error;
  }
}

