import axios, { AxiosInstance, AxiosError } from 'axios';
import { useAuthStore } from '../store/authStore';

// API base URLs (aligned with Team 5's architecture)
const USER_SERVICE_URL = process.env.REACT_APP_USER_SERVICE_URL || 'http://localhost:8001';
const ADMIN_SERVICE_URL = process.env.REACT_APP_ADMIN_SERVICE_URL || 'http://localhost:8006';
const AI_SERVICE_URL = process.env.REACT_APP_AI_SERVICE_URL || 'http://localhost:8008';
const FLIGHT_SERVICE_URL = process.env.REACT_APP_FLIGHT_SERVICE_URL || 'http://localhost:8002';
const HOTEL_SERVICE_URL = process.env.REACT_APP_HOTEL_SERVICE_URL || 'http://localhost:8003';
const CAR_SERVICE_URL = process.env.REACT_APP_CAR_SERVICE_URL || 'http://localhost:8004';
const SEARCH_SERVICE_URL = process.env.REACT_APP_SEARCH_SERVICE_URL || 'http://localhost:8007';

// Create axios instances
const createApiInstance = (baseURL: string): AxiosInstance => {
  const instance = axios.create({
    baseURL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor to add auth token
  instance.interceptors.request.use((config) => {
    const { userToken, adminToken } = useAuthStore.getState();
    const token = baseURL.includes('8002') ? adminToken : userToken;
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  // Response interceptor for error handling
  instance.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      if (error.response?.status === 401) {
        // Handle unauthorized - logout
        const { logoutUser, logoutAdmin } = useAuthStore.getState();
        logoutUser();
        logoutAdmin();
      }
      return Promise.reject(error);
    }
  );

  return instance;
};

export const userApi = createApiInstance(USER_SERVICE_URL);
export const adminApi = createApiInstance(ADMIN_SERVICE_URL);
export const aiApi = createApiInstance(AI_SERVICE_URL);
export const flightApi = createApiInstance(FLIGHT_SERVICE_URL);
export const hotelApi = createApiInstance(HOTEL_SERVICE_URL);
export const carApi = createApiInstance(CAR_SERVICE_URL);

// User Service API
export const userService = {
  // Auth
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    const response = await userApi.post('/users/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  register: async (userData: any) => {
    const response = await userApi.post('/users', userData);
    return response.data;
  },

  // Profile
  getProfile: async () => {
    const response = await userApi.get('/users/me');
    return response.data;
  },

  updateProfile: async (data: any) => {
    const response = await userApi.put('/users/me', data);
    return response.data;
  },

  uploadProfileImage: async (userId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await userApi.post(`/users/${userId}/profile-image`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  changePassword: async (currentPassword: string, newPassword: string) => {
    const response = await userApi.post('/users/me/change-password', null, {
      params: { current_password: currentPassword, new_password: newPassword },
    });
    return response.data;
  },

  // Users list (for admins)
  getUsers: async (params: any = {}) => {
    const response = await userApi.get('/users', { params });
    return response.data;
  },

  getUserById: async (userId: string) => {
    const response = await userApi.get(`/users/${userId}`);
    return response.data;
  },

  deleteUser: async (userId: string) => {
    const response = await userApi.delete(`/users/${userId}`);
    return response.data;
  },
};

// Admin Service API
export const adminService = {
  // Auth
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    const response = await adminApi.post('/admin/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getProfile: async () => {
    const response = await adminApi.get('/admin/me');
    return response.data;
  },

  // User Management
  getUsers: async (params: any = {}) => {
    const response = await adminApi.get('/admin/users', { params });
    return response.data;
  },

  updateUser: async (userId: string, data: any) => {
    const response = await adminApi.put(`/admin/users/${userId}`, data);
    return response.data;
  },

  deleteUser: async (userId: string) => {
    const response = await adminApi.delete(`/admin/users/${userId}`);
    return response.data;
  },

  // Listing Management
  getListings: async (params: any = {}) => {
    const response = await adminApi.get('/admin/listings', { params });
    return response.data;
  },

  createListing: async (data: any) => {
    const response = await adminApi.post('/admin/listings', data);
    return response.data;
  },

  updateListing: async (listingId: string, data: any) => {
    const response = await adminApi.put(`/admin/listings/${listingId}`, data);
    return response.data;
  },

  // Reports
  getTopProperties: async (year?: number) => {
    const response = await adminApi.get('/admin/reports/top-properties', {
      params: year ? { year } : {},
    });
    return response.data;
  },

  getCityRevenue: async (year?: number) => {
    const response = await adminApi.get('/admin/reports/city-revenue', {
      params: year ? { year } : {},
    });
    return response.data;
  },

  getProviderAnalysis: async (month?: number, year?: number) => {
    const response = await adminApi.get('/admin/reports/provider-analysis', {
      params: { month, year },
    });
    return response.data;
  },

  getDashboardStats: async () => {
    const response = await adminApi.get('/admin/dashboard/stats');
    return response.data;
  },

  getActivityLog: async (params: any = {}) => {
    const response = await adminApi.get('/admin/activity-log', { params });
    return response.data;
  },
};

// AI Service API
export const aiService = {
  getDeals: async () => {
    const response = await aiApi.get('/deals');
    return response.data;
  },

  getBundles: async (preferences: any) => {
    const response = await aiApi.post('/bundles', preferences);
    return response.data;
  },

  chat: async (message: string) => {
    const response = await aiApi.post('/chat', { message });
    return response.data;
  },

  setWatch: async (watchData: any) => {
    const response = await aiApi.post('/watches', watchData);
    return response.data;
  },
};

// ==================== Team 2 Listing Services ====================

// Flight Service API (Team 2 - Port 8002)
export const flightService = {
  search: async (params: {
    origin?: string;
    destination?: string;
    departure_date?: string;
    min_price?: number;
    max_price?: number;
    flight_class?: 'Economy' | 'Business' | 'First';
    departure_time_start?: string;
    departure_time_end?: string;
    page?: number;
    page_size?: number;
  }) => {
    const response = await flightApi.get('/flights/search', { params });
    return response.data;
  },

  getById: async (flightId: string) => {
    const response = await flightApi.get(`/flights/${flightId}`);
    return response.data;
  },

  // Admin operations
  create: async (data: any) => {
    const response = await flightApi.post('/flights', data);
    return response.data;
  },

  update: async (flightId: string, data: any) => {
    const response = await flightApi.put(`/flights/${flightId}`, data);
    return response.data;
  },

  delete: async (flightId: string) => {
    const response = await flightApi.delete(`/flights/${flightId}`);
    return response.data;
  },
};

// Hotel Service API (Team 2 - Port 8003)
export const hotelService = {
  search: async (params: {
    location?: string;
    city?: string;
    state?: string;
    check_in_date?: string;
    check_out_date?: string;
    min_price?: number;
    max_price?: number;
    min_stars?: number;
    max_stars?: number;
    amenities?: string;
    page?: number;
    page_size?: number;
  }) => {
    const response = await hotelApi.get('/hotels/search', { params });
    return response.data;
  },

  getById: async (hotelId: string) => {
    const response = await hotelApi.get(`/hotels/${hotelId}`);
    return response.data;
  },

  getImages: async (hotelId: string, imageType: 'hotel' | 'room' = 'hotel') => {
    const response = await hotelApi.get(`/hotels/${hotelId}/images`, {
      params: { image_type: imageType },
    });
    return response.data;
  },

  // Admin operations
  create: async (data: any) => {
    const response = await hotelApi.post('/hotels', data);
    return response.data;
  },

  update: async (hotelId: string, data: any) => {
    const response = await hotelApi.put(`/hotels/${hotelId}`, data);
    return response.data;
  },

  delete: async (hotelId: string) => {
    const response = await hotelApi.delete(`/hotels/${hotelId}`);
    return response.data;
  },

  uploadImage: async (hotelId: string, file: File, imageType: 'hotel' | 'room') => {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('image_type', imageType);
    const response = await hotelApi.post(`/hotels/${hotelId}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};

// Car Service API (Team 2 - Port 8004)
export const carService = {
  search: async (params: {
    location?: string;
    city?: string;
    state?: string;
    car_type?: string;
    min_price?: number;
    max_price?: number;
    transmission_type?: 'Automatic' | 'Manual';
    min_seats?: number;
    max_seats?: number;
    page?: number;
    page_size?: number;
  }) => {
    const response = await carApi.get('/cars/search', { params });
    return response.data;
  },

  getById: async (carId: string) => {
    const response = await carApi.get(`/cars/${carId}`);
    return response.data;
  },

  getImages: async (carId: string) => {
    const response = await carApi.get(`/cars/${carId}/images`);
    return response.data;
  },

  // Admin operations
  create: async (data: any) => {
    const response = await carApi.post('/cars', data);
    return response.data;
  },

  update: async (carId: string, data: any) => {
    const response = await carApi.put(`/cars/${carId}`, data);
    return response.data;
  },

  delete: async (carId: string) => {
    const response = await carApi.delete(`/cars/${carId}`);
    return response.data;
  },

  uploadImage: async (carId: string, file: File) => {
    const formData = new FormData();
    formData.append('image', file);
    const response = await carApi.post(`/cars/${carId}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};


