import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  user_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  profile_image_url?: string;
  is_active: boolean;
  is_verified: boolean;
}

interface Admin {
  admin_id: string;
  first_name: string;
  last_name: string;
  email: string;
  role: string;
  access_level: number;
  permissions: {
    can_manage_users: boolean;
    can_manage_listings: boolean;
    can_view_billing: boolean;
    can_view_analytics: boolean;
    can_manage_admins: boolean;
  };
}

interface AuthState {
  // User auth
  user: User | null;
  userToken: string | null;
  isAuthenticated: boolean;
  
  // Admin auth
  admin: Admin | null;
  adminToken: string | null;
  isAdmin: boolean;
  
  // Actions
  loginUser: (user: User, token: string) => void;
  logoutUser: () => void;
  updateUser: (user: Partial<User>) => void;
  
  loginAdmin: (admin: Admin, token: string) => void;
  logoutAdmin: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      // Initial state
      user: null,
      userToken: null,
      isAuthenticated: false,
      admin: null,
      adminToken: null,
      isAdmin: false,

      // User actions
      loginUser: (user, token) =>
        set({
          user,
          userToken: token,
          isAuthenticated: true,
        }),

      logoutUser: () =>
        set({
          user: null,
          userToken: null,
          isAuthenticated: false,
        }),

      updateUser: (updates) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...updates } : null,
        })),

      // Admin actions
      loginAdmin: (admin, token) =>
        set({
          admin,
          adminToken: token,
          isAdmin: true,
        }),

      logoutAdmin: () =>
        set({
          admin: null,
          adminToken: null,
          isAdmin: false,
        }),
    }),
    {
      name: 'kayak-auth',
      partialize: (state) => ({
        user: state.user,
        userToken: state.userToken,
        isAuthenticated: state.isAuthenticated,
        admin: state.admin,
        adminToken: state.adminToken,
        isAdmin: state.isAdmin,
      }),
    }
  )
);


