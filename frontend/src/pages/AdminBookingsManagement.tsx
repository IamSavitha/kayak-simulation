import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, Search, CheckCircle, Clock, XCircle, DollarSign, Edit, Trash2, AlertCircle } from 'lucide-react';
import { getAllBookings, updateBookingStatus, adminCancelBooking, AdminBooking } from '../api/adminBookings';
import { getBillingByBookingId, approveRefund, rejectRefund } from '../api/adminBookings';

const AdminBookingsManagement: React.FC = () => {
  const navigate = useNavigate();
  const [bookings, setBookings] = useState<AdminBooking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [total, setTotal] = useState(0);
  const [filterType, setFilterType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [selectedBooking, setSelectedBooking] = useState<AdminBooking | null>(null);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [showRefundModal, setShowRefundModal] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const [cancelReason, setCancelReason] = useState('');
  const [billingInfo, setBillingInfo] = useState<any>(null);
  const [refundReason, setRefundReason] = useState('');

  useEffect(() => {
    const adminToken = localStorage.getItem('admin_token');
    const isAdmin = localStorage.getItem('is_admin');

    if (!adminToken || isAdmin !== 'true') {
      navigate('/admin/login');
      return;
    }

    loadBookings();

    // Set up auto-refresh every 10 seconds for real-time updates
    const refreshInterval = setInterval(() => {
      loadBookings();
    }, 10000);

    // Cleanup interval on unmount
    return () => clearInterval(refreshInterval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, filterType, filterStatus]); // navigate is stable, don't include it

  const loadBookings = async () => {
    const adminToken = localStorage.getItem('admin_token');
    if (!adminToken) return;

    setLoading(true);
    setError(null);
    try {
      const data = await getAllBookings(
        adminToken,
        page,
        pageSize,
        filterType !== 'all' ? filterType : undefined,
        filterStatus !== 'all' ? filterStatus : undefined
      );
      setBookings(data.bookings);
      setTotal(data.total);
    } catch (err: any) {
      console.error('Error loading bookings:', err);
      setError(err.message || 'Failed to load bookings');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async () => {
    if (!selectedBooking || !newStatus) return;

    const adminToken = localStorage.getItem('admin_token');
    if (!adminToken) return;

    try {
      await updateBookingStatus(selectedBooking.booking_id, newStatus, adminToken);
      setShowStatusModal(false);
      setSelectedBooking(null);
      setNewStatus('');
      loadBookings();
      alert('Booking status updated successfully');
    } catch (err: any) {
      alert(err.message || 'Failed to update booking status');
    }
  };

  const handleCancelBooking = async () => {
    if (!selectedBooking || !cancelReason.trim()) {
      alert('Please provide a reason for cancellation');
      return;
    }

    const adminToken = localStorage.getItem('admin_token');
    if (!adminToken) return;

    try {
      await adminCancelBooking(
        selectedBooking.booking_id,
        cancelReason,
        false, // refund_requested is now automatic - always set to pending if payment completed
        adminToken
      );
      setShowCancelModal(false);
      setSelectedBooking(null);
      setCancelReason('');
      loadBookings();
      alert('Booking cancelled successfully. If payment was completed, refund is now pending approval.');
    } catch (err: any) {
      alert(err.message || 'Failed to cancel booking');
    }
  };

  const handleViewRefund = async (booking: AdminBooking) => {
    const adminToken = localStorage.getItem('admin_token');
    if (!adminToken) {
      alert('Admin token not found. Please log in again.');
      return;
    }

    try {
      console.log('Fetching billing for booking:', booking.booking_id);
      const billing = await getBillingByBookingId(booking.booking_id, adminToken);
      console.log('Billing data:', billing);
      
      if (!billing) {
        alert(`No billing record found for booking ${booking.booking_id}. This booking may not have been paid yet.`);
        return;
      }
      
      // Normalize total_amount to number if it's a string
      if (billing.total_amount && typeof billing.total_amount === 'string') {
        billing.total_amount = parseFloat(billing.total_amount);
      }
      
      setBillingInfo(billing);
      setSelectedBooking(booking);
      setShowRefundModal(true);
    } catch (err: any) {
      console.error('Error loading billing:', err);
      alert(err.message || 'Failed to load billing information. Please check the console for details.');
    }
  };

  const handleApproveRefund = async () => {
    if (!billingInfo) {
      alert('Billing information not available');
      return;
    }

    const adminToken = localStorage.getItem('admin_token');
    if (!adminToken) return;

    try {
      // Use provided reason or default message
      const reason = refundReason.trim() || 'Refund approved by admin';
      await approveRefund(billingInfo.billing_id, reason, adminToken);
      setShowRefundModal(false);
      setBillingInfo(null);
      setSelectedBooking(null);
      setRefundReason('');
      loadBookings();
      alert('Refund approved successfully. Booking status updated to cancelled.');
    } catch (err: any) {
      alert(err.message || 'Failed to approve refund');
    }
  };

  const handleRejectRefund = async () => {
    if (!billingInfo) {
      alert('Billing information not available');
      return;
    }

    if (!refundReason.trim()) {
      alert('Please provide a reason for rejection');
      return;
    }

    const adminToken = localStorage.getItem('admin_token');
    if (!adminToken) return;

    try {
      await rejectRefund(billingInfo.billing_id, refundReason, adminToken);
      setShowRefundModal(false);
      setBillingInfo(null);
      setSelectedBooking(null);
      setRefundReason('');
      loadBookings();
      alert('Refund rejected');
    } catch (err: any) {
      alert(err.message || 'Failed to reject refund');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'confirmed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'cancelled':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'refund_pending':
        return <Clock className="w-5 h-5 text-orange-500" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-blue-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'confirmed':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'cancelled':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'refund_pending':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'completed':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-slate-900 flex items-center">
                <Calendar className="mr-3 text-slate-600" size={36} />
                Bookings Management
              </h1>
              <p className="mt-2 text-slate-600">Manage all customer bookings</p>
            </div>
            <button
              onClick={() => navigate('/admin')}
              className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-md"
            >
              Back to Dashboard
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border-2 border-slate-200">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Booking Type</label>
              <select
                value={filterType}
                onChange={(e) => {
                  setFilterType(e.target.value);
                  setPage(1);
                }}
                className="w-full px-4 py-2 border-2 border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
              >
                <option value="all">All Types</option>
                <option value="flight">Flights</option>
                <option value="hotel">Hotels</option>
                <option value="car">Cars</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Status</label>
              <select
                value={filterStatus}
                onChange={(e) => {
                  setFilterStatus(e.target.value);
                  setPage(1);
                }}
                className="w-full px-4 py-2 border-2 border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
              >
                <option value="all">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="confirmed">Confirmed</option>
                <option value="refund_pending">Refund Pending</option>
                <option value="cancelled">Cancelled</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={loadBookings}
                className="w-full px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-md flex items-center justify-center"
              >
                <Search className="w-4 h-4 mr-2" />
                Refresh
              </button>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <p className="mt-4 text-slate-600">Loading bookings...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-xl mb-8">
            <p className="font-bold">Error:</p>
            <p>{error}</p>
            <button
              onClick={loadBookings}
              className="mt-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Bookings Table */}
        {!loading && !error && (
          <>
            <div className="bg-white rounded-xl shadow-lg overflow-hidden border-2 border-slate-200">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-100">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Booking ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Type</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">User ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Amount</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-slate-200">
                    {bookings.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="px-6 py-12 text-center text-slate-500">
                          <Calendar className="w-12 h-12 mx-auto mb-2 text-slate-400" />
                          <p>No bookings found</p>
                        </td>
                      </tr>
                    ) : (
                      bookings.map((booking) => (
                        <tr key={booking.booking_id} className="hover:bg-slate-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-slate-900">{booking.booking_id}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-700 capitalize">{booking.booking_type}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-slate-700">{booking.user_id}</td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(booking.status)}`}>
                              {getStatusIcon(booking.status)}
                              <span className="ml-1 capitalize">{booking.status}</span>
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-slate-900">
                            ${booking.total_price.toFixed(2)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                            {formatDate(booking.created_at)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() => {
                                  setSelectedBooking(booking);
                                  setNewStatus(booking.status);
                                  setShowStatusModal(true);
                                }}
                                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                title="Edit Status"
                              >
                                <Edit className="w-4 h-4" />
                              </button>
                              <button
                              onClick={() => {
                                setSelectedBooking(booking);
                                setCancelReason('');
                                setShowCancelModal(true);
                              }}
                                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                title="Cancel Booking"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                              {(booking.status === 'confirmed' || booking.status === 'refund_pending' || booking.status === 'cancelled') && (
                                <button
                                  onClick={() => handleViewRefund(booking)}
                                  className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                                  title="View/Approve Refund"
                                >
                                  <DollarSign className="w-4 h-4" />
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Pagination */}
            {total > pageSize && (
              <div className="mt-6 flex items-center justify-between">
                <div className="text-sm text-slate-600">
                  Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of {total} bookings
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 border-2 border-slate-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage(p => p + 1)}
                    disabled={page * pageSize >= total}
                    className="px-4 py-2 border-2 border-slate-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}

        {/* Status Update Modal */}
        {showStatusModal && selectedBooking && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
              <h3 className="text-xl font-bold text-slate-900 mb-4">Update Booking Status</h3>
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">New Status</label>
                <select
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value)}
                  className="w-full px-4 py-2 border-2 border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                >
                  <option value="pending">Pending</option>
                  <option value="confirmed">Confirmed</option>
                  <option value="cancelled">Cancelled</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    setShowStatusModal(false);
                    setSelectedBooking(null);
                    setNewStatus('');
                  }}
                  className="flex-1 px-4 py-2 border-2 border-slate-300 rounded-lg hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpdateStatus}
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800"
                >
                  Update
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Cancel Booking Modal */}
        {showCancelModal && selectedBooking && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
              <h3 className="text-xl font-bold text-slate-900 mb-4">Cancel Booking</h3>
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">Reason</label>
                <textarea
                  value={cancelReason}
                  onChange={(e) => setCancelReason(e.target.value)}
                  placeholder="Enter reason for cancellation (unavoidable conditions, technical/business reasons, etc.)"
                  className="w-full px-4 py-2 border-2 border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white h-24"
                />
              </div>
              <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Note:</strong> If this booking has a completed payment, the refund will automatically be set to <strong>pending</strong> and will require admin approval.
                </p>
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    setShowCancelModal(false);
                    setSelectedBooking(null);
                    setCancelReason('');
                  }}
                  className="flex-1 px-4 py-2 border-2 border-slate-300 rounded-lg hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCancelBooking}
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-lg hover:from-red-700 hover:to-red-800"
                >
                  Cancel Booking
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Refund Approval Modal */}
        {showRefundModal && selectedBooking && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
              <h3 className="text-xl font-bold text-slate-900 mb-4">Refund Management</h3>
              {!billingInfo ? (
                <div className="text-center py-8">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-4"></div>
                  <p className="text-slate-600 mb-4">Loading billing information...</p>
                  <button
                    onClick={() => {
                      setShowRefundModal(false);
                      setBillingInfo(null);
                      setSelectedBooking(null);
                      setRefundReason('');
                    }}
                    className="px-4 py-2 border-2 border-slate-300 rounded-lg hover:bg-slate-50"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <>
                  <div className="mb-4 space-y-2">
                    <div>
                      <p className="text-sm text-slate-600">Booking ID:</p>
                      <p className="font-mono text-sm text-slate-900">{selectedBooking.booking_id}</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-600">Billing ID:</p>
                      <p className="font-mono text-sm text-slate-900">{billingInfo.billing_id}</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-600">Amount:</p>
                      <p className="font-semibold text-slate-900">${(typeof billingInfo.total_amount === 'number' ? billingInfo.total_amount : parseFloat(billingInfo.total_amount || '0')).toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-600">Payment Status:</p>
                      <p className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                        billingInfo.payment_status === 'refund_pending' ? 'bg-yellow-100 text-yellow-800' :
                        billingInfo.payment_status === 'refunded' ? 'bg-green-100 text-green-800' :
                        billingInfo.payment_status === 'completed' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {billingInfo.payment_status === 'refund_pending' ? 'Refund Pending Approval' :
                         billingInfo.payment_status === 'refunded' ? 'Refunded' :
                         billingInfo.payment_status === 'completed' ? 'Payment Completed' :
                         billingInfo.payment_status}
                      </p>
                    </div>
                  </div>
                  {billingInfo.payment_status === 'refund_pending' && (
                <>
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-slate-700 mb-2">Reason</label>
                    <textarea
                      value={refundReason}
                      onChange={(e) => setRefundReason(e.target.value)}
                      placeholder="Enter reason for approval/rejection"
                      className="w-full px-4 py-2 border-2 border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white h-24"
                    />
                  </div>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => {
                        setShowRefundModal(false);
                        setBillingInfo(null);
                        setSelectedBooking(null);
                        setRefundReason('');
                      }}
                      className="flex-1 px-4 py-2 border-2 border-slate-300 rounded-lg hover:bg-slate-50"
                    >
                      Close
                    </button>
                    <button
                      onClick={handleRejectRefund}
                      className="flex-1 px-4 py-2 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-lg hover:from-red-700 hover:to-red-800"
                    >
                      Reject
                    </button>
                    <button
                      onClick={handleApproveRefund}
                      className="flex-1 px-4 py-2 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:from-green-700 hover:to-green-800"
                    >
                      Approve
                    </button>
                  </div>
                </>
              )}
                  {billingInfo.payment_status !== 'refund_pending' && (
                    <div>
                      {billingInfo.payment_status === 'refunded' && (
                        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                          <p className="text-sm text-green-800">
                            <strong>Refund Completed:</strong> This refund has been approved and processed. The booking status is cancelled.
                          </p>
                        </div>
                      )}
                      <button
                        onClick={() => {
                          setShowRefundModal(false);
                          setBillingInfo(null);
                          setSelectedBooking(null);
                          setRefundReason('');
                        }}
                        className="w-full px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800"
                      >
                        Close
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminBookingsManagement;

