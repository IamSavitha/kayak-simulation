import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Users, Plane, Hotel, Car, DollarSign, BarChart3, Settings, Calendar } from 'lucide-react';
import { getDashboardStats, getAllBookings, DashboardStats, AdminBooking } from '../api/adminBookings';

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [admin, setAdmin] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [bookings, setBookings] = useState<AdminBooking[]>([]);
  const [bookingsLoading, setBookingsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const refreshIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadDashboardStats = useCallback(async () => {
    const adminToken = localStorage.getItem('admin_token');
    if (!adminToken) return;
    
    try {
      const statsData = await getDashboardStats(adminToken);
      setStats(statsData);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error loading dashboard stats:', error);
    }
  }, []);

  const loadBookings = useCallback(async () => {
    const adminToken = localStorage.getItem('admin_token');
    if (!adminToken) return;
    
    setBookingsLoading(true);
    try {
      const bookingsData = await getAllBookings(adminToken, 1, 10);
      setBookings(bookingsData.bookings);
    } catch (error) {
      console.error('Error loading bookings:', error);
    } finally {
      setBookingsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Check if admin is logged in
    const adminToken = localStorage.getItem('admin_token');
    const adminData = localStorage.getItem('admin');
    const isAdmin = localStorage.getItem('is_admin');

    if (!adminToken || !adminData || isAdmin !== 'true') {
      // Clear any regular user session if present
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // Redirect to admin login if not authenticated as admin
      navigate('/admin/login');
      return;
    }

    try {
      setAdmin(JSON.parse(adminData));
      // Load dashboard stats
      loadDashboardStats();
      // Load recent bookings
      loadBookings();
    } catch (error) {
      console.error('Error parsing admin data:', error);
      navigate('/admin/login');
      return;
    } finally {
      setLoading(false);
    }

    // Set up auto-refresh every 5 seconds for real-time updates
    refreshIntervalRef.current = setInterval(() => {
      loadDashboardStats();
      loadBookings();
    }, 5000);

    // Cleanup interval on unmount
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
        refreshIntervalRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run once on mount - navigate is stable, functions are memoized

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin');
    localStorage.removeItem('is_admin');
    navigate('/admin/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-white to-slate-100/30">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-600 mx-auto"></div>
          <p className="mt-4 text-slate-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!admin) {
    return null; // Will redirect
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-slate-900 flex items-center">
                <Shield className="mr-3 text-slate-600" size={36} />
                Admin Dashboard
              </h1>
              <p className="mt-2 text-slate-600">
                Welcome back, {admin.first_name} {admin.last_name} ({admin.role})
              </p>
              <p className="text-xs text-slate-500 mt-1">
                🔄 Auto-refreshing every 5 seconds • Last updated: {lastUpdated.toLocaleTimeString()}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-md"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Total Users</p>
                <p className="text-3xl font-bold text-slate-900">
                  {stats ? stats.total_users.toLocaleString() : '-'}
                </p>
              </div>
              <Users className="text-blue-600" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Total Revenue</p>
                <p className="text-3xl font-bold text-slate-900">
                  {stats ? `$${stats.total_revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '-'}
                </p>
              </div>
              <DollarSign className="text-green-600" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Total Bookings</p>
                <p className="text-3xl font-bold text-slate-900">
                  {stats ? stats.total_bookings.toLocaleString() : '-'}
                </p>
              </div>
              <BarChart3 className="text-slate-600" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Active Listings</p>
                <p className="text-3xl font-bold text-slate-900">
                  {stats ? stats.active_listings.toLocaleString() : '-'}
                </p>
              </div>
              <Settings className="text-orange-600" size={32} />
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-slate-200">
            <div className="flex items-center mb-4">
              <BarChart3 className="text-purple-600 mr-3" size={24} />
              <h3 className="text-xl font-bold text-slate-900">Analytics</h3>
            </div>
            <p className="text-slate-600 mb-4">Revenue reports and charts</p>
            <button 
              onClick={() => navigate('/admin/analytics')}
              className="w-full px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg hover:from-purple-700 hover:to-purple-800 transition-all shadow-md"
            >
              View Analytics
            </button>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-slate-200">
            <div className="flex items-center mb-4">
              <Plane className="text-blue-600 mr-3" size={24} />
              <h3 className="text-xl font-bold text-slate-900">Manage Flights</h3>
            </div>
            <p className="text-slate-600 mb-4">View and manage flight listings</p>
            <button 
              onClick={() => navigate('/admin/flights')}
              className="w-full px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-md"
            >
              Manage Flights
            </button>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-slate-200">
            <div className="flex items-center mb-4">
              <Hotel className="text-green-600 mr-3" size={24} />
              <h3 className="text-xl font-bold text-slate-900">Manage Hotels</h3>
            </div>
            <p className="text-slate-600 mb-4">View and manage hotel listings</p>
            <button
              onClick={() => navigate('/admin/hotels')}
              className="w-full px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-md"
            >
              Manage Hotels
            </button>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-slate-200">
            <div className="flex items-center mb-4">
              <Car className="text-orange-600 mr-3" size={24} />
              <h3 className="text-xl font-bold text-slate-900">Manage Cars</h3>
            </div>
            <p className="text-slate-600 mb-4">View and manage car listings</p>
            <button
              onClick={() => navigate('/admin/cars')}
              className="w-full px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-md"
            >
              Manage Cars
            </button>
          </div>
        </div>

        {/* Recent Bookings */}
        <div className="mt-8 bg-white rounded-xl shadow-lg p-6 border-2 border-slate-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-slate-900 flex items-center">
              <Calendar className="mr-2" size={24} />
              Recent Bookings
            </h2>
            <button
              onClick={() => navigate('/admin/bookings')}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              View All →
            </button>
          </div>
          
          {bookingsLoading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-slate-600"></div>
              <p className="mt-2 text-slate-600">Loading bookings...</p>
            </div>
          ) : bookings.length === 0 ? (
            <div className="text-center py-8 text-slate-600">
              <Calendar className="w-12 h-12 mx-auto mb-2 text-slate-400" />
              <p>No bookings found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Booking ID</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Type</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">User ID</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Status</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-slate-700">Amount</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {bookings.map((booking) => (
                    <tr key={booking.booking_id} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="py-3 px-4 text-sm text-slate-900 font-mono">{booking.booking_id}</td>
                      <td className="py-3 px-4 text-sm text-slate-700 capitalize">{booking.booking_type}</td>
                      <td className="py-3 px-4 text-sm text-slate-700 font-mono">{booking.user_id}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          booking.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                          booking.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                          booking.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {booking.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm text-slate-900 font-semibold text-right">
                        ${booking.total_price.toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-sm text-slate-600">
                        {new Date(booking.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Admin Info */}
        <div className="mt-8 bg-white rounded-xl shadow-lg p-6 border-2 border-slate-200">
          <h2 className="text-2xl font-bold text-slate-900 mb-4">Admin Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-slate-600">Admin ID</p>
              <p className="font-semibold text-slate-900">{admin.admin_id}</p>
            </div>
            <div>
              <p className="text-sm text-slate-600">Email</p>
              <p className="font-semibold text-slate-900">{admin.email}</p>
            </div>
            <div>
              <p className="text-sm text-slate-600">Role</p>
              <p className="font-semibold text-slate-900 capitalize">{admin.role}</p>
            </div>
            <div>
              <p className="text-sm text-slate-600">Status</p>
              <p className="font-semibold text-slate-900">
                {admin.is_active ? (
                  <span className="text-green-600">Active</span>
                ) : (
                  <span className="text-red-600">Inactive</span>
                )}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;

