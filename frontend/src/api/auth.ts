/**
 * Authentication API functions
 */

// Always use proxy URLs - Vite dev server will route them correctly
const API_BASE_URL = '/api/users';

export interface SignupData {
  user_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  password: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    user_id: string;
    first_name: string;
    last_name: string;
    email: string;
    phone_number?: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
  };
}

/**
 * Register a new user with optional profile image upload
 */
export async function signup(data: SignupData, imageFile?: File): Promise<any> {
  try {
    const formData = new FormData();
    formData.append('user_data', JSON.stringify(data));
    if (imageFile) {
      formData.append('image', imageFile);
    }

    const response = await fetch(`${API_BASE_URL}`, {
      method: 'POST',
      // Don't set Content-Type header - browser will set it with boundary for FormData
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      // Handle nested error detail structure
      const errorMessage = error.detail?.message || error.detail || error.message || 'Failed to create account';
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error('Signup error:', error);
    throw error;
  }
}

/**
 * Login user
 */
export async function login(data: LoginData): Promise<TokenResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      // Handle nested error detail structure
      const errorMessage = error.detail?.message || error.detail || error.message || 'Invalid email or password';
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

/**
 * Get current user info
 */
export async function getCurrentUser(token: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to get user info');
    }

    return await response.json();
  } catch (error) {
    console.error('Get current user error:', error);
    throw error;
  }
}

export interface UserProfile {
  user_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone_number?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  profile_image_url?: string;
  credit_card_last_four?: string;
  credit_card_type?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UpdateProfileData {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone_number?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  profile_image_url?: string;
}

/**
 * Get user profile by ID
 */
export async function getUserProfile(userId: string, token: string): Promise<UserProfile> {
  try {
    const response = await fetch(`${API_BASE_URL}/${userId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail?.message || error.detail || 'Failed to get user profile');
    }

    return await response.json();
  } catch (error) {
    console.error('Get user profile error:', error);
    throw error;
  }
}

/**
 * Update user profile with optional image upload
 */
export async function updateUserProfile(
  userId: string,
  data: UpdateProfileData,
  token: string,
  imageFile?: File
): Promise<UserProfile> {
  try {
    let response: Response;
    
    if (imageFile) {
      // Use FormData for image upload
      const formData = new FormData();
      formData.append('user_data', JSON.stringify(data));
      formData.append('image', imageFile);
      
      response = await fetch(`${API_BASE_URL}/${userId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          // Don't set Content-Type - browser will set it with boundary for FormData
        },
        body: formData,
      });
    } else {
      // Use JSON for regular updates
      response = await fetch(`${API_BASE_URL}/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });
    }

    if (!response.ok) {
      const error = await response.json();
      const errorMessage = error.detail?.message || error.detail || error.message || 'Failed to update profile';
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error('Update user profile error:', error);
    throw error;
  }
}
