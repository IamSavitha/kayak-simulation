import React, { useState, useEffect } from 'react';
import { Hotel, MapPin, Calendar, Users, Search, Filter, Star, Wifi, Coffee, ParkingSquare, ArrowRight, DollarSign, Loader2, X, Phone, Globe, Mail, CheckCircle } from 'lucide-react';
import { searchHotels, Hotel as HotelAPI, HotelSearchParams, getHotel } from '../api/hotels';
import { useAuth } from '../context/AuthContext';
import { createBooking, BookingCreate } from '../api/bookings';
import { useNavigate, useSearchParams } from 'react-router-dom';
import PaymentModal from '../components/PaymentModal';
import { BillingResponse } from '../api/billing';

interface HotelListing {
  id: string;
  name: string;
  location: string;
  rating: number;
  reviews: number;
  price: number;
  image: string;
  amenities: string[];
  roomType: string;
  available_rooms?: number; // Available rooms for selected dates
}

const HotelsPage: React.FC = () => {
  const [showFilters, setShowFilters] = useState(false);
  const [hotels, setHotels] = useState<HotelListing[]>([]);
  const [filteredHotels, setFilteredHotels] = useState<HotelListing[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedHotel, setSelectedHotel] = useState<HotelAPI | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [bookingLoading, setBookingLoading] = useState(false);
  const [bookingError, setBookingError] = useState<string | null>(null);
  const [bookingSuccess, setBookingSuccess] = useState(false);
  const [bookingId, setBookingId] = useState<string | null>(null);
  const [showPayment, setShowPayment] = useState(false);
  const [booking, setBooking] = useState<any>(null);
  const { user, token, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [urlSearchParams] = useSearchParams();
  
  // Editable booking parameters in modal
  const [bookingParams, setBookingParams] = useState({
    checkIn: '',
    checkOut: '',
    guests: '2',
    rooms: '1'
  });
  const [searchParams, setSearchParams] = useState({
    city: '',
    checkIn: '',
    checkOut: '',
    guests: '2'
  });
  const [filters, setFilters] = useState({
    priceRange: [0, 500] as [number, number],
    starRatings: [] as number[],
    amenities: [] as string[]
  });

  // Generate hotel image URL - using reliable Unsplash Source URLs
  const getHotelImage = (hotelName: string, city: string, hotelId?: string): string => {
    // Updated hotel image URLs with proper format
    const hotelImages = [
      'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=400&h=300',
      'https://images.unsplash.com/photo-1571896346562-66123b1b1cfa?auto=format&fit=crop&w=400&h=300',
      'https://images.unsplash.com/photo-1551884170-09c70a23afe8?auto=format&fit=crop&w=400&h=300',
      'https://images.unsplash.com/photo-1564501049412-61c2d308c1b8?auto=format&fit=crop&w=400&h=300',
      'https://images.unsplash.com/photo-1582719508467-0b99ccb8756b?auto=format&fit=crop&w=400&h=300',
      'https://images.unsplash.com/photo-1571003123894-1f0595d1b052?auto=format&fit=crop&w=400&h=300',
      'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=400&h=300',
      'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=400&h=300',
      'https://images.unsplash.com/photo-1445019980597-93fa8acb246c?auto=format&fit=crop&w=400&h=300',
      'https://images.unsplash.com/photo-1496417263034-38ec4f0b665a?auto=format&fit=crop&w=400&h=300',
    ];
    
    // Use hotel name + city to deterministically select an image
    const seedString = (hotelName || '') + (city || '') + (hotelId || '');
    const seed = seedString.split('').reduce((acc, char) => {
      return ((acc << 5) - acc) + char.charCodeAt(0);
    }, 0);
    
    const imageIndex = Math.abs(seed) % hotelImages.length;
    const defaultImage = 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=400&h=300';
    return hotelImages[imageIndex] || defaultImage;
  };

  // Convert API hotel to display format
  const convertHotel = (hotel: HotelAPI): HotelListing => {
    const cityState = hotel.state ? `${hotel.city}, ${hotel.state}` : hotel.city || 'Unknown';
    
    // Handle amenities - could be string, array, or null
    let amenitiesList: string[] = [];
    if (hotel.amenities) {
      if (typeof hotel.amenities === 'string') {
        // If it's a string, try to parse it or split by comma
        try {
          const parsed = JSON.parse(hotel.amenities);
          amenitiesList = Array.isArray(parsed) ? parsed : [hotel.amenities];
        } catch {
          // If parsing fails, split by comma or use as single item
          const amenityStr = String(hotel.amenities);
          amenitiesList = amenityStr.includes(',') 
            ? amenityStr.split(',').map((a: string) => a.trim())
            : [amenityStr];
        }
      } else if (Array.isArray(hotel.amenities)) {
        amenitiesList = hotel.amenities;
      }
    }
    
    return {
      id: hotel.hotel_id || '',
      name: hotel.hotel_name || 'Unknown Hotel',
      location: cityState,
      rating: hotel.rating || hotel.star_rating || 4.0,
      reviews: hotel.total_reviews || 0,
      price: (hotel as any).min_price || 150, // Use minimum room price from API
      image: getHotelImage(hotel.hotel_name || '', hotel.city || '', hotel.hotel_id),
      amenities: amenitiesList,
      roomType: 'Standard Room',
      available_rooms: hotel.available_rooms || hotel.total_available_rooms || 0
    };
  };

  // Load hotels on mount and when search params change
  useEffect(() => {
    loadHotels();
  }, []);

  // Handle hotel_id from URL query params (from deals page)
  useEffect(() => {
    const hotelId = urlSearchParams.get('hotel_id');
    if (hotelId && hotels.length > 0) {
      // Small delay to ensure hotels are loaded
      setTimeout(() => {
        handleViewDetails(hotelId);
      }, 500);
    }
  }, [urlSearchParams, hotels]);

  // Apply filters whenever hotels or filters change
  useEffect(() => {
    let filtered = [...hotels];

    // Price filter
    filtered = filtered.filter(hotel => 
      hotel.price >= filters.priceRange[0] && hotel.price <= filters.priceRange[1]
    );

    // Star rating filter
    if (filters.starRatings.length > 0) {
      filtered = filtered.filter(hotel => 
        filters.starRatings.some(rating => Math.floor(hotel.rating) >= rating)
      );
    }

    // Amenities filter
    if (filters.amenities.length > 0) {
      filtered = filtered.filter(hotel => 
        filters.amenities.some(amenity => 
          hotel.amenities.some(hotelAmenity => 
            hotelAmenity.toLowerCase().includes(amenity.toLowerCase())
          )
        )
      );
    }

    setFilteredHotels(filtered);
  }, [hotels, filters]);

  const loadHotels = async () => {
    setLoading(true);
    setError(null);
    try {
      const params: HotelSearchParams = {
        page: 1,
        page_size: 1000 // Show all hotels
      };
      
      if (searchParams.city) {
        params.city = searchParams.city;
      }
      if (searchParams.checkIn) {
        params.check_in_date = searchParams.checkIn;
      }
      if (searchParams.checkOut) {
        params.check_out_date = searchParams.checkOut;
      }
      if (searchParams.guests) {
        params.num_guests = parseInt(searchParams.guests);
      }

      const response = await searchHotels(params);
      // Safely convert hotels with error handling
      const convertedHotels = response.hotels
        .map((hotel) => {
          try {
            return convertHotel(hotel);
          } catch (error) {
            console.error('Error converting hotel:', hotel, error);
            return null;
          }
        })
        .filter((hotel): hotel is HotelListing => hotel !== null);
      
      setHotels(convertedHotels);
      setFilteredHotels(convertedHotels); // Initialize filtered hotels
    } catch (err: any) {
      setError(err.message || 'Failed to load hotels');
      console.error('Error loading hotels:', err);
      setHotels([]); // Set empty array on error to prevent blank page
      setFilteredHotels([]); // Also set filtered hotels to empty
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    // Validate dates before searching
    if (searchParams.checkIn && searchParams.checkOut) {
      if (new Date(searchParams.checkOut) <= new Date(searchParams.checkIn)) {
        setError('Check-out date must be after check-in date');
        return;
      }
    }
    setError(null);
    loadHotels();
  };

  const handleViewDetails = async (hotelId: string) => {
    setDetailsLoading(true);
    try {
      const hotel = await getHotel(hotelId);
      setSelectedHotel(hotel);
      setShowDetailsModal(true);
    } catch (err: any) {
      console.error('Error loading hotel details:', err);
      setError('Failed to load hotel details');
    } finally {
      setDetailsLoading(false);
    }
  };

  const handleCloseDetails = () => {
    setShowDetailsModal(false);
    setSelectedHotel(null);
    setShowBookingModal(false);
    setBookingError(null);
    setBookingSuccess(false);
    setBookingId(null);
    setShowPayment(false);
    setBooking(null);
  };

  const handlePaymentSuccess = (billing: BillingResponse) => {
    setBookingSuccess(true);
    setShowPayment(false);
    setShowBookingModal(false);
    setSelectedHotel(null);
    setBooking(null);
    setBookingId(null);
    // Navigate to bookings page to see the booking with billing info
    setTimeout(() => {
      navigate('/bookings');
    }, 2000);
  };

  const handleBookNow = () => {
    if (!isAuthenticated || !user || !token) {
      setBookingError('Please log in to book a hotel');
      setTimeout(() => {
        navigate('/login');
      }, 2000);
      return;
    }

    if (!searchParams.checkIn || !searchParams.checkOut) {
      setBookingError('Please select check-in and check-out dates');
      return;
    }

    if (new Date(searchParams.checkOut) <= new Date(searchParams.checkIn)) {
      setBookingError('Check-out date must be after check-in date');
      return;
    }

    // Initialize booking params from search params
    setBookingParams({
      checkIn: searchParams.checkIn,
      checkOut: searchParams.checkOut,
      guests: searchParams.guests,
      rooms: '1' // Default to 1 room
    });

    setShowBookingModal(true);
    setBookingError(null);
    setBookingSuccess(false);
  };

  const validateBookingParams = (): string | null => {
    if (!bookingParams.checkIn || !bookingParams.checkOut) {
      return 'Please select both check-in and check-out dates';
    }

    const checkIn = new Date(bookingParams.checkIn);
    const checkOut = new Date(bookingParams.checkOut);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (checkIn < today) {
      return 'Check-in date cannot be in the past';
    }

    if (checkOut <= checkIn) {
      return 'Check-out date must be after check-in date';
    }

    const guests = parseInt(bookingParams.guests) || 1;
    const rooms = parseInt(bookingParams.rooms) || 1;

    if (guests < 1) {
      return 'Number of guests must be at least 1';
    }

    if (rooms < 1) {
      return 'Number of rooms must be at least 1';
    }

    // Check if guests exceed reasonable capacity (assuming 2 guests per room max)
    if (guests > rooms * 4) {
      return `Too many guests for ${rooms} room(s). Maximum ${rooms * 4} guests allowed for ${rooms} room(s).`;
    }

    return null;
  };

  const parseBookingError = (errorMessage: string): string => {
    // Parse backend error messages to show user-friendly messages
    if (errorMessage.includes('No available room type found')) {
      return 'No rooms available for this hotel. Please try a different hotel or dates.';
    }
    if (errorMessage.includes('Insufficient rooms')) {
      const match = errorMessage.match(/Available: (\d+), Requested: (\d+)/);
      if (match) {
        return `Only ${match[1]} room(s) available, but you requested ${match[2]}. Please reduce the number of rooms.`;
      }
      return 'Not enough rooms available. Please reduce the number of rooms or try different dates.';
    }
    if (errorMessage.includes('already booked') || errorMessage.includes('overlapping')) {
      return 'These dates are not available. The hotel is already booked for the selected dates. Please choose different dates.';
    }
    if (errorMessage.includes('Room is already booked')) {
      return 'These dates are not available. Please choose different check-in or check-out dates.';
    }
    if (errorMessage.includes('Check-out date is required')) {
      return 'Please select a check-out date.';
    }
    return errorMessage;
  };

  const handleConfirmBooking = async () => {
    if (!selectedHotel || !user || !token) return;

    // Validate booking parameters
    const validationError = validateBookingParams();
    if (validationError) {
      setBookingError(validationError);
      return;
    }

    setBookingLoading(true);
    setBookingError(null);

    try {
      const checkInDate = new Date(bookingParams.checkIn).toISOString();
      const checkOutDate = new Date(bookingParams.checkOut).toISOString();
      const numRooms = parseInt(bookingParams.rooms) || 1;

      const bookingData: BookingCreate = {
        user_id: user.user_id,
        booking_type: 'hotel',
        listing_id: selectedHotel.hotel_id,
        check_in_date: checkInDate,
        check_out_date: checkOutDate,
        num_rooms: numRooms,
        // Don't specify room_type - let backend pick first available room
        // room_type: undefined,
      };

      const bookingResponse = await createBooking(bookingData, token);
      setBookingId(bookingResponse.booking_id);
      setBooking(bookingResponse);
      // Close booking modal but keep payment-related state
      setShowBookingModal(false);
      setShowDetailsModal(false);
      setBookingError(null);
      // Show payment modal instead of success immediately
      setShowPayment(true);
    } catch (err: any) {
      console.error('Booking error:', err);
      const errorMsg = err.message || 'Failed to create booking. Please try again.';
      setBookingError(parseBookingError(errorMsg));
    } finally {
      setBookingLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30">
      {/* Search Header */}
      <div className="bg-gradient-to-r from-slate-700 to-slate-800 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-8 animate-slide-down">Find Your Perfect Stay</h1>

          {/* Search Form */}
          <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-6 border-2 border-white/40 shadow-2xl animate-scale-in">
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700">Destination</label>
                <div className="flex items-center border-2 border-slate-300 rounded-xl px-4 py-3 bg-white hover:border-slate-500 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200 transition-all shadow-sm">
                  <MapPin className="text-slate-600 mr-3 flex-shrink-0" size={18} />
                  <input
                    type="text"
                    placeholder="Los Angeles, CA"
                    value={searchParams.city}
                    onChange={(e) => setSearchParams({ ...searchParams, city: e.target.value })}
                    className="w-full outline-none text-sm font-semibold text-slate-900 placeholder:text-slate-400 bg-transparent"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700">Check-in</label>
                <div className={`flex items-center border-2 rounded-xl px-4 py-3 bg-white transition-all shadow-sm ${
                  searchParams.checkOut && searchParams.checkIn && new Date(searchParams.checkOut) <= new Date(searchParams.checkIn)
                    ? 'border-red-500 focus-within:border-red-500 focus-within:ring-2 focus-within:ring-red-200'
                    : 'border-slate-300 hover:border-slate-500 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200'
                }`}>
                  <Calendar className="text-slate-600 mr-3 flex-shrink-0" size={18} />
                  <input
                    type="date"
                    value={searchParams.checkIn}
                    min={new Date().toISOString().split('T')[0]}
                    onChange={(e) => {
                      const newCheckIn = e.target.value;
                      setSearchParams({ ...searchParams, checkIn: newCheckIn });
                      // If check-out date is before or equal to new check-in date, clear it
                      if (searchParams.checkOut && new Date(searchParams.checkOut) <= new Date(newCheckIn)) {
                        setSearchParams({ ...searchParams, checkIn: newCheckIn, checkOut: '' });
                      }
                    }}
                    className="w-full outline-none text-sm font-semibold text-slate-900 placeholder:text-slate-400 bg-transparent [color-scheme:light]"
                  />
                </div>
                {searchParams.checkOut && searchParams.checkIn && new Date(searchParams.checkOut) <= new Date(searchParams.checkIn) && (
                  <p className="text-xs text-red-600 mt-1">Check-out date must be after check-in date</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700">Check-out</label>
                <div className={`flex items-center border-2 rounded-xl px-4 py-3 bg-white transition-all shadow-sm ${
                  searchParams.checkOut && searchParams.checkIn && new Date(searchParams.checkOut) <= new Date(searchParams.checkIn)
                    ? 'border-red-500 focus-within:border-red-500 focus-within:ring-2 focus-within:ring-red-200'
                    : 'border-slate-300 hover:border-slate-500 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200'
                }`}>
                  <Calendar className="text-slate-600 mr-3 flex-shrink-0" size={18} />
                  <input
                    type="date"
                    value={searchParams.checkOut}
                    min={searchParams.checkIn ? new Date(new Date(searchParams.checkIn).getTime() + 24 * 60 * 60 * 1000).toISOString().split('T')[0] : new Date().toISOString().split('T')[0]}
                    onChange={(e) => {
                      const newCheckOut = e.target.value;
                      // Validate that check-out is after check-in
                      if (searchParams.checkIn && new Date(newCheckOut) <= new Date(searchParams.checkIn)) {
                        // Don't update if invalid
                        return;
                      }
                      setSearchParams({ ...searchParams, checkOut: newCheckOut });
                    }}
                    className="w-full outline-none text-sm font-semibold text-slate-900 placeholder:text-slate-400 bg-transparent [color-scheme:light]"
                  />
                </div>
                {searchParams.checkOut && searchParams.checkIn && new Date(searchParams.checkOut) <= new Date(searchParams.checkIn) && (
                  <p className="text-xs text-red-600 mt-1">Check-out date must be after check-in date</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700">Guests</label>
                <div className="flex items-center border-2 border-slate-300 rounded-xl px-4 py-3 bg-white hover:border-slate-500 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200 transition-all shadow-sm">
                  <Users className="text-slate-600 mr-3 flex-shrink-0" size={18} />
                  <input
                    type="number"
                    placeholder="2"
                    min="1"
                    value={searchParams.guests}
                    onChange={(e) => setSearchParams({ ...searchParams, guests: e.target.value })}
                    className="w-full outline-none text-sm font-semibold text-slate-900 placeholder:text-slate-400 bg-transparent"
                  />
                </div>
              </div>
            </div>

            <button 
              onClick={handleSearch}
              disabled={loading}
              className="w-full mt-6 bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 font-bold py-4 px-6 rounded-xl flex items-center justify-center space-x-3 transition-all duration-200 shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] group disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
              {loading ? (
                <Loader2 size={20} className="animate-spin" />
              ) : (
              <Search size={20} className="group-hover:rotate-90 transition-transform duration-300" />
              )}
              <span className="text-base">{loading ? 'Searching...' : 'Search Hotels'}</span>
              {!loading && <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform duration-300" />}
            </button>
          </div>
        </div>
      </div>

      {/* Results Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold text-slate-900">Available Hotels</h2>
            {error ? (
              <p className="text-red-600 mt-1">{error}</p>
            ) : (
              <p className="text-slate-600 mt-1">
                {filteredHotels.length} of {hotels.length} properties found
              </p>
            )}
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn-secondary flex items-center space-x-2 py-2.5 px-5"
          >
            <Filter size={18} />
            <span>Filters</span>
          </button>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Filters Sidebar */}
          {showFilters && (
            <div className="lg:col-span-1 animate-slide-up">
              <div className="card p-6 sticky top-24">
                <h3 className="text-lg font-bold text-slate-900 mb-6">Filter Results</h3>

                {/* Price Range */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Price Range</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="text-xs text-slate-600 mb-1 block">Min: ${filters.priceRange[0]}</label>
                      <input 
                        type="range" 
                        min="0" 
                        max="500" 
                        className="w-full"
                        value={filters.priceRange[0]}
                        onChange={(e) => {
                          const min = parseInt(e.target.value);
                          if (min <= filters.priceRange[1]) {
                            setFilters({ ...filters, priceRange: [min, filters.priceRange[1]] });
                          }
                        }}
                      />
                    </div>
                    <div>
                      <label className="text-xs text-slate-600 mb-1 block">Max: ${filters.priceRange[1]}</label>
                      <input 
                        type="range" 
                        min="0" 
                        max="500" 
                        className="w-full"
                        value={filters.priceRange[1]}
                        onChange={(e) => {
                          const max = parseInt(e.target.value);
                          if (max >= filters.priceRange[0]) {
                            setFilters({ ...filters, priceRange: [filters.priceRange[0], max] });
                          }
                        }}
                      />
                    </div>
                  <div className="flex justify-between text-xs text-slate-600 mt-2">
                      <span>${filters.priceRange[0]}</span>
                      <span>${filters.priceRange[1]}</span>
                    </div>
                  </div>
                </div>

                {/* Star Rating */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Star Rating</h4>
                  <div className="space-y-2">
                    {[5, 4, 3, 2].map((stars) => (
                      <label key={stars} className="flex items-center space-x-2 cursor-pointer group">
                        <input 
                          type="checkbox" 
                          className="rounded text-slate-600 focus:ring-slate-500"
                          checked={filters.starRatings.includes(stars)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setFilters({ ...filters, starRatings: [...filters.starRatings, stars] });
                            } else {
                              setFilters({ ...filters, starRatings: filters.starRatings.filter(r => r !== stars) });
                            }
                          }}
                        />
                        <div className="flex items-center text-sm text-slate-600 group-hover:text-slate-900">
                          {Array.from({ length: stars }).map((_, i) => (
                            <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                          ))}
                          <span className="ml-1">& up</span>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Amenities */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Amenities</h4>
                  <div className="space-y-2">
                    {[
                      { icon: <Wifi size={16} />, label: 'WiFi', value: 'wifi' },
                      { icon: <Coffee size={16} />, label: 'Breakfast', value: 'breakfast' },
                      { icon: <ParkingSquare size={16} />, label: 'Parking', value: 'parking' }
                    ].map(({ icon, label, value }) => (
                      <label key={label} className="flex items-center space-x-2 cursor-pointer group">
                        <input 
                          type="checkbox" 
                          className="rounded text-slate-600 focus:ring-slate-500"
                          checked={filters.amenities.includes(value)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setFilters({ ...filters, amenities: [...filters.amenities, value] });
                            } else {
                              setFilters({ ...filters, amenities: filters.amenities.filter(a => a !== value) });
                            }
                          }}
                        />
                        <span className="flex items-center text-sm text-slate-600 group-hover:text-slate-900">
                          {icon}
                          <span className="ml-2">{label}</span>
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Clear Filters Button */}
                <button
                  onClick={() => setFilters({ priceRange: [0, 500], starRatings: [], amenities: [] })}
                  className="w-full mt-4 px-4 py-2 border-2 border-slate-300 rounded-xl font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
                >
                  Clear All Filters
                </button>
              </div>
            </div>
          )}

          {/* Hotel Results */}
          <div className={showFilters ? 'lg:col-span-2' : 'lg:col-span-3'}>
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 size={32} className="animate-spin text-slate-600" />
                <span className="ml-3 text-slate-600">Loading hotels...</span>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
                  <p className="text-red-800 font-semibold mb-2">Error loading hotels</p>
                  <p className="text-red-600 text-sm">{error}</p>
                  <button
                    onClick={loadHotels}
                    className="mt-4 btn-secondary px-4 py-2"
                  >
                    Try Again
                  </button>
                </div>
              </div>
            ) : hotels.length === 0 ? (
              <div className="text-center py-12">
                <Hotel className="mx-auto text-slate-400 mb-4" size={48} />
                <p className="text-slate-600 text-lg">No hotels found. Try adjusting your search criteria.</p>
                <button
                  onClick={loadHotels}
                  className="mt-4 btn-secondary px-4 py-2"
                >
                  Reload Hotels
                </button>
              </div>
            ) : filteredHotels.length === 0 ? (
              <div className="text-center py-12">
                <Hotel className="mx-auto text-slate-400 mb-4" size={48} />
                <p className="text-slate-600 text-lg">No hotels match your filters. Try adjusting your filter criteria.</p>
                <button
                  onClick={() => setFilters({ priceRange: [0, 500], starRatings: [], amenities: [] })}
                  className="mt-4 btn-secondary px-4 py-2"
                >
                  Clear All Filters
                </button>
              </div>
            ) : (
            <div className="space-y-4">
                {filteredHotels.map((hotel, index) => (
                  <HotelCard 
                    key={hotel.id || `hotel-${index}`} 
                    hotel={hotel} 
                    delay={index * 100}
                    onViewDetails={handleViewDetails}
                    isLoading={detailsLoading}
                  />
              ))}
            </div>
            )}
          </div>
        </div>
      </div>

      {/* Hotel Details Modal */}
      {showDetailsModal && selectedHotel && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto animate-scale-in">
            <div className="p-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-slate-900">Hotel Details</h2>
                <button
                  onClick={handleCloseDetails}
                  className="text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <X size={24} />
                </button>
              </div>

              {/* Hotel Image */}
              <div className="relative aspect-video bg-gradient-to-br from-slate-300 to-slate-400 rounded-xl mb-6 overflow-hidden">
                <div
                  className="absolute inset-0 bg-cover bg-center"
                  style={{ 
                    backgroundImage: `url(${getHotelImage(selectedHotel.hotel_name || '', selectedHotel.city || '', selectedHotel.hotel_id)})`, 
                    backgroundColor: '#64748b' 
                  }}
                />
              </div>

              {/* Hotel Info */}
              <div className="space-y-6">
                <div>
                  <h3 className="text-3xl font-bold text-slate-900 mb-2">{selectedHotel.hotel_name}</h3>
                  <div className="flex items-center text-slate-600 mb-4">
                    <MapPin size={18} className="mr-2" />
                    <span>{selectedHotel.address}, {selectedHotel.city}, {selectedHotel.state} {selectedHotel.zip_code}</span>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <Star
                          key={i}
                          className={`w-5 h-5 ${
                            i < (selectedHotel.star_rating || 0)
                              ? 'fill-yellow-400 text-yellow-400'
                              : 'text-slate-300'
                          }`}
                        />
                      ))}
                      <span className="ml-2 text-slate-600">({selectedHotel.star_rating || 0} stars)</span>
                    </div>
                    {selectedHotel.rating && (
                      <div className="flex items-center">
                        <Star className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                        <span className="ml-2 font-semibold text-slate-900">{selectedHotel.rating.toFixed(1)}</span>
                        {selectedHotel.total_reviews && (
                          <span className="ml-1 text-slate-600">({selectedHotel.total_reviews} reviews)</span>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {selectedHotel.description && (
                  <div>
                    <h4 className="text-lg font-semibold text-slate-900 mb-2">Description</h4>
                    <p className="text-slate-600">{selectedHotel.description}</p>
                  </div>
                )}

                {/* Amenities */}
                {selectedHotel.amenities && (
                  <div>
                    <h4 className="text-lg font-semibold text-slate-900 mb-3">Amenities</h4>
                    <div className="flex flex-wrap gap-2">
                      {(() => {
                        let amenitiesList: string[] = [];
                        if (typeof selectedHotel.amenities === 'string') {
                          amenitiesList = String(selectedHotel.amenities).includes(',') 
                            ? String(selectedHotel.amenities).split(',').map((a: string) => a.trim())
                            : [String(selectedHotel.amenities)];
                        } else if (Array.isArray(selectedHotel.amenities)) {
                          amenitiesList = selectedHotel.amenities;
                        }
                        return amenitiesList.map((amenity, idx) => (
                          <span
                            key={amenity || `amenity-${idx}`}
                            className="inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium bg-blue-50 text-blue-700 border border-blue-200"
                          >
                            {amenity}
                          </span>
                        ));
                      })()}
                    </div>
                  </div>
                )}

                {/* Contact Information */}
                <div className="grid md:grid-cols-2 gap-4 pt-4 border-t border-slate-200">
                  {selectedHotel.phone_number && (
                    <div className="flex items-center text-slate-600">
                      <Phone size={18} className="mr-3 text-slate-400" />
                      <span>{selectedHotel.phone_number}</span>
                    </div>
                  )}
                  {selectedHotel.email && (
                    <div className="flex items-center text-slate-600">
                      <Mail size={18} className="mr-3 text-slate-400" />
                      <span>{selectedHotel.email}</span>
                    </div>
                  )}
                  {selectedHotel.website && (
                    <div className="flex items-center text-blue-600">
                      <Globe size={18} className="mr-3" />
                      <a href={selectedHotel.website} target="_blank" rel="noopener noreferrer" className="hover:underline">
                        Visit Website
                      </a>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex items-center justify-end space-x-4 pt-4 border-t border-slate-200">
                  <button
                    onClick={handleCloseDetails}
                    className="px-6 py-3 border-2 border-slate-300 rounded-xl font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
                  >
                    Close
                  </button>
                  <button 
                    onClick={handleBookNow}
                    className="btn-primary px-6 py-3"
                    disabled={!searchParams.checkIn || !searchParams.checkOut}
                  >
                    <span>Book Now</span>
                    <ArrowRight size={16} className="ml-2 inline" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Payment Modal */}
      {showPayment && bookingId && booking && (
        <PaymentModal
          bookingId={bookingId}
          bookingType="hotel"
          amount={typeof booking.total_price === 'number' ? booking.total_price : parseFloat(booking.total_price?.toString() || '0')}
          isOpen={showPayment}
          onClose={() => {
            setShowPayment(false);
            setBooking(null);
            setBookingId(null);
          }}
          onSuccess={handlePaymentSuccess}
        />
      )}

      {/* Hotel Booking Modal */}
      {showBookingModal && selectedHotel && !showPayment && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full animate-scale-in">
            <div className="p-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-slate-900 flex items-center">
                  <Hotel className="mr-2" size={24} />
                  Confirm Your Hotel Booking
                </h2>
                <button
                  onClick={handleCloseDetails}
                  className="text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <X size={24} />
                </button>
              </div>

              {/* Hotel Details */}
              <div className="mb-6">
                <h3 className="text-xl font-semibold text-slate-900 mb-2">{selectedHotel.hotel_name}</h3>
                <div className="flex items-center text-slate-600 mb-4">
                  <MapPin size={16} className="mr-2" />
                  <span>{selectedHotel.city}, {selectedHotel.state}</span>
                </div>
              </div>

              {/* Booking Details - Editable */}
              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Check-in Date</label>
                  <input
                    type="date"
                    value={bookingParams.checkIn}
                    min={new Date().toISOString().split('T')[0]}
                    onChange={(e) => {
                      const newCheckIn = e.target.value;
                      setBookingParams({ ...bookingParams, checkIn: newCheckIn });
                      // Auto-adjust check-out if it's before new check-in
                      if (bookingParams.checkOut && new Date(bookingParams.checkOut) <= new Date(newCheckIn)) {
                        const nextDay = new Date(newCheckIn);
                        nextDay.setDate(nextDay.getDate() + 1);
                        setBookingParams({ ...bookingParams, checkIn: newCheckIn, checkOut: nextDay.toISOString().split('T')[0] });
                      } else {
                        setBookingParams({ ...bookingParams, checkIn: newCheckIn });
                      }
                      setBookingError(null);
                    }}
                    className="w-full px-4 py-2 border-2 border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Check-out Date</label>
                  <input
                    type="date"
                    value={bookingParams.checkOut}
                    min={bookingParams.checkIn ? new Date(new Date(bookingParams.checkIn).getTime() + 24 * 60 * 60 * 1000).toISOString().split('T')[0] : new Date().toISOString().split('T')[0]}
                    onChange={(e) => {
                      const newCheckOut = e.target.value;
                      if (bookingParams.checkIn && new Date(newCheckOut) <= new Date(bookingParams.checkIn)) {
                        setBookingError('Check-out date must be after check-in date');
                        return;
                      }
                      setBookingParams({ ...bookingParams, checkOut: newCheckOut });
                      setBookingError(null);
                    }}
                    className={`w-full px-4 py-2 border-2 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      bookingParams.checkOut && bookingParams.checkIn && new Date(bookingParams.checkOut) <= new Date(bookingParams.checkIn)
                        ? 'border-red-500'
                        : 'border-slate-300'
                    }`}
                  />
                  {bookingParams.checkOut && bookingParams.checkIn && new Date(bookingParams.checkOut) <= new Date(bookingParams.checkIn) && (
                    <p className="text-xs text-red-600 mt-1">Check-out must be after check-in</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Number of Guests</label>
                  <input
                    type="number"
                    min="1"
                    max="20"
                    value={bookingParams.guests}
                    onChange={(e) => {
                      const guests = e.target.value;
                      setBookingParams({ ...bookingParams, guests });
                      setBookingError(null);
                    }}
                    className="w-full px-4 py-2 border-2 border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Number of Rooms</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={bookingParams.rooms}
                    onChange={(e) => {
                      const rooms = e.target.value;
                      setBookingParams({ ...bookingParams, rooms });
                      setBookingError(null);
                    }}
                    className="w-full px-4 py-2 border-2 border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  {parseInt(bookingParams.guests) > (parseInt(bookingParams.rooms) || 1) * 4 && (
                    <p className="text-xs text-red-600 mt-1">
                      Too many guests for {bookingParams.rooms} room(s). Maximum {(parseInt(bookingParams.rooms) || 1) * 4} guests allowed.
                    </p>
                  )}
                </div>
                <div className="flex justify-between items-center py-3 border-t border-slate-200">
                  <span className="text-slate-600">Total Nights</span>
                  <span className="font-semibold text-slate-900">
                    {bookingParams.checkIn && bookingParams.checkOut
                      ? Math.ceil((new Date(bookingParams.checkOut).getTime() - new Date(bookingParams.checkIn).getTime()) / (1000 * 60 * 60 * 24))
                      : '0'}
                  </span>
                </div>
              </div>

              {/* Booking For */}
              {user && (
                <div className="bg-slate-50 rounded-lg p-4 mb-6">
                  <p className="text-sm text-slate-600 mb-1">Booking for</p>
                  <p className="font-semibold text-slate-900">{user.first_name} {user.last_name}</p>
                  <p className="text-sm text-slate-600">{user.email}</p>
                </div>
              )}

              {/* Error Message */}
              {bookingError && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-xl mb-6">
                  <p>{bookingError}</p>
                </div>
              )}

              {/* Success Message */}
              {bookingSuccess && bookingId && (
                <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-xl mb-6">
                  <p className="font-semibold">Booking confirmed!</p>
                  <p className="text-sm">Booking ID: {bookingId}</p>
                </div>
              )}

              {/* Total Price */}
              <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl p-6 mb-6">
                <p className="text-sm mb-2">Total Price</p>
                <p className="text-3xl font-bold">
                  {bookingParams.checkIn && bookingParams.checkOut
                    ? `$${(150 * Math.ceil((new Date(bookingParams.checkOut).getTime() - new Date(bookingParams.checkIn).getTime()) / (1000 * 60 * 60 * 24)) * (parseInt(bookingParams.rooms) || 1)).toFixed(2)}`
                    : '$0.00'}
                </p>
                <p className="text-sm mt-2 opacity-90">
                  {bookingParams.checkIn && bookingParams.checkOut
                    ? `$${150} × ${Math.ceil((new Date(bookingParams.checkOut).getTime() - new Date(bookingParams.checkIn).getTime()) / (1000 * 60 * 60 * 24))} nights × ${parseInt(bookingParams.rooms) || 1} room(s)`
                    : 'Select dates to see price'}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end space-x-4">
                <button
                  onClick={handleCloseDetails}
                  className="px-6 py-3 border-2 border-slate-300 rounded-xl font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
                  disabled={bookingLoading}
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmBooking}
                  className="btn-primary px-6 py-3 flex items-center"
                  disabled={bookingLoading || bookingSuccess}
                >
                  {bookingLoading ? (
                    <>
                      <Loader2 size={16} className="mr-2 animate-spin" />
                      <span>Processing...</span>
                    </>
                  ) : bookingSuccess ? (
                    <>
                      <CheckCircle size={16} className="mr-2" />
                      <span>Confirmed</span>
                    </>
                  ) : (
                    <>
                      <span>Confirm Booking</span>
                      <ArrowRight size={16} className="ml-2" />
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

interface HotelCardProps {
  hotel: HotelListing;
  delay: number;
  onViewDetails: (hotelId: string) => void;
  isLoading?: boolean;
}

const HotelCard: React.FC<HotelCardProps> = ({ hotel, delay, onViewDetails, isLoading = false }) => (
  <div
    className="card-interactive p-0 overflow-hidden animate-slide-up"
    style={{ animationDelay: `${delay}ms` }}
  >
    <div className="grid md:grid-cols-3 gap-0">
      {/* Hotel Image */}
      <div className="md:col-span-1 relative aspect-[4/3] md:aspect-auto bg-gradient-to-br from-slate-300 to-slate-400">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${hotel.image})`, backgroundColor: '#64748b' }}
        />
        <div className="absolute top-4 left-4 glass px-3 py-1.5 rounded-lg text-sm font-bold text-slate-900">
          <Star className="w-4 h-4 inline fill-yellow-400 text-yellow-400 mr-1" />
          {hotel.rating}
        </div>
      </div>

      {/* Hotel Info */}
      <div className="md:col-span-2 p-6 flex flex-col justify-between">
        <div>
          <div className="flex items-start justify-between mb-3">
            <div>
              <h3 className="text-xl font-bold text-slate-900 mb-1">{hotel.name}</h3>
              <div className="flex items-center text-slate-600 text-sm">
                <MapPin size={14} className="mr-1" />
                <span>{hotel.location}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2 mb-4 text-sm">
            <div className="flex">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star
                  key={i}
                  className={`w-4 h-4 ${
                    i < Math.floor(hotel.rating)
                      ? 'fill-yellow-400 text-yellow-400'
                      : 'text-slate-300'
                  }`}
                />
              ))}
            </div>
            <span className="text-slate-600">({hotel.reviews} reviews)</span>
          </div>

          <div className="mb-4">
            <span className="text-sm font-medium text-slate-700">{hotel.roomType}</span>
            {hotel.available_rooms !== undefined && (
              <div className="mt-2">
                <span className={`inline-flex items-center px-3 py-1 rounded-lg text-xs font-semibold ${
                  hotel.available_rooms > 5
                    ? 'bg-green-100 text-green-800 border border-green-300'
                    : hotel.available_rooms > 0
                      ? 'bg-yellow-100 text-yellow-800 border border-yellow-300'
                      : 'bg-red-100 text-red-800 border border-red-300'
                }`}>
                  {hotel.available_rooms > 0
                    ? `${hotel.available_rooms} room${hotel.available_rooms !== 1 ? 's' : ''} available`
                    : 'No rooms available'
                  }
                </span>
              </div>
            )}
          </div>

          {hotel.amenities && hotel.amenities.length > 0 && (
          <div className="flex flex-wrap gap-2">
              {hotel.amenities.map((amenity, idx) => (
              <span
                  key={amenity || `amenity-${idx}`}
                className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200"
              >
                {amenity}
              </span>
            ))}
          </div>
          )}
        </div>

        <div className="flex items-end justify-between mt-6 pt-4 border-t border-slate-200">
          <div>
            <div className="flex items-center text-slate-600 text-sm mb-1">
              <DollarSign size={14} />
              <span>per night</span>
            </div>
            <div className="text-3xl font-bold text-slate-800">${hotel.price}</div>
            <div className="text-xs text-slate-500">includes taxes & fees</div>
          </div>
          <button 
            onClick={() => onViewDetails(hotel.id)}
            disabled={isLoading}
            className="btn-primary px-6 py-3 whitespace-nowrap group disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <Loader2 size={16} className="ml-2 inline animate-spin" />
                <span>Loading...</span>
              </>
            ) : (
              <>
            <span>View Details</span>
            <ArrowRight size={16} className="ml-2 inline group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  </div>
);

export default HotelsPage;
