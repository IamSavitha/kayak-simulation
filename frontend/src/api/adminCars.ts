/**
 * Admin Car Management API functions
 */

// Always use proxy URLs - Vite dev server will route them correctly
const ADMIN_API_BASE_URL = '/api/admin';
const CAR_API_BASE_URL = '/api/cars';

export interface CarCreateData {
  car_id: string;
  car_type: 'sedan' | 'suv' | 'compact' | 'luxury' | 'van';
  make: string;
  model: string;
  year: number;
  provider_name: string;
  transmission_type: 'automatic' | 'manual';
  seats: number;
  doors: number;
  daily_rental_price: number;
  pickup_location: string;
  city?: string;
  state?: string;
  image_url?: string;
}

export interface CarUpdateData {
  car_type?: 'sedan' | 'suv' | 'compact' | 'luxury' | 'van';
  make?: string;
  model?: string;
  year?: number;
  provider_name?: string;
  transmission_type?: 'automatic' | 'manual';
  seats?: number;
  doors?: number;
  daily_rental_price?: number;
  pickup_location?: string;
  city?: string;
  state?: string;
  image_url?: string;
  is_available?: boolean;
  is_active?: boolean;
}

export interface CarResponse {
  car_id: string;
  car_type: string;
  make: string;
  model: string;
  year: number;
  provider_name: string;
  transmission_type: string;
  seats: number;
  doors: number;
  daily_rental_price: string;
  pickup_location: string;
  city?: string;
  state?: string;
  image_url?: string;
  is_available: boolean;
  is_active: boolean;
  rating: number;
  total_reviews: number;
  created_at: string;
  updated_at: string;
}

function getAdminToken(): string | null {
  return localStorage.getItem('admin_token') || localStorage.getItem('token');
}

export async function createCar(
  data: CarCreateData,
  imageFile?: File
): Promise<{ message: string; car: CarResponse }> {
  const token = getAdminToken();
  if (!token) throw new Error('Admin authentication required');

  const formData = new FormData();
  formData.append('car_data', JSON.stringify(data));
  if (imageFile) {
    formData.append('image', imageFile);
  }

  const response = await fetch(`${ADMIN_API_BASE_URL}/cars`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create car');
  }
  return await response.json();
}

export async function updateCar(
  carId: string,
  data: CarUpdateData,
  imageFile?: File
): Promise<{ message: string; car: CarResponse }> {
  const token = getAdminToken();
  if (!token) throw new Error('Admin authentication required');

  const formData = new FormData();
  formData.append('car_data', JSON.stringify(data));
  if (imageFile) {
    formData.append('image', imageFile);
  }

  const response = await fetch(`${ADMIN_API_BASE_URL}/cars/${carId}`, {
    method: 'PUT',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update car');
  }
  return await response.json();
}

export async function deleteCar(carId: string): Promise<{ message: string }> {
  const token = getAdminToken();
  if (!token) throw new Error('Admin authentication required');

  const response = await fetch(`${ADMIN_API_BASE_URL}/cars/${carId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete car');
  }
  return { message: 'Car deleted successfully' };
}

export async function getAllCars(): Promise<CarResponse[]> {
  const token = getAdminToken();
  if (!token) {
    throw new Error('Admin authentication required');
  }

  try {
    const response = await fetch(`${ADMIN_API_BASE_URL}/cars`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      let errorMsg = 'Failed to fetch cars';
      try {
        const error = await response.json();
        errorMsg = error.detail || error.message || errorMsg;
      } catch (parseError) {
        errorMsg = `HTTP ${response.status}: ${response.statusText}`;
      }
      throw new Error(errorMsg);
    }

    const data = await response.json();
    return data.cars || [];
  } catch (error: any) {
    console.error('Get cars error:', error);
    const errorMessage = error instanceof Error ? error.message : String(error);
    throw new Error(errorMessage);
  }
}
