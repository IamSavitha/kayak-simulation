import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Car, MapPin, Calendar, Search, Filter, Star, Users, Fuel, Gauge, ArrowRight, DollarSign, Luggage, X, Loader2, CheckCircle } from 'lucide-react';
import { searchCars, Car as CarAPI, CarSearchParams } from '../api/cars';
import { useAuth } from '../context/AuthContext';
import { createBooking, BookingCreate } from '../api/bookings';
import { useNavigate } from 'react-router-dom';
import PaymentModal from '../components/PaymentModal';
import { BillingResponse } from '../api/billing';

interface CarRental {
  id: string;
  name: string;
  company: string;
  type: string;
  transmission: string;
  passengers: number;
  luggage: number;
  fuelType: string;
  price: number;
  rating: number;
  reviews: number;
  image: string;
  features: string[];
  city: string;
  state: string;
}

const CarsPage: React.FC = () => {
  const { user, token, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [urlParams] = useSearchParams();
  const [showFilters, setShowFilters] = useState(false);
  const [cars, setCars] = useState<CarRental[]>([]);
  const [filteredCars, setFilteredCars] = useState<CarRental[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCar, setSelectedCar] = useState<CarRental | null>(null);
  const [highlightedCarId, setHighlightedCarId] = useState<string | null>(null);
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [bookingLoading, setBookingLoading] = useState(false);
  const [bookingError, setBookingError] = useState<string | null>(null);
  const [bookingSuccess, setBookingSuccess] = useState(false);
  const [bookingId, setBookingId] = useState<string | null>(null);
  const [showPayment, setShowPayment] = useState(false);
  const [booking, setBooking] = useState<any>(null);
  const [searchParams, setSearchParams] = useState({
    city: '',
    pickupDate: '',
    dropoffDate: '',
    carType: ''
  });
  const [filters, setFilters] = useState({
    priceRange: [0, 200] as [number, number],
    carTypes: [] as string[],
    transmission: [] as string[],
    fuelType: [] as string[]
  });

  // Convert API car to display format
  const convertCar = (car: CarAPI): CarRental => {
    // Generate a deterministic image URL based on car make/model
    const imageMap: { [key: string]: string } = {
      'toyota': 'https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=400&h=300&fit=crop',
      'honda': 'https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=400&h=300&fit=crop',
      'ford': 'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=400&h=300&fit=crop',
      'chevrolet': 'https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=400&h=300&fit=crop',
      'nissan': 'https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=400&h=300&fit=crop',
      'bmw': 'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=400&h=300&fit=crop',
      'mercedes': 'https://images.unsplash.com/photo-1617531653332-bd46c24f2068?w=400&h=300&fit=crop',
      'audi': 'https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=400&h=300&fit=crop',
      'tesla': 'https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=400&h=300&fit=crop',
    };
    
    const makeLower = (car.make || '').toLowerCase();
    const defaultImage = 'https://images.unsplash.com/photo-1492144534655-ae79c475cae3?w=400&h=300&fit=crop';
    const imageUrl = imageMap[makeLower] || defaultImage;
    
    return {
      id: car.car_id,
      name: `${car.make} ${car.model}`,
      company: car.provider_name,
      type: car.car_type || 'Standard',
      transmission: car.transmission_type || 'Automatic',
      passengers: car.seats || 5,
      luggage: 2, // Default, not in API
      fuelType: 'Gasoline', // Default, not in API
      price: Number(car.daily_rental_price) || 0, // Fix: use daily_rental_price from API
      rating: car.rating || 4.0,
      reviews: car.total_reviews || 0,
      image: imageUrl,
      features: car.features || ['GPS', 'Bluetooth'],
      city: car.city || '',
      state: car.state || ''
    };
  };

  // Load cars on mount
  useEffect(() => {
    loadCars();
  }, []);

  // Apply filters whenever cars or filters change
  useEffect(() => {
    let filtered = [...cars];

    // Price filter
    filtered = filtered.filter(car => 
      car.price >= filters.priceRange[0] && car.price <= filters.priceRange[1]
    );

    // Car type filter
    if (filters.carTypes.length > 0) {
      filtered = filtered.filter(car => 
        filters.carTypes.some(type => car.type.toLowerCase() === type.toLowerCase())
      );
    }

    // Transmission filter
    if (filters.transmission.length > 0) {
      filtered = filtered.filter(car => 
        filters.transmission.some(trans => car.transmission.toLowerCase() === trans.toLowerCase())
      );
    }

    // Fuel type filter (note: fuelType is hardcoded to 'Gasoline' in convertCar, so this may not work until we get real data)
    if (filters.fuelType.length > 0) {
      filtered = filtered.filter(car => 
        filters.fuelType.some(fuel => car.fuelType.toLowerCase() === fuel.toLowerCase())
      );
    }

    setFilteredCars(filtered);
  }, [cars, filters]);

  // Handle car_id from URL (when coming from deals page)
  useEffect(() => {
    const carId = urlParams.get('car_id');
    if (carId && filteredCars.length > 0) {
      setHighlightedCarId(carId);
      
      // Find and scroll to the car
      setTimeout(() => {
        const element = document.getElementById(`car-${carId}`);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 300);
      
      // Clear highlight after 3 seconds
      setTimeout(() => {
        setHighlightedCarId(null);
      }, 3000);
    }
  }, [urlParams, filteredCars]);

  const loadCars = async () => {
    setLoading(true);
    setError(null);
    try {
      const params: CarSearchParams = {
        page: 1,
        page_size: 1000 // Show all cars
      };
      
      if (searchParams.city) {
        params.city = searchParams.city;
      }
      if (searchParams.carType) {
        params.car_type = searchParams.carType;
      }

      const response = await searchCars(params);
      // Filter out unavailable cars
      const availableCars = response.cars.filter(car => car.is_available === true);
      const convertedCars = availableCars.map(convertCar);
      setCars(convertedCars);
      setFilteredCars(convertedCars); // Initialize filtered cars
    } catch (err: any) {
      setError(err.message || 'Failed to load cars');
      console.error('Error loading cars:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    // Validate dates before searching
    if (searchParams.pickupDate && searchParams.dropoffDate) {
      if (new Date(searchParams.dropoffDate) <= new Date(searchParams.pickupDate)) {
        setError('Drop-off date must be after pick-up date');
        return;
      }
    }
    setError(null);
    loadCars();
  };

  const handleReserve = (car: CarRental) => {
    if (!isAuthenticated || !user || !token) {
      alert('Please log in to reserve a car');
      setTimeout(() => navigate('/login'), 2000);
      return;
    }
    setSelectedCar(car);
    setShowBookingModal(true);
    setBookingError(null);
    setBookingSuccess(false);
  };

  const handleBooking = async () => {
    if (!selectedCar || !user || !token) return;

    if (!searchParams.pickupDate || !searchParams.dropoffDate) {
      setBookingError('Please select pickup and drop-off dates');
      return;
    }

    setBookingLoading(true);
    setBookingError(null);

    try {
      const pickupDate = new Date(searchParams.pickupDate);
      const dropoffDate = new Date(searchParams.dropoffDate);

      if (dropoffDate <= pickupDate) {
        setBookingError('Drop-off date must be after pickup date');
        setBookingLoading(false);
        return;
      }

      const bookingData: BookingCreate = {
        user_id: user.user_id,
        booking_type: 'car',
        listing_id: selectedCar.id,
        check_in_date: pickupDate.toISOString(),
        check_out_date: dropoffDate.toISOString(),
      };

      const bookingResponse = await createBooking(bookingData, token);
      setBookingId(bookingResponse.booking_id);
      setBooking(bookingResponse);
      // Show payment modal instead of success immediately
      setShowPayment(true);
    } catch (err: any) {
      setBookingError(err.message || 'Failed to create booking. Please try again.');
    } finally {
      setBookingLoading(false);
    }
  };

  const handleCloseModal = () => {
    if (!bookingLoading) {
      setShowBookingModal(false);
      setSelectedCar(null);
      setBookingError(null);
      setBookingSuccess(false);
      setBookingId(null);
      setShowPayment(false);
      setBooking(null);
    }
  };

  const handlePaymentSuccess = (billing: BillingResponse) => {
    setBookingSuccess(true);
    setShowPayment(false);
    setShowBookingModal(false);
    setSelectedCar(null);
    setBooking(null);
    setBookingId(null);
    // Optionally navigate to bookings page to see the booking with billing info
    setTimeout(() => {
      navigate('/bookings');
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30">
      {/* Search Header */}
      <div className="bg-gradient-to-r from-slate-700 to-slate-800 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-8 animate-slide-down">Rent a Car</h1>

          {/* Search Form */}
          <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-6 border-2 border-white/40 shadow-2xl animate-scale-in">
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700">Pick-up Location</label>
                <div className="flex items-center border-2 border-slate-300 rounded-xl px-4 py-3 bg-white hover:border-slate-500 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200 transition-all shadow-sm">
                  <MapPin className="text-slate-600 mr-3 flex-shrink-0" size={18} />
                  <input
                    type="text"
                    placeholder="City, State"
                    value={searchParams.city}
                    onChange={(e) => setSearchParams({ ...searchParams, city: e.target.value })}
                    className="w-full outline-none text-sm font-semibold text-slate-900 placeholder:text-slate-400 bg-transparent"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700">Pick-up Date</label>
                <div className={`flex items-center border-2 rounded-xl px-4 py-3 bg-white transition-all shadow-sm ${
                  searchParams.dropoffDate && searchParams.pickupDate && new Date(searchParams.dropoffDate) <= new Date(searchParams.pickupDate)
                    ? 'border-red-500 focus-within:border-red-500 focus-within:ring-2 focus-within:ring-red-200'
                    : 'border-slate-300 hover:border-slate-500 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200'
                }`}>
                  <Calendar className="text-slate-600 mr-3 flex-shrink-0" size={18} />
                  <input
                    type="date"
                    value={searchParams.pickupDate}
                    min={new Date().toISOString().split('T')[0]}
                    onChange={(e) => {
                      const newPickupDate = e.target.value;
                      setSearchParams({ ...searchParams, pickupDate: newPickupDate });
                      // If dropoff date is before or equal to new pickup date, clear it
                      if (searchParams.dropoffDate && new Date(searchParams.dropoffDate) <= new Date(newPickupDate)) {
                        setSearchParams({ ...searchParams, pickupDate: newPickupDate, dropoffDate: '' });
                      }
                    }}
                    className="w-full outline-none text-sm font-semibold text-slate-900 placeholder:text-slate-400 bg-transparent [color-scheme:light]"
                  />
                </div>
                {searchParams.dropoffDate && searchParams.pickupDate && new Date(searchParams.dropoffDate) <= new Date(searchParams.pickupDate) && (
                  <p className="text-xs text-red-600 mt-1">Drop-off date must be after pick-up date</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700">Drop-off Date</label>
                <div className={`flex items-center border-2 rounded-xl px-4 py-3 bg-white transition-all shadow-sm ${
                  searchParams.dropoffDate && searchParams.pickupDate && new Date(searchParams.dropoffDate) <= new Date(searchParams.pickupDate)
                    ? 'border-red-500 focus-within:border-red-500 focus-within:ring-2 focus-within:ring-red-200'
                    : 'border-slate-300 hover:border-slate-500 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200'
                }`}>
                  <Calendar className="text-slate-600 mr-3 flex-shrink-0" size={18} />
                  <input
                    type="date"
                    value={searchParams.dropoffDate}
                    min={searchParams.pickupDate ? new Date(new Date(searchParams.pickupDate).getTime() + 24 * 60 * 60 * 1000).toISOString().split('T')[0] : new Date().toISOString().split('T')[0]}
                    onChange={(e) => {
                      const newDropoffDate = e.target.value;
                      // Validate that dropoff is after pickup
                      if (searchParams.pickupDate && new Date(newDropoffDate) <= new Date(searchParams.pickupDate)) {
                        // Don't update if invalid
                        return;
                      }
                      setSearchParams({ ...searchParams, dropoffDate: newDropoffDate });
                    }}
                    className="w-full outline-none text-sm font-semibold text-slate-900 placeholder:text-slate-400 bg-transparent [color-scheme:light]"
                  />
                </div>
                {searchParams.dropoffDate && searchParams.pickupDate && new Date(searchParams.dropoffDate) <= new Date(searchParams.pickupDate) && (
                  <p className="text-xs text-red-600 mt-1">Drop-off date must be after pick-up date</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700">Car Type</label>
                <div className="flex items-center border-2 border-slate-300 rounded-xl px-4 py-3 bg-white hover:border-slate-500 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200 transition-all shadow-sm">
                  <Car className="text-slate-600 mr-3 flex-shrink-0" size={18} />
                  <select 
                    value={searchParams.carType}
                    onChange={(e) => setSearchParams({ ...searchParams, carType: e.target.value })}
                    className="w-full outline-none text-sm font-semibold text-slate-900 bg-transparent appearance-none cursor-pointer"
                  >
                    <option value="">All Types</option>
                    <option value="sedan">Sedan</option>
                    <option value="suv">SUV</option>
                    <option value="luxury">Luxury</option>
                    <option value="compact">Compact</option>
                  </select>
                </div>
              </div>
            </div>

            <button 
              onClick={handleSearch}
              className="w-full mt-6 bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 font-bold py-4 px-6 rounded-xl flex items-center justify-center space-x-3 transition-all duration-200 shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] group"
            >
              <Search size={20} className="group-hover:rotate-90 transition-transform duration-300" />
              <span className="text-base">Search Cars</span>
              <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform duration-300" />
            </button>
          </div>
        </div>
      </div>

      {/* Results Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold text-slate-900">Available Cars</h2>
            {loading ? (
              <p className="text-slate-600 mt-1">Loading...</p>
            ) : error ? (
              <p className="text-red-600 mt-1">{error}</p>
            ) : (
              <p className="text-slate-600 mt-1">
                {filteredCars.length} of {cars.length} vehicles found
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

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-slate-600">Loading cars...</p>
          </div>
        )}

        {!loading && !error && cars.length === 0 && (
          <div className="text-center py-12">
            <Car className="mx-auto text-slate-400 mb-4" size={48} />
            <p className="text-slate-600 text-lg">No cars found. Try adjusting your search criteria.</p>
          </div>
        )}

        {!loading && !error && cars.length > 0 && filteredCars.length === 0 && (
          <div className="text-center py-12">
            <Car className="mx-auto text-slate-400 mb-4" size={48} />
            <p className="text-slate-600 text-lg">No cars match your filters. Try adjusting your filter criteria.</p>
            <button
              onClick={() => setFilters({ priceRange: [0, 200], carTypes: [], transmission: [], fuelType: [] })}
              className="mt-4 btn-secondary px-4 py-2"
            >
              Clear All Filters
            </button>
          </div>
        )}

        {!loading && !error && filteredCars.length > 0 && (
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Filters Sidebar */}
          {showFilters && (
            <div className="lg:col-span-1 animate-slide-up">
              <div className="card p-6 sticky top-24">
                <h3 className="text-lg font-bold text-slate-900 mb-6">Filter Results</h3>

                {/* Price Range */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Price Per Day</h4>
                    <div className="space-y-3">
                      <div>
                        <label className="text-xs text-slate-600 mb-1 block">Min: ${filters.priceRange[0]}</label>
                        <input 
                          type="range" 
                          min="0" 
                          max="200" 
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
                          max="200" 
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

                {/* Car Type */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Car Type</h4>
                  <div className="space-y-2">
                    {['Sedan', 'SUV', 'Luxury', 'Compact'].map((type) => (
                      <label key={type} className="flex items-center space-x-2 cursor-pointer group">
                          <input 
                            type="checkbox" 
                            className="rounded text-blue-600 focus:ring-blue-500"
                            checked={filters.carTypes.includes(type)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setFilters({ ...filters, carTypes: [...filters.carTypes, type] });
                              } else {
                                setFilters({ ...filters, carTypes: filters.carTypes.filter(t => t !== type) });
                              }
                            }}
                          />
                        <span className="text-sm text-slate-600 group-hover:text-slate-900">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Transmission */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Transmission</h4>
                  <div className="space-y-2">
                    {['Automatic', 'Manual'].map((trans) => (
                      <label key={trans} className="flex items-center space-x-2 cursor-pointer group">
                          <input 
                            type="checkbox" 
                            className="rounded text-blue-600 focus:ring-blue-500"
                            checked={filters.transmission.includes(trans)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setFilters({ ...filters, transmission: [...filters.transmission, trans] });
                              } else {
                                setFilters({ ...filters, transmission: filters.transmission.filter(t => t !== trans) });
                              }
                            }}
                          />
                        <span className="text-sm text-slate-600 group-hover:text-slate-900">{trans}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Fuel Type */}
                  <div className="mb-6">
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Fuel Type</h4>
                  <div className="space-y-2">
                    {['Gasoline', 'Electric', 'Hybrid'].map((fuel) => (
                      <label key={fuel} className="flex items-center space-x-2 cursor-pointer group">
                          <input 
                            type="checkbox" 
                            className="rounded text-blue-600 focus:ring-blue-500"
                            checked={filters.fuelType.includes(fuel)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setFilters({ ...filters, fuelType: [...filters.fuelType, fuel] });
                              } else {
                                setFilters({ ...filters, fuelType: filters.fuelType.filter(f => f !== fuel) });
                              }
                            }}
                          />
                        <span className="text-sm text-slate-600 group-hover:text-slate-900">{fuel}</span>
                      </label>
                    ))}
                  </div>
                  </div>

                  {/* Clear Filters Button */}
                  <button
                    onClick={() => setFilters({ priceRange: [0, 200], carTypes: [], transmission: [], fuelType: [] })}
                    className="w-full mt-4 px-4 py-2 border-2 border-slate-300 rounded-xl font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
                  >
                    Clear All Filters
                  </button>
              </div>
            </div>
          )}

          {/* Car Results */}
          <div className={showFilters ? 'lg:col-span-2' : 'lg:col-span-3'}>
            <div className="grid md:grid-cols-2 gap-6">
                {filteredCars.map((car, index) => (
                  <CarCard 
                    key={car.id} 
                    car={car} 
                    delay={index * 100}
                    onReserve={() => handleReserve(car)}
                    isHighlighted={highlightedCarId === car.id}
                  />
              ))}
            </div>
          </div>
        </div>
        )}

        {/* Payment Modal */}
        {showPayment && bookingId && booking && (
          <PaymentModal
            bookingId={bookingId}
            bookingType="car"
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

        {/* Booking Modal */}
        {showBookingModal && selectedCar && !showPayment && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto animate-scale-in">
              <div className="p-6">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-slate-900">Reserve Car</h2>
                  <button
                    onClick={handleCloseModal}
                    disabled={bookingLoading}
                    className="text-slate-400 hover:text-slate-600 transition-colors disabled:opacity-50"
                  >
                    <X size={24} />
                  </button>
                </div>

                {bookingSuccess ? (
                  <div className="text-center py-8">
                    <CheckCircle className="mx-auto text-green-500 mb-4" size={64} />
                    <h3 className="text-2xl font-bold text-slate-900 mb-2">Booking Confirmed!</h3>
                    <p className="text-slate-600 mb-4">Your car reservation has been confirmed.</p>
                    <p className="text-sm text-slate-500">Booking ID: {bookingId}</p>
                    <button
                      onClick={handleCloseModal}
                      className="mt-6 btn-primary px-6 py-3"
                    >
                      Close
                    </button>
                  </div>
                ) : (
                  <>
                    {/* Car Details */}
                    <div className="bg-slate-50 rounded-xl p-6 mb-6">
                      <h3 className="text-lg font-bold text-slate-900 mb-4">Car Details</h3>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm text-slate-600">Vehicle</p>
                            <p className="font-semibold text-slate-900">{selectedCar.name}</p>
                          </div>
                          <div>
                            <p className="text-sm text-slate-600">Provider</p>
                            <p className="font-semibold text-slate-900">{selectedCar.company}</p>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm text-slate-600">Type</p>
                            <p className="font-semibold text-slate-900 capitalize">{selectedCar.type}</p>
                          </div>
                          <div>
                            <p className="text-sm text-slate-600">Transmission</p>
                            <p className="font-semibold text-slate-900">{selectedCar.transmission}</p>
                          </div>
                        </div>
                        {selectedCar.city && (
                          <div>
                            <p className="text-sm text-slate-600">Location</p>
                            <p className="font-semibold text-slate-900">{selectedCar.city}, {selectedCar.state}</p>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Date Selection */}
                    <div className="mb-6">
                      <h3 className="text-lg font-bold text-slate-900 mb-4">Rental Period</h3>
                      <div className="grid md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-semibold text-slate-700 mb-2">
                            <Calendar size={16} className="inline mr-2" />
                            Pickup Date
                          </label>
                          <input
                            type="date"
                            value={searchParams.pickupDate}
                            onChange={(e) => setSearchParams({ ...searchParams, pickupDate: e.target.value })}
                            min={new Date().toISOString().split('T')[0]}
                            className="w-full px-4 py-3 border-2 border-slate-300 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none [color-scheme:light]"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-semibold text-slate-700 mb-2">
                            <Calendar size={16} className="inline mr-2" />
                            Drop-off Date
                          </label>
                          <input
                            type="date"
                            value={searchParams.dropoffDate}
                            onChange={(e) => setSearchParams({ ...searchParams, dropoffDate: e.target.value })}
                            min={searchParams.pickupDate || new Date().toISOString().split('T')[0]}
                            className="w-full px-4 py-3 border-2 border-slate-300 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none [color-scheme:light]"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Price Calculation */}
                    {searchParams.pickupDate && searchParams.dropoffDate && (
                      <div className="bg-blue-50 rounded-xl p-4 mb-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm text-slate-600">Daily Rate</p>
                            <p className="text-2xl font-bold text-slate-900">${selectedCar.price.toFixed(2)}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm text-slate-600">
                              {Math.ceil((new Date(searchParams.dropoffDate).getTime() - new Date(searchParams.pickupDate).getTime()) / (1000 * 60 * 60 * 24))} days
                            </p>
                            <p className="text-2xl font-bold text-blue-600">
                              ${(selectedCar.price * Math.ceil((new Date(searchParams.dropoffDate).getTime() - new Date(searchParams.pickupDate).getTime()) / (1000 * 60 * 60 * 24))).toFixed(2)}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Error Message */}
                    {bookingError && (
                      <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                        <p className="text-red-800">{bookingError}</p>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="flex items-center justify-end space-x-4">
                      <button
                        onClick={handleCloseModal}
                        disabled={bookingLoading}
                        className="px-6 py-3 border-2 border-slate-300 rounded-xl font-semibold text-slate-700 hover:bg-slate-50 transition-colors disabled:opacity-50"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleBooking}
                        disabled={bookingLoading || !searchParams.pickupDate || !searchParams.dropoffDate}
                        className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-blue-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                      >
                        {bookingLoading ? (
                          <>
                            <Loader2 className="animate-spin" size={20} />
                            <span>Processing...</span>
                          </>
                        ) : (
                          <>
                            <DollarSign size={20} />
                            <span>Confirm Reservation</span>
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
      </div>
    </div>
  );
};

interface CarCardProps {
  car: CarRental;
  delay: number;
  onReserve: () => void;
  isHighlighted?: boolean;
}

const CarCard: React.FC<CarCardProps> = ({ car, delay, onReserve, isHighlighted }) => (
  <div
    id={`car-${car.id}`}
    className={`card-interactive p-0 overflow-hidden animate-slide-up ${isHighlighted ? 'ring-4 ring-blue-500 ring-offset-2' : ''}`}
    style={{ animationDelay: `${delay}ms` }}
  >
    {/* Car Image */}
    <div className="relative aspect-[16/10] bg-gradient-to-br from-slate-300 to-slate-400">
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{ backgroundImage: `url(${car.image})`, backgroundColor: '#64748b' }}
      />
      <div className="absolute top-4 left-4 bg-slate-700 text-white px-3 py-1.5 rounded-lg text-xs font-bold uppercase">
        {car.type}
      </div>
      <div className="absolute top-4 right-4 flex flex-col gap-2">
        <div className="glass px-3 py-1.5 rounded-lg text-sm font-bold text-slate-900">
        <Star className="w-4 h-4 inline fill-yellow-400 text-yellow-400 mr-1" />
          {car.rating.toFixed(1)}
        </div>
        <div className="bg-green-500 text-white px-3 py-1.5 rounded-lg text-xs font-bold uppercase">
          Available
        </div>
      </div>
    </div>

    {/* Car Info */}
    <div className="p-6">
      <div className="mb-4">
        <h3 className="text-xl font-bold text-slate-900 mb-1">{car.name}</h3>
        <div className="flex items-center text-sm text-slate-600">
          <span className="font-medium">{car.company}</span>
          {car.city && (
            <>
          <span className="mx-2">•</span>
              <span>{car.city}, {car.state}</span>
            </>
          )}
        </div>
        {car.reviews > 0 && (
          <div className="flex items-center text-sm text-slate-600 mt-1">
            <Star className="w-3 h-3 fill-yellow-400 text-yellow-400 mr-1" />
            ({car.reviews} reviews)
        </div>
        )}
      </div>

      {/* Specs */}
      <div className="grid grid-cols-2 gap-3 mb-4 pb-4 border-b border-slate-200">
        <div className="flex items-center text-sm text-slate-600">
          <Users size={16} className="mr-2 text-slate-600" />
          <span>{car.passengers} passengers</span>
        </div>
        <div className="flex items-center text-sm text-slate-600">
          <Luggage size={16} className="mr-2 text-slate-600" />
          <span>{car.luggage} bags</span>
        </div>
        <div className="flex items-center text-sm text-slate-600">
          <Gauge size={16} className="mr-2 text-slate-600" />
          <span>{car.transmission}</span>
        </div>
        <div className="flex items-center text-sm text-slate-600">
          <Fuel size={16} className="mr-2 text-slate-600" />
          <span>{car.fuelType}</span>
        </div>
      </div>

      {/* Features */}
      <div className="mb-4">
        <div className="flex flex-wrap gap-2">
          {car.features.map((feature) => (
            <span
              key={feature}
              className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-700"
            >
              {feature}
            </span>
          ))}
        </div>
      </div>

      {/* Price and Action */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-200">
        <div>
          <div className="flex items-center text-slate-600 text-xs mb-1">
            <DollarSign size={12} />
            <span>per day</span>
          </div>
          <div className="text-2xl font-bold text-slate-800">${car.price.toFixed(2)}</div>
        </div>
        <button 
          onClick={onReserve}
          className="btn-primary px-5 py-2.5 text-sm whitespace-nowrap group"
        >
          <span>Reserve</span>
          <ArrowRight size={14} className="ml-2 inline group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  </div>
);

export default CarsPage;
