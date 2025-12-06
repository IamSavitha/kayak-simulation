/**
 * Admin Hotel Management API functions
 */

// Always use proxy URLs - Vite dev server will route them correctly
const ADMIN_API_BASE_URL = '/api/admin';
const HOTEL_API_BASE_URL = '/api/hotels';

export interface HotelCreateData {
  hotel_id: string;
  hotel_name: string;
  description?: string;
  address: string;
  city: string;
  state?: string;
  zip_code?: string;
  star_rating?: number;
  amenities?: string;
  phone_number?: string;
  email?: string;
  website?: string;
  image_url?: string;
}

export interface HotelUpdateData {
  hotel_name?: string;
  description?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  star_rating?: number;
  amenities?: string;
  phone_number?: string;
  email?: string;
  website?: string;
  image_url?: string;
  is_active?: boolean;
}

export interface HotelRoomCreateData {
  room_id: string;
  room_type: 'single' | 'double' | 'suite' | 'deluxe';
  room_number?: string;
  price_per_night: number;
  max_occupancy: number;
  total_rooms: number;
}

export interface HotelRoomUpdateData {
  price_per_night?: number;
  max_occupancy?: number;
  total_rooms?: number;
  available_rooms?: number;
  is_active?: boolean;
}

export interface HotelRoomResponse {
  room_id: string;
  hotel_id: string;
  room_type: string;
  room_number?: string;
  price_per_night: string;
  max_occupancy: number;
  total_rooms: number;
  available_rooms: number;
  is_active: boolean;
}

export interface HotelResponse {
  hotel_id: string;
  hotel_name: string;
  description?: string;
  address: string;
  city: string;
  state?: string;
  zip_code?: string;
  star_rating?: number;
  rating: number;
  total_reviews: number;
  amenities?: string;
  phone_number?: string;
  email?: string;
  website?: string;
  image_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  rooms?: HotelRoomResponse[];
}

/**
 * Get admin token from localStorage
 */
function getAdminToken(): string | null {
  return localStorage.getItem('admin_token') || localStorage.getItem('token');
}

/**
 * Create a new hotel with optional image upload
 */
export async function createHotel(
  data: HotelCreateData,
  imageFile?: File
): Promise<HotelResponse> {
  const token = getAdminToken();
  if (!token) {
    throw new Error('Admin authentication required');
  }

  try {
    const formData = new FormData();
    formData.append('hotel_data', JSON.stringify(data));
    if (imageFile) {
      formData.append('image', imageFile);
    }

    const response = await fetch(`${ADMIN_API_BASE_URL}/hotels`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        // Don't set Content-Type header - browser will set it with boundary for FormData
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      const errorMessage = error.detail || error.message || 'Failed to create hotel';
      throw new Error(errorMessage);
    }

    const result = await response.json();
    return result.hotel || result;
  } catch (error) {
    console.error('Create hotel error:', error);
    throw error;
  }
}

/**
 * Update a hotel with optional image upload
 */
export async function updateHotel(
  hotelId: string,
  data: HotelUpdateData,
  imageFile?: File
): Promise<HotelResponse> {
  const token = getAdminToken();
  if (!token) {
    throw new Error('Admin authentication required');
  }

  try {
    const formData = new FormData();
    formData.append('hotel_data', JSON.stringify(data));
    if (imageFile) {
      formData.append('image', imageFile);
    }

    const response = await fetch(`${ADMIN_API_BASE_URL}/hotels/${hotelId}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        // Don't set Content-Type header - browser will set it with boundary for FormData
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      const errorMessage = error.detail || error.message || 'Failed to update hotel';
      throw new Error(errorMessage);
    }

    const result = await response.json();
    return result.hotel || result;
  } catch (error) {
    console.error('Update hotel error:', error);
    throw error;
  }
}

/**
 * Delete a hotel
 */
export async function deleteHotel(hotelId: string): Promise<{ message: string }> {
  const token = getAdminToken();
  if (!token) {
    throw new Error('Admin authentication required');
  }

  try {
    const response = await fetch(`${ADMIN_API_BASE_URL}/hotels/${hotelId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      const errorMessage = error.detail || error.message || 'Failed to delete hotel';
      throw new Error(errorMessage);
    }

    return { message: 'Hotel deleted successfully' };
  } catch (error) {
    console.error('Delete hotel error:', error);
    throw error;
  }
}

/**
 * Get all hotels
 */
export async function getAllHotels(): Promise<HotelResponse[]> {
  const token = getAdminToken();
  if (!token) {
    throw new Error('Admin authentication required');
  }

  try {
    const response = await fetch(`${ADMIN_API_BASE_URL}/hotels`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      let errorMsg = 'Failed to fetch hotels';
      try {
        const error = await response.json();
        errorMsg = error.detail || error.message || errorMsg;
      } catch (parseError) {
        errorMsg = `HTTP ${response.status}: ${response.statusText}`;
      }
      throw new Error(errorMsg);
    }

    const data = await response.json();
    return data.hotels || [];
  } catch (error: any) {
    console.error('Get hotels error:', error);
    const errorMessage = error instanceof Error ? error.message : String(error);
    throw new Error(errorMessage);
  }
}

/**
 * Get hotel rooms
 */
export async function getHotelRooms(hotelId: string): Promise<HotelRoomResponse[]> {
  const token = getAdminToken();
  if (!token) {
    throw new Error('Admin authentication required');
  }

  try {
    const response = await fetch(`${ADMIN_API_BASE_URL}/hotels/${hotelId}/rooms`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch rooms');
    }

    return await response.json();
  } catch (error) {
    console.error('Get hotel rooms error:', error);
    throw error;
  }
}

/**
 * Create a hotel room
 */
export async function createHotelRoom(
  hotelId: string,
  data: HotelRoomCreateData
): Promise<HotelRoomResponse> {
  const token = getAdminToken();
  if (!token) {
    throw new Error('Admin authentication required');
  }

  try {
    const response = await fetch(`${ADMIN_API_BASE_URL}/hotels/${hotelId}/rooms`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      const errorMessage = error.detail || error.message || 'Failed to create room';
      throw new Error(errorMessage);
    }

    const result = await response.json();
    return result.room || result;
  } catch (error) {
    console.error('Create hotel room error:', error);
    throw error;
  }
}

/**
 * Update a hotel room
 */
export async function updateHotelRoom(
  hotelId: string,
  roomId: string,
  data: HotelRoomUpdateData
): Promise<HotelRoomResponse> {
  const token = getAdminToken();
  if (!token) {
    throw new Error('Admin authentication required');
  }

  try {
    const response = await fetch(`${ADMIN_API_BASE_URL}/hotels/${hotelId}/rooms/${roomId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      const errorMessage = error.detail || error.message || 'Failed to update room';
      throw new Error(errorMessage);
    }

    const result = await response.json();
    return result.room || result;
  } catch (error) {
    console.error('Update hotel room error:', error);
    throw error;
  }
}

/**
 * Delete a hotel room
 */
export async function deleteHotelRoom(hotelId: string, roomId: string): Promise<{ message: string }> {
  const token = getAdminToken();
  if (!token) {
    throw new Error('Admin authentication required');
  }

  try {
    const response = await fetch(`${ADMIN_API_BASE_URL}/hotels/${hotelId}/rooms/${roomId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      const errorMessage = error.detail || error.message || 'Failed to delete room';
      throw new Error(errorMessage);
    }

    return { message: 'Room deleted successfully' };
  } catch (error) {
    console.error('Delete hotel room error:', error);
    throw error;
  }
}
