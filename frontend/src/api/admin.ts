/**
 * Admin API functions
 */

// Always use proxy URLs - Vite dev server will route them correctly
const ADMIN_API_BASE_URL = '/api/admin';

export interface AdminSignupData {
  admin_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone_number?: string;
  password: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  role?: 'admin' | 'super_admin' | 'moderator' | 'ADMIN' | 'SUPER_ADMIN' | 'MODERATOR';
}

export interface AdminLoginData {
  email: string;
  password: string;
}

export interface AdminTokenResponse {
  access_token: string;
  token_type: string;
  admin: {
    admin_id: string;
    first_name: string;
    last_name: string;
    email: string;
    phone_number?: string;
    role: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
  };
}

/**
 * Register a new admin with optional profile image upload
 */
export async function adminSignup(data: AdminSignupData, imageFile?: File): Promise<any> {
  try {
    const formData = new FormData();
    formData.append('admin_data', JSON.stringify(data));
    if (imageFile) {
      formData.append('image', imageFile);
    }

    const response = await fetch(`${ADMIN_API_BASE_URL}/auth/signup`, {
      method: 'POST',
      // Don't set Content-Type header - browser will set it with boundary for FormData
      body: formData,
    });

    if (!response.ok) {
      let errorMessage = 'Failed to create admin account';
      try {
        const error = await response.json();
        errorMessage = error.detail || error.message || errorMessage;
      } catch (e) {
        // If response is not JSON, use status text
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error: any) {
    console.error('Admin signup error:', error);
    // Handle network errors
    if (error.message === 'Failed to fetch' || error.name === 'TypeError') {
      throw new Error('Unable to connect to admin service. Please check if the service is running.');
    }
    throw error;
  }
}

/**
 * Login admin
 */
export async function adminLogin(data: AdminLoginData): Promise<AdminTokenResponse> {
  try {
    const response = await fetch(`${ADMIN_API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      let errorMessage = 'Invalid email or password';
      try {
        const error = await response.json();
        errorMessage = error.detail || error.message || errorMessage;
      } catch (e) {
        // If response is not JSON, use status text
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error: any) {
    console.error('Admin login error:', error);
    // Handle network errors
    if (error.message === 'Failed to fetch' || error.name === 'TypeError') {
      throw new Error('Unable to connect to admin service. Please check if the service is running.');
    }
    throw error;
  }
}

