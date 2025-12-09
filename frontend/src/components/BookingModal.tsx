import React, { useState } from 'react';
import { X, Plane, Calendar, Users, DollarSign, Loader2, CheckCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { createBooking, BookingCreate } from '../api/bookings';
import { useNavigate } from 'react-router-dom';
import PaymentModal from './PaymentModal';
import { BillingResponse } from '../api/billing';

interface Flight {
  id: string;
  airline: string;
  from: string;
  to: string;
  departure: string;
  arrival: string;
  departure_datetime?: string; // Full ISO datetime string
  arrival_datetime?: string; // Full ISO datetime string
  duration: string;
  price: number;
  class: string;
  travelers: string;
}

interface BookingModalProps {
  flight: Flight | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

const BookingModal: React.FC<BookingModalProps> = ({ flight, isOpen, onClose, onSuccess }) => {
  const { user, token, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [bookingId, setBookingId] = useState<string | null>(null);
  const [showPayment, setShowPayment] = useState(false);
  const [booking, setBooking] = useState<any>(null);

  if (!isOpen || !flight) return null;

  const handleBooking = async () => {
    if (!isAuthenticated || !user || !token) {
      setError('Please log in to book a flight');
      setTimeout(() => {
        navigate('/login');
      }, 2000);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Use the actual departure datetime from the flight data
      let checkInDate: string;
      if (flight.departure_datetime) {
        // Use the exact datetime from the API without conversion
        // This preserves the original date/time from the flight data
        checkInDate = flight.departure_datetime;
      } else {
        // Fallback: construct from departure time (shouldn't happen if API is correct)
        const today = new Date();
        const [time, period] = flight.departure.split(' ');
        const [hours, minutes] = time.split(':');
        let hour24 = parseInt(hours);
        if (period === 'PM' && hour24 !== 12) hour24 += 12;
        if (period === 'AM' && hour24 === 12) hour24 = 0;
        
        today.setHours(hour24, parseInt(minutes), 0, 0);
        // Add 7 days to make it a future date
        today.setDate(today.getDate() + 7);
        checkInDate = today.toISOString();
      }

      // Convert flight class to uppercase (backend expects ECONOMY, BUSINESS, FIRST)
      const flightClass = flight.class ? flight.class.toUpperCase() : undefined;
      
      const bookingData: BookingCreate = {
        user_id: user.user_id,
        booking_type: 'flight', // Backend will accept lowercase, but we'll send as-is
        listing_id: flight.id,
        check_in_date: checkInDate,
        num_passengers: parseInt(flight.travelers) || 1,
        flight_class: flightClass,
      };

      const bookingResponse = await createBooking(bookingData, token);
      setBookingId(bookingResponse.booking_id);
      setBooking(bookingResponse);
      // Show payment modal (it will appear on top with higher z-index)
      setShowPayment(true);
    } catch (err: any) {
      console.error('Booking error:', err);
      // Extract error message
      let errorMessage = 'Failed to create booking. Please try again.';
      if (err.message) {
        errorMessage = err.message;
      } else if (err instanceof Error) {
        errorMessage = err.message;
      } else if (typeof err === 'string') {
        errorMessage = err;
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setSuccess(false);
      setError(null);
      setBookingId(null);
      setShowPayment(false);
      setBooking(null);
      onClose();
    }
  };

  const handlePaymentSuccess = (billing: BillingResponse) => {
    setSuccess(true);
    setShowPayment(false);
    if (onSuccess) {
      onSuccess();
    }
  };

  // Calculate total price
  const totalPrice = flight.price * (parseInt(flight.travelers) || 1);

  return (
    <>
      {/* Payment Modal - Higher z-index to appear on top */}
      {showPayment && bookingId && (
        <PaymentModal
          bookingId={bookingId}
          bookingType="flight"
          amount={totalPrice}
          isOpen={showPayment}
          onClose={() => {
            setShowPayment(false);
          }}
          onSuccess={handlePaymentSuccess}
        />
      )}
      {/* Booking Modal - Only show if payment modal is not showing */}
      {!showPayment && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto animate-scale-in">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 rounded-t-2xl flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Plane className="w-6 h-6" />
            <h2 className="text-2xl font-bold">
              {success ? 'Booking Confirmed!' : 'Confirm Your Flight Booking'}
            </h2>
          </div>
          <button
            onClick={handleClose}
            disabled={loading}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors disabled:opacity-50"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {success ? (
            <div className="text-center py-8">
              <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-4" />
              <h3 className="text-2xl font-bold text-slate-900 mb-2">Booking Successful!</h3>
              <p className="text-slate-600 mb-4">
                Your flight has been booked successfully.
              </p>
              {bookingId && (
                <div className="bg-slate-100 rounded-lg p-4 mb-6">
                  <p className="text-sm text-slate-600">Booking ID</p>
                  <p className="text-lg font-bold text-slate-900">{bookingId}</p>
                </div>
              )}
              <div className="flex gap-4 justify-center">
                <button
                  onClick={() => navigate('/bookings')}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                >
                  View My Bookings
                </button>
                <button
                  onClick={handleClose}
                  className="px-6 py-3 bg-slate-200 text-slate-800 rounded-lg font-semibold hover:bg-slate-300 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          ) : (
            <>
              {/* Flight Details */}
              <div className="bg-slate-50 rounded-xl p-6 mb-6">
                <h3 className="text-lg font-bold text-slate-900 mb-4">Flight Details</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-600">Airline</p>
                      <p className="font-semibold text-slate-900">{flight.airline}</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-600">Class</p>
                      <p className="font-semibold text-slate-900 capitalize">{flight.class}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between py-4 border-y border-slate-200">
                    <div>
                      <p className="text-sm text-slate-600">Departure</p>
                      <p className="text-xl font-bold text-slate-900">{flight.from}</p>
                      <p className="text-sm text-slate-600">{flight.departure}</p>
                      {flight.departure_datetime && (
                        <p className="text-xs text-slate-500 mt-1">
                          <Calendar size={12} className="inline mr-1" />
                          {new Date(flight.departure_datetime).toLocaleDateString('en-US', { 
                            weekday: 'short',
                            month: 'short', 
                            day: 'numeric', 
                            year: 'numeric' 
                          })}
                        </p>
                      )}
                    </div>
                    <div className="flex-1 px-4">
                      <div className="flex items-center">
                        <div className="flex-1 h-0.5 bg-slate-300"></div>
                        <Plane className="mx-2 text-slate-400" size={20} />
                        <div className="flex-1 h-0.5 bg-slate-300"></div>
                      </div>
                      <p className="text-center text-xs text-slate-500 mt-1">{flight.duration}</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-600">Arrival</p>
                      <p className="text-xl font-bold text-slate-900">{flight.to}</p>
                      <p className="text-sm text-slate-600">{flight.arrival}</p>
                      {flight.arrival_datetime && (
                        <p className="text-xs text-slate-500 mt-1">
                          <Calendar size={12} className="inline mr-1" />
                          {new Date(flight.arrival_datetime).toLocaleDateString('en-US', { 
                            weekday: 'short',
                            month: 'short', 
                            day: 'numeric', 
                            year: 'numeric' 
                          })}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Users className="text-slate-600" size={18} />
                      <span className="text-sm text-slate-600">
                        {flight.travelers} {parseInt(flight.travelers) === 1 ? 'Passenger' : 'Passengers'}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <DollarSign className="text-slate-600" size={18} />
                      <span className="text-2xl font-bold text-slate-900">${flight.price}</span>
                      <span className="text-sm text-slate-600">per person</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* User Info */}
              {user && (
                <div className="bg-blue-50 rounded-xl p-4 mb-6">
                  <p className="text-sm text-slate-600 mb-1">Booking for</p>
                  <p className="font-semibold text-slate-900">
                    {user.first_name} {user.last_name}
                  </p>
                  <p className="text-sm text-slate-600">{user.email}</p>
                </div>
              )}

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}

              {/* Total Price */}
              <div className="bg-slate-900 text-white rounded-xl p-6 mb-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-300 text-sm">Total Price</p>
                    <p className="text-3xl font-bold">
                      ${(flight.price * (parseInt(flight.travelers) || 1)).toFixed(2)}
                    </p>
                    <p className="text-slate-400 text-xs mt-1">
                      ${flight.price} × {flight.travelers} {parseInt(flight.travelers) === 1 ? 'passenger' : 'passengers'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-4">
                <button
                  onClick={handleClose}
                  disabled={loading}
                  className="flex-1 px-6 py-3 bg-slate-200 text-slate-800 rounded-lg font-semibold hover:bg-slate-300 transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleBooking}
                  disabled={loading || !isAuthenticated}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-blue-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="animate-spin" size={20} />
                      <span>Processing...</span>
                    </>
                  ) : (
                    <>
                      <span>Confirm Booking</span>
                      <Plane size={20} />
                    </>
                  )}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
        </div>
        )}
    </>
  );
};

export default BookingModal;

