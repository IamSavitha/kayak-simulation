import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format, parseISO, isFuture, isPast } from 'date-fns';
import toast from 'react-hot-toast';
import { FaPlane, FaHotel, FaCar, FaStar } from 'react-icons/fa';
import {
  HiCalendar,
  HiClock,
  HiLocationMarker,
  HiTicket,
  HiCurrencyDollar,
  HiX,
  HiCheck,
  HiExclamation,
  HiRefresh,
  HiDownload,
} from 'react-icons/hi';
import { useAuthStore } from '../../store/authStore';
import { mockBookingService, mockBillingService, Booking, Billing } from '../../services/mockData';

// Booking Card Component
const BookingCard: React.FC<{
  booking: Booking;
  onCancel: (id: string) => void;
  onViewDetails: (booking: Booking) => void;
}> = ({ booking, onCancel, onViewDetails }) => {
  const getTypeIcon = () => {
    switch (booking.booking_type) {
      case 'flight': return FaPlane;
      case 'hotel': return FaHotel;
      case 'car': return FaCar;
    }
  };

  const TypeIcon = getTypeIcon();

  const getStatusColor = () => {
    switch (booking.status) {
      case 'pending': return 'bg-yellow-500/20 text-yellow-400';
      case 'confirmed': return 'bg-green-500/20 text-green-400';
      case 'completed': return 'bg-blue-500/20 text-blue-400';
      case 'cancelled': return 'bg-red-500/20 text-red-400';
    }
  };

  const getTypeColor = () => {
    switch (booking.booking_type) {
      case 'flight': return 'bg-primary-500/20 text-primary-400';
      case 'hotel': return 'bg-secondary-500/20 text-secondary-400';
      case 'car': return 'bg-accent-emerald/20 text-accent-emerald';
    }
  };

  const canCancel = ['pending', 'confirmed'].includes(booking.status) && 
                    isFuture(parseISO(booking.check_in_date));

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="card-hover p-6"
    >
      <div className="flex items-start space-x-4">
        {/* Icon */}
        <div className={`w-16 h-16 rounded-xl flex items-center justify-center ${getTypeColor()}`}>
          <TypeIcon className="w-8 h-8" />
        </div>

        {/* Content */}
        <div className="flex-1">
          <div className="flex items-start justify-between mb-2">
            <div>
              <div className="flex items-center space-x-2 mb-1">
                <span className={`badge ${getTypeColor()}`}>
                  <TypeIcon className="w-3 h-3 mr-1" />
                  {booking.booking_type.charAt(0).toUpperCase() + booking.booking_type.slice(1)}
                </span>
                <span className={`badge ${getStatusColor()}`}>
                  {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
                </span>
                <span className="text-gray-500 text-sm">#{booking.booking_id}</span>
              </div>
              <h3 className="text-lg font-semibold text-white">{booking.listing_name}</h3>
              <p className="text-gray-400 text-sm">{booking.provider}</p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-primary-400">
                ${booking.total_price.toFixed(2)}
              </p>
            </div>
          </div>

          {/* Details */}
          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-400 mb-4">
            <span className="flex items-center">
              <HiCalendar className="w-4 h-4 mr-1" />
              {format(parseISO(booking.check_in_date), 'MMM dd, yyyy')}
              {booking.check_out_date && (
                <> - {format(parseISO(booking.check_out_date), 'MMM dd, yyyy')}</>
              )}
            </span>
            {booking.num_passengers && (
              <span className="flex items-center">
                <HiTicket className="w-4 h-4 mr-1" />
                {booking.num_passengers} passenger{booking.num_passengers > 1 ? 's' : ''}
              </span>
            )}
            {booking.num_rooms && (
              <span className="flex items-center">
                <FaHotel className="w-4 h-4 mr-1" />
                {booking.num_rooms} room{booking.num_rooms > 1 ? 's' : ''} • {booking.num_nights} night{booking.num_nights && booking.num_nights > 1 ? 's' : ''}
              </span>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-3">
            <button
              onClick={() => onViewDetails(booking)}
              className="btn-ghost text-sm"
            >
              View Details
            </button>
            {canCancel && (
              <button
                onClick={() => onCancel(booking.booking_id)}
                className="btn-ghost text-sm text-red-400 hover:bg-red-500/10"
              >
                Cancel Booking
              </button>
            )}
            {booking.status === 'completed' && (
              <button className="btn-ghost text-sm text-primary-400">
                <FaStar className="w-3 h-3 mr-1" />
                Write Review
              </button>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

// Booking Details Modal
const BookingDetailsModal: React.FC<{
  booking: Booking;
  onClose: () => void;
}> = ({ booking, onClose }) => {
  const { data: billing, isLoading } = useQuery({
    queryKey: ['billing', booking.booking_id],
    queryFn: () => mockBillingService.getBillByBooking(booking.booking_id),
  });

  const getTypeIcon = () => {
    switch (booking.booking_type) {
      case 'flight': return FaPlane;
      case 'hotel': return FaHotel;
      case 'car': return FaCar;
    }
  };

  const TypeIcon = getTypeIcon();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-dark-950/80 backdrop-blur-sm p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="card w-full max-w-2xl max-h-[90vh] overflow-y-auto"
      >
        {/* Header */}
        <div className="p-6 border-b border-dark-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                booking.booking_type === 'flight' ? 'bg-primary-500/20 text-primary-400' :
                booking.booking_type === 'hotel' ? 'bg-secondary-500/20 text-secondary-400' :
                'bg-accent-emerald/20 text-accent-emerald'
              }`}>
                <TypeIcon className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-white">{booking.listing_name}</h3>
                <p className="text-gray-400">{booking.provider}</p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 text-gray-400 hover:text-white rounded-lg">
              <HiX className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Status and ID */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className={`badge ${
                booking.status === 'confirmed' ? 'badge-success' :
                booking.status === 'pending' ? 'badge-warning' :
                booking.status === 'completed' ? 'badge-primary' : 'badge-error'
              }`}>
                {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
              </span>
              <span className="text-gray-500">Booking #{booking.booking_id}</span>
            </div>
            <p className="text-2xl font-bold text-primary-400">
              ${booking.total_price.toFixed(2)}
            </p>
          </div>

          {/* Booking Details */}
          <div className="grid grid-cols-2 gap-4">
            <div className="card p-4 bg-dark-800/50">
              <p className="text-gray-500 text-sm mb-1">Check-in Date</p>
              <p className="text-white font-medium">
                {format(parseISO(booking.check_in_date), 'EEEE, MMMM dd, yyyy')}
              </p>
            </div>
            {booking.check_out_date && (
              <div className="card p-4 bg-dark-800/50">
                <p className="text-gray-500 text-sm mb-1">Check-out Date</p>
                <p className="text-white font-medium">
                  {format(parseISO(booking.check_out_date), 'EEEE, MMMM dd, yyyy')}
                </p>
              </div>
            )}
            {booking.num_passengers && (
              <div className="card p-4 bg-dark-800/50">
                <p className="text-gray-500 text-sm mb-1">Passengers</p>
                <p className="text-white font-medium">{booking.num_passengers}</p>
              </div>
            )}
            {booking.num_rooms && (
              <>
                <div className="card p-4 bg-dark-800/50">
                  <p className="text-gray-500 text-sm mb-1">Rooms</p>
                  <p className="text-white font-medium">{booking.num_rooms}</p>
                </div>
                <div className="card p-4 bg-dark-800/50">
                  <p className="text-gray-500 text-sm mb-1">Nights</p>
                  <p className="text-white font-medium">{booking.num_nights}</p>
                </div>
              </>
            )}
            <div className="card p-4 bg-dark-800/50">
              <p className="text-gray-500 text-sm mb-1">Booking Date</p>
              <p className="text-white font-medium">
                {format(parseISO(booking.booking_date), 'MMM dd, yyyy HH:mm')}
              </p>
            </div>
          </div>

          {/* Payment Information */}
          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Payment Information</h4>
            {isLoading ? (
              <div className="card p-4 bg-dark-800/50 animate-pulse">
                <div className="h-4 bg-dark-700 rounded w-1/2 mb-2"></div>
                <div className="h-4 bg-dark-700 rounded w-1/3"></div>
              </div>
            ) : billing ? (
              <div className="card p-4 bg-dark-800/50 space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Invoice #</span>
                  <span className="text-white">{billing.invoice_number}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Payment Method</span>
                  <span className="text-white capitalize">
                    {billing.payment_method.replace('_', ' ')}
                    {billing.card_last_four && ` •••• ${billing.card_last_four}`}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Payment Status</span>
                  <span className={`badge ${
                    billing.payment_status === 'completed' ? 'badge-success' :
                    billing.payment_status === 'pending' ? 'badge-warning' : 'badge-error'
                  }`}>
                    {billing.payment_status}
                  </span>
                </div>
                <div className="border-t border-dark-600 pt-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Subtotal</span>
                    <span className="text-white">${billing.subtotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Tax</span>
                    <span className="text-white">${billing.tax_amount.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between font-semibold mt-2">
                    <span className="text-white">Total</span>
                    <span className="text-primary-400">${billing.total_amount.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="card p-4 bg-dark-800/50 text-center">
                <p className="text-gray-400">Payment information not available</p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-dark-700 flex justify-between">
          <button className="btn-ghost">
            <HiDownload className="w-5 h-5 mr-2" />
            Download Receipt
          </button>
          <button onClick={onClose} className="btn-primary">
            Close
          </button>
        </div>
      </motion.div>
    </div>
  );
};

// Main Bookings Page
const BookingsPage: React.FC = () => {
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'upcoming' | 'past'>('upcoming');
  const [selectedBooking, setSelectedBooking] = useState<Booking | null>(null);

  // Use a mock user ID for demo purposes
  const userId = user?.user_id || '123-45-6789';

  // Queries
  const upcomingQuery = useQuery({
    queryKey: ['bookings', 'upcoming', userId],
    queryFn: () => mockBookingService.getUpcomingBookings(userId),
  });

  const pastQuery = useQuery({
    queryKey: ['bookings', 'past', userId],
    queryFn: () => mockBookingService.getPastBookings(userId),
  });

  // Cancel mutation
  const cancelMutation = useMutation({
    mutationFn: (bookingId: string) => mockBookingService.cancelBooking(bookingId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookings'] });
      toast.success('Booking cancelled successfully');
    },
    onError: () => {
      toast.error('Failed to cancel booking');
    },
  });

  const handleCancel = (bookingId: string) => {
    if (window.confirm('Are you sure you want to cancel this booking? This action cannot be undone.')) {
      cancelMutation.mutate(bookingId);
    }
  };

  const currentQuery = activeTab === 'upcoming' ? upcomingQuery : pastQuery;
  const bookings = currentQuery.data || [];
  const isLoading = currentQuery.isLoading;

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl font-display font-bold text-white mb-2">
            My Bookings
          </h1>
          <p className="text-gray-400">View and manage your trips</p>
        </div>

        {/* Tabs */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveTab('upcoming')}
              className={`px-6 py-3 rounded-xl font-medium transition-all ${
                activeTab === 'upcoming'
                  ? 'bg-primary-500 text-dark-950'
                  : 'bg-dark-800 text-gray-300 hover:bg-dark-700'
              }`}
            >
              Upcoming ({upcomingQuery.data?.length || 0})
            </button>
            <button
              onClick={() => setActiveTab('past')}
              className={`px-6 py-3 rounded-xl font-medium transition-all ${
                activeTab === 'past'
                  ? 'bg-primary-500 text-dark-950'
                  : 'bg-dark-800 text-gray-300 hover:bg-dark-700'
              }`}
            >
              Past Trips ({pastQuery.data?.length || 0})
            </button>
          </div>
          <button
            onClick={() => currentQuery.refetch()}
            className="p-2 text-gray-400 hover:text-white transition-colors"
            disabled={isLoading}
          >
            <HiRefresh className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Bookings List */}
        <AnimatePresence mode="wait">
          <div className="space-y-4">
            {isLoading ? (
              // Loading skeleton
              [...Array(3)].map((_, i) => (
                <div key={i} className="card p-6 animate-pulse">
                  <div className="flex items-start space-x-4">
                    <div className="w-16 h-16 bg-dark-700 rounded-xl"></div>
                    <div className="flex-1 space-y-3">
                      <div className="flex space-x-2">
                        <div className="w-16 h-6 bg-dark-700 rounded"></div>
                        <div className="w-20 h-6 bg-dark-700 rounded"></div>
                      </div>
                      <div className="w-48 h-5 bg-dark-700 rounded"></div>
                      <div className="w-32 h-4 bg-dark-700 rounded"></div>
                    </div>
                    <div className="w-24 h-8 bg-dark-700 rounded"></div>
                  </div>
                </div>
              ))
            ) : bookings.length === 0 ? (
              // Empty state
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="card p-12 text-center"
              >
                <div className="text-6xl mb-4">
                  {activeTab === 'upcoming' ? '✈️' : '📅'}
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  No {activeTab} trips
                </h3>
                <p className="text-gray-400 mb-6">
                  {activeTab === 'upcoming'
                    ? "You don't have any upcoming trips. Start planning your next adventure!"
                    : 'Your completed trips will appear here.'}
                </p>
                {activeTab === 'upcoming' && (
                  <a href="/search/flights" className="btn-primary">
                    Search Flights
                  </a>
                )}
              </motion.div>
            ) : (
              // Bookings list
              bookings.map((booking) => (
                <BookingCard
                  key={booking.booking_id}
                  booking={booking}
                  onCancel={handleCancel}
                  onViewDetails={setSelectedBooking}
                />
              ))
            )}
          </div>
        </AnimatePresence>

        {/* Booking Details Modal */}
        <AnimatePresence>
          {selectedBooking && (
            <BookingDetailsModal
              booking={selectedBooking}
              onClose={() => setSelectedBooking(null)}
            />
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

export default BookingsPage;
