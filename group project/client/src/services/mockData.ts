/**
 * Mock Data for Team 3 (Booking) and Team 4 (Billing) Services
 * 
 * Use these mocks until integration with actual services is complete.
 * Replace with real API calls when Team 3/4 provide their endpoints.
 */

// Types
export interface Booking {
  booking_id: string;
  user_id: string;
  booking_type: 'flight' | 'hotel' | 'car';
  listing_id: string;
  listing_name: string;
  provider: string;
  check_in_date: string;
  check_out_date: string | null;
  num_passengers: number | null;
  num_rooms: number | null;
  num_nights: number | null;
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed';
  total_price: number;
  booking_date: string;
  created_at: string;
  updated_at: string;
}

export interface Billing {
  billing_id: string;
  user_id: string;
  booking_id: string;
  booking_type: 'flight' | 'hotel' | 'car';
  transaction_date: string;
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  payment_method: 'credit_card' | 'debit_card' | 'paypal' | 'bank_transfer';
  payment_status: 'pending' | 'completed' | 'failed' | 'refunded';
  card_last_four: string | null;
  invoice_number: string;
  created_at: string;
  updated_at: string;
}

export interface Review {
  review_id: string;
  user_id: string;
  booking_id: string;
  listing_id: string;
  listing_type: 'flight' | 'hotel' | 'car';
  rating: number;
  title: string;
  content: string;
  created_at: string;
}

// Helper to generate dates
const now = new Date();
const addDays = (days: number) => new Date(now.getTime() + days * 24 * 60 * 60 * 1000).toISOString();
const subDays = (days: number) => new Date(now.getTime() - days * 24 * 60 * 60 * 1000).toISOString();

// Mock Bookings Data
export const MOCK_BOOKINGS: Booking[] = [
  {
    booking_id: 'BK-001',
    user_id: '123-45-6789',
    booking_type: 'flight',
    listing_id: 'FLT-ABC123',
    listing_name: 'San Francisco → New York',
    provider: 'United Airlines',
    check_in_date: addDays(30),
    check_out_date: null,
    num_passengers: 2,
    num_rooms: null,
    num_nights: null,
    status: 'confirmed',
    total_price: 598.00,
    booking_date: now.toISOString(),
    created_at: now.toISOString(),
    updated_at: now.toISOString(),
  },
  {
    booking_id: 'BK-002',
    user_id: '123-45-6789',
    booking_type: 'hotel',
    listing_id: 'HTL-XYZ789',
    listing_name: 'Marriott Times Square',
    provider: 'Marriott International',
    check_in_date: addDays(30),
    check_out_date: addDays(33),
    num_passengers: null,
    num_rooms: 1,
    num_nights: 3,
    status: 'confirmed',
    total_price: 567.00,
    booking_date: now.toISOString(),
    created_at: now.toISOString(),
    updated_at: now.toISOString(),
  },
  {
    booking_id: 'BK-003',
    user_id: '123-45-6789',
    booking_type: 'car',
    listing_id: 'CAR-DEF456',
    listing_name: 'Toyota RAV4 2023',
    provider: 'Hertz',
    check_in_date: addDays(15),
    check_out_date: addDays(18),
    num_passengers: null,
    num_rooms: null,
    num_nights: null,
    status: 'pending',
    total_price: 267.00,
    booking_date: now.toISOString(),
    created_at: now.toISOString(),
    updated_at: now.toISOString(),
  },
  {
    booking_id: 'BK-004',
    user_id: '123-45-6789',
    booking_type: 'flight',
    listing_id: 'FLT-GHI321',
    listing_name: 'Los Angeles → Miami',
    provider: 'Delta Airlines',
    check_in_date: subDays(10),
    check_out_date: null,
    num_passengers: 1,
    num_rooms: null,
    num_nights: null,
    status: 'completed',
    total_price: 349.00,
    booking_date: subDays(30),
    created_at: subDays(30),
    updated_at: subDays(10),
  },
  {
    booking_id: 'BK-005',
    user_id: '123-45-6789',
    booking_type: 'hotel',
    listing_id: 'HTL-JKL654',
    listing_name: 'Hilton Downtown LA',
    provider: 'Hilton Hotels',
    check_in_date: subDays(5),
    check_out_date: subDays(2),
    num_passengers: null,
    num_rooms: 2,
    num_nights: 3,
    status: 'completed',
    total_price: 687.00,
    booking_date: subDays(20),
    created_at: subDays(20),
    updated_at: subDays(2),
  },
  {
    booking_id: 'BK-006',
    user_id: '234-56-7890',
    booking_type: 'flight',
    listing_id: 'FLT-MNO987',
    listing_name: 'Chicago → Seattle',
    provider: 'American Airlines',
    check_in_date: addDays(45),
    check_out_date: null,
    num_passengers: 3,
    num_rooms: null,
    num_nights: null,
    status: 'confirmed',
    total_price: 897.00,
    booking_date: subDays(2),
    created_at: subDays(2),
    updated_at: subDays(2),
  },
  {
    booking_id: 'BK-007',
    user_id: '345-67-8901',
    booking_type: 'car',
    listing_id: 'CAR-PQR654',
    listing_name: 'BMW 5 Series 2024',
    provider: 'Enterprise',
    check_in_date: subDays(15),
    check_out_date: subDays(10),
    num_passengers: null,
    num_rooms: null,
    num_nights: null,
    status: 'completed',
    total_price: 750.00,
    booking_date: subDays(25),
    created_at: subDays(25),
    updated_at: subDays(10),
  },
];

// Mock Billings Data
export const MOCK_BILLINGS: Billing[] = [
  {
    billing_id: 'BIL-001',
    user_id: '123-45-6789',
    booking_id: 'BK-001',
    booking_type: 'flight',
    transaction_date: now.toISOString(),
    subtotal: 550.00,
    tax_amount: 48.00,
    total_amount: 598.00,
    payment_method: 'credit_card',
    payment_status: 'completed',
    card_last_four: '4242',
    invoice_number: 'INV-2025-001',
    created_at: now.toISOString(),
    updated_at: now.toISOString(),
  },
  {
    billing_id: 'BIL-002',
    user_id: '123-45-6789',
    booking_id: 'BK-002',
    booking_type: 'hotel',
    transaction_date: now.toISOString(),
    subtotal: 520.00,
    tax_amount: 47.00,
    total_amount: 567.00,
    payment_method: 'credit_card',
    payment_status: 'completed',
    card_last_four: '4242',
    invoice_number: 'INV-2025-002',
    created_at: now.toISOString(),
    updated_at: now.toISOString(),
  },
  {
    billing_id: 'BIL-003',
    user_id: '123-45-6789',
    booking_id: 'BK-003',
    booking_type: 'car',
    transaction_date: now.toISOString(),
    subtotal: 245.00,
    tax_amount: 22.00,
    total_amount: 267.00,
    payment_method: 'paypal',
    payment_status: 'pending',
    card_last_four: null,
    invoice_number: 'INV-2025-003',
    created_at: now.toISOString(),
    updated_at: now.toISOString(),
  },
  {
    billing_id: 'BIL-004',
    user_id: '123-45-6789',
    booking_id: 'BK-004',
    booking_type: 'flight',
    transaction_date: subDays(30),
    subtotal: 320.00,
    tax_amount: 29.00,
    total_amount: 349.00,
    payment_method: 'debit_card',
    payment_status: 'completed',
    card_last_four: '1234',
    invoice_number: 'INV-2024-104',
    created_at: subDays(30),
    updated_at: subDays(30),
  },
  {
    billing_id: 'BIL-005',
    user_id: '123-45-6789',
    booking_id: 'BK-005',
    booking_type: 'hotel',
    transaction_date: subDays(20),
    subtotal: 630.00,
    tax_amount: 57.00,
    total_amount: 687.00,
    payment_method: 'credit_card',
    payment_status: 'completed',
    card_last_four: '5678',
    invoice_number: 'INV-2024-105',
    created_at: subDays(20),
    updated_at: subDays(20),
  },
];

// Mock Reviews Data
export const MOCK_REVIEWS: Review[] = [
  {
    review_id: 'REV-001',
    user_id: '123-45-6789',
    booking_id: 'BK-004',
    listing_id: 'FLT-GHI321',
    listing_type: 'flight',
    rating: 4.5,
    title: 'Great flight experience',
    content: 'Smooth flight, friendly crew, and on-time arrival. Would recommend!',
    created_at: subDays(8),
  },
  {
    review_id: 'REV-002',
    user_id: '123-45-6789',
    booking_id: 'BK-005',
    listing_id: 'HTL-JKL654',
    listing_type: 'hotel',
    rating: 4.0,
    title: 'Nice stay, good location',
    content: 'Great hotel in a prime location. Rooms were clean and staff was helpful.',
    created_at: subDays(1),
  },
];

// Mock Service Functions
export const mockBookingService = {
  getUserBookings: (userId: string): Promise<Booking[]> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(MOCK_BOOKINGS.filter(b => b.user_id === userId));
      }, 500);
    });
  },

  getUpcomingBookings: (userId: string): Promise<Booking[]> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const now = new Date();
        resolve(
          MOCK_BOOKINGS.filter(
            b => b.user_id === userId && 
            ['pending', 'confirmed'].includes(b.status) &&
            new Date(b.check_in_date) > now
          )
        );
      }, 500);
    });
  },

  getPastBookings: (userId: string): Promise<Booking[]> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(
          MOCK_BOOKINGS.filter(
            b => b.user_id === userId && 
            ['completed', 'cancelled'].includes(b.status)
          )
        );
      }, 500);
    });
  },

  getAllBookings: (params?: {
    page?: number;
    page_size?: number;
    status?: string;
    booking_type?: string;
  }): Promise<{ bookings: Booking[]; total: number; page: number; page_size: number; total_pages: number }> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        let filtered = [...MOCK_BOOKINGS];
        
        if (params?.status) {
          filtered = filtered.filter(b => b.status === params.status);
        }
        if (params?.booking_type) {
          filtered = filtered.filter(b => b.booking_type === params.booking_type);
        }
        
        const page = params?.page || 1;
        const pageSize = params?.page_size || 20;
        const total = filtered.length;
        const start = (page - 1) * pageSize;
        
        resolve({
          bookings: filtered.slice(start, start + pageSize),
          total,
          page,
          page_size: pageSize,
          total_pages: Math.ceil(total / pageSize),
        });
      }, 500);
    });
  },

  cancelBooking: (bookingId: string): Promise<Booking | null> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const booking = MOCK_BOOKINGS.find(b => b.booking_id === bookingId);
        if (booking) {
          booking.status = 'cancelled';
          booking.updated_at = new Date().toISOString();
          resolve(booking);
        } else {
          resolve(null);
        }
      }, 500);
    });
  },
};

export const mockBillingService = {
  getUserBills: (userId: string): Promise<Billing[]> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(MOCK_BILLINGS.filter(b => b.user_id === userId));
      }, 500);
    });
  },

  getBillByBooking: (bookingId: string): Promise<Billing | null> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(MOCK_BILLINGS.find(b => b.booking_id === bookingId) || null);
      }, 500);
    });
  },

  searchBills: (params?: {
    page?: number;
    page_size?: number;
    start_date?: string;
    end_date?: string;
    payment_status?: string;
    booking_type?: string;
  }): Promise<{ billings: Billing[]; total: number; page: number; page_size: number; total_pages: number }> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        let filtered = [...MOCK_BILLINGS];
        
        if (params?.start_date) {
          filtered = filtered.filter(b => new Date(b.transaction_date) >= new Date(params.start_date!));
        }
        if (params?.end_date) {
          filtered = filtered.filter(b => new Date(b.transaction_date) <= new Date(params.end_date!));
        }
        if (params?.payment_status) {
          filtered = filtered.filter(b => b.payment_status === params.payment_status);
        }
        if (params?.booking_type) {
          filtered = filtered.filter(b => b.booking_type === params.booking_type);
        }
        
        const page = params?.page || 1;
        const pageSize = params?.page_size || 20;
        const total = filtered.length;
        const start = (page - 1) * pageSize;
        
        resolve({
          billings: filtered.slice(start, start + pageSize),
          total,
          page,
          page_size: pageSize,
          total_pages: Math.ceil(total / pageSize),
        });
      }, 500);
    });
  },

  getRevenueByMonth: (year: number): Promise<any[]> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const months = [];
        for (let month = 1; month <= 12; month++) {
          months.push({
            month,
            year,
            total_revenue: Math.random() * 100000 + 50000,
            flight_revenue: Math.random() * 40000 + 20000,
            hotel_revenue: Math.random() * 40000 + 20000,
            car_revenue: Math.random() * 20000 + 10000,
            transaction_count: Math.floor(Math.random() * 400) + 100,
          });
        }
        resolve(months);
      }, 500);
    });
  },

  getRevenueByCity: (year: number): Promise<any[]> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const cities = [
          { city: 'New York', state: 'NY' },
          { city: 'Los Angeles', state: 'CA' },
          { city: 'San Francisco', state: 'CA' },
          { city: 'Miami', state: 'FL' },
          { city: 'Chicago', state: 'IL' },
          { city: 'Seattle', state: 'WA' },
          { city: 'Boston', state: 'MA' },
          { city: 'Denver', state: 'CO' },
          { city: 'Austin', state: 'TX' },
          { city: 'Las Vegas', state: 'NV' },
        ];
        
        resolve(
          cities.map(c => ({
            ...c,
            year,
            total_revenue: Math.random() * 400000 + 100000,
            booking_count: Math.floor(Math.random() * 1500) + 500,
          }))
        );
      }, 500);
    });
  },
};

// Dashboard Stats
export const getDashboardStats = () => {
  const totalBookings = MOCK_BOOKINGS.length;
  const pendingBookings = MOCK_BOOKINGS.filter(b => b.status === 'pending').length;
  const confirmedBookings = MOCK_BOOKINGS.filter(b => b.status === 'confirmed').length;
  const completedBookings = MOCK_BOOKINGS.filter(b => b.status === 'completed').length;
  
  const totalRevenue = MOCK_BILLINGS
    .filter(b => b.payment_status === 'completed')
    .reduce((sum, b) => sum + b.total_amount, 0);
  
  const pendingPayments = MOCK_BILLINGS
    .filter(b => b.payment_status === 'pending')
    .reduce((sum, b) => sum + b.total_amount, 0);
  
  return {
    totalBookings,
    pendingBookings,
    confirmedBookings,
    completedBookings,
    totalRevenue,
    pendingPayments,
    averageBookingValue: totalRevenue / completedBookings || 0,
    conversionRate: (confirmedBookings + completedBookings) / totalBookings * 100,
  };
};

