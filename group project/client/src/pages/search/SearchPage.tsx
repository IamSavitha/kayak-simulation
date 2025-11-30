import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import { FaPlane, FaHotel, FaCar, FaStar, FaWifi, FaParking, FaSwimmingPool } from 'react-icons/fa';
import {
  HiLocationMarker,
  HiCalendar,
  HiAdjustments,
  HiSortDescending,
  HiSearch,
  HiUsers,
  HiRefresh,
  HiChevronLeft,
  HiChevronRight,
} from 'react-icons/hi';
import { flightService, hotelService, carService } from '../../services/api';

// Types
interface FlightResult {
  flight_id: string;
  airline: string;
  departure_airport: string;
  arrival_airport: string;
  departure_date_time: string;
  arrival_date_time: string;
  duration_minutes: number;
  flight_class: string;
  ticket_price: number;
  current_available_seats: number;
  flight_rating: number;
}

interface HotelResult {
  hotel_id: string;
  hotel_name: string;
  address: string;
  city: string;
  state: string;
  star_rating: number;
  price_per_night: number;
  amenities: string;
  hotel_rating: number;
  current_available_rooms: number;
}

interface CarResult {
  car_id: string;
  car_type: string;
  company_provider_name: string;
  model_and_year: string;
  transmission_type: string;
  number_of_seats: number;
  daily_rental_price: number;
  car_rating: number;
  availability_status: string;
}

// Search Form Components
const FlightSearchForm: React.FC<{ onSearch: (params: any) => void }> = ({ onSearch }) => {
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [departureDate, setDepartureDate] = useState('');
  const [flightClass, setFlightClass] = useState('');
  const [passengers, setPassengers] = useState(1);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch({
      origin: origin || undefined,
      destination: destination || undefined,
      departure_date: departureDate || undefined,
      flight_class: flightClass || undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="card p-6 mb-8">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div>
          <label className="label">From</label>
          <div className="relative">
            <FaPlane className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 w-4 h-4" />
            <input
              type="text"
              value={origin}
              onChange={(e) => setOrigin(e.target.value.toUpperCase())}
              placeholder="SFO"
              className="input pl-10"
              maxLength={5}
            />
          </div>
        </div>
        <div>
          <label className="label">To</label>
          <div className="relative">
            <HiLocationMarker className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 w-4 h-4" />
            <input
              type="text"
              value={destination}
              onChange={(e) => setDestination(e.target.value.toUpperCase())}
              placeholder="JFK"
              className="input pl-10"
              maxLength={5}
            />
          </div>
        </div>
        <div>
          <label className="label">Departure Date</label>
          <div className="relative">
            <HiCalendar className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 w-4 h-4" />
            <input
              type="date"
              value={departureDate}
              onChange={(e) => setDepartureDate(e.target.value)}
              className="input pl-10"
            />
          </div>
        </div>
        <div>
          <label className="label">Class</label>
          <select
            value={flightClass}
            onChange={(e) => setFlightClass(e.target.value)}
            className="input"
          >
            <option value="">Any Class</option>
            <option value="Economy">Economy</option>
            <option value="Business">Business</option>
            <option value="First">First</option>
          </select>
        </div>
        <div className="flex items-end">
          <button type="submit" className="btn-primary w-full">
            <HiSearch className="w-5 h-5 mr-2" />
            Search Flights
          </button>
        </div>
      </div>
    </form>
  );
};

const HotelSearchForm: React.FC<{ onSearch: (params: any) => void }> = ({ onSearch }) => {
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [checkIn, setCheckIn] = useState('');
  const [checkOut, setCheckOut] = useState('');
  const [minStars, setMinStars] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch({
      city: city || undefined,
      state: state || undefined,
      check_in_date: checkIn || undefined,
      check_out_date: checkOut || undefined,
      min_stars: minStars ? parseInt(minStars) : undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="card p-6 mb-8">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
        <div>
          <label className="label">City</label>
          <div className="relative">
            <HiLocationMarker className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 w-4 h-4" />
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              placeholder="New York"
              className="input pl-10"
            />
          </div>
        </div>
        <div>
          <label className="label">State</label>
          <input
            type="text"
            value={state}
            onChange={(e) => setState(e.target.value.toUpperCase())}
            placeholder="NY"
            className="input"
            maxLength={2}
          />
        </div>
        <div>
          <label className="label">Check-in</label>
          <input
            type="date"
            value={checkIn}
            onChange={(e) => setCheckIn(e.target.value)}
            className="input"
          />
        </div>
        <div>
          <label className="label">Check-out</label>
          <input
            type="date"
            value={checkOut}
            onChange={(e) => setCheckOut(e.target.value)}
            className="input"
          />
        </div>
        <div>
          <label className="label">Min Stars</label>
          <select
            value={minStars}
            onChange={(e) => setMinStars(e.target.value)}
            className="input"
          >
            <option value="">Any</option>
            <option value="3">3+ Stars</option>
            <option value="4">4+ Stars</option>
            <option value="5">5 Stars</option>
          </select>
        </div>
        <div className="flex items-end">
          <button type="submit" className="btn-primary w-full">
            <HiSearch className="w-5 h-5 mr-2" />
            Search Hotels
          </button>
        </div>
      </div>
    </form>
  );
};

const CarSearchForm: React.FC<{ onSearch: (params: any) => void }> = ({ onSearch }) => {
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [carType, setCarType] = useState('');
  const [transmission, setTransmission] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch({
      city: city || undefined,
      state: state || undefined,
      car_type: carType || undefined,
      transmission_type: transmission || undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="card p-6 mb-8">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div>
          <label className="label">City</label>
          <div className="relative">
            <HiLocationMarker className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 w-4 h-4" />
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              placeholder="Los Angeles"
              className="input pl-10"
            />
          </div>
        </div>
        <div>
          <label className="label">State</label>
          <input
            type="text"
            value={state}
            onChange={(e) => setState(e.target.value.toUpperCase())}
            placeholder="CA"
            className="input"
            maxLength={2}
          />
        </div>
        <div>
          <label className="label">Car Type</label>
          <select
            value={carType}
            onChange={(e) => setCarType(e.target.value)}
            className="input"
          >
            <option value="">Any Type</option>
            <option value="Compact">Compact</option>
            <option value="Sedan">Sedan</option>
            <option value="SUV">SUV</option>
            <option value="Luxury">Luxury</option>
            <option value="Van">Van</option>
          </select>
        </div>
        <div>
          <label className="label">Transmission</label>
          <select
            value={transmission}
            onChange={(e) => setTransmission(e.target.value)}
            className="input"
          >
            <option value="">Any</option>
            <option value="Automatic">Automatic</option>
            <option value="Manual">Manual</option>
          </select>
        </div>
        <div className="flex items-end">
          <button type="submit" className="btn-primary w-full">
            <HiSearch className="w-5 h-5 mr-2" />
            Search Cars
          </button>
        </div>
      </div>
    </form>
  );
};

// Result Card Components
const FlightCard: React.FC<{ flight: FlightResult; index: number }> = ({ flight, index }) => {
  const departureTime = new Date(flight.departure_date_time);
  const arrivalTime = new Date(flight.arrival_date_time);
  const hours = Math.floor(flight.duration_minutes / 60);
  const mins = flight.duration_minutes % 60;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="card-hover p-6"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-6">
          <div className="w-16 h-16 bg-gradient-to-br from-primary-500/20 to-primary-600/20 rounded-xl flex items-center justify-center">
            <FaPlane className="w-8 h-8 text-primary-400" />
          </div>
          <div>
            <p className="text-lg font-semibold text-white">{flight.airline}</p>
            <p className="text-gray-400 text-sm">
              {flight.flight_class} • {flight.current_available_seats} seats left
            </p>
          </div>
          <div className="text-center">
            <p className="text-xl font-semibold text-white">
              {format(departureTime, 'HH:mm')}
            </p>
            <p className="text-gray-400 text-sm">{flight.departure_airport}</p>
          </div>
          <div className="text-center px-8">
            <p className="text-gray-400 text-sm">{hours}h {mins}m</p>
            <div className="w-24 h-0.5 bg-dark-600 relative my-2">
              <div className="absolute left-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-dark-400 rounded-full"></div>
              <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-primary-500 rounded-full"></div>
            </div>
            <p className="text-gray-500 text-xs">Direct</p>
          </div>
          <div className="text-center">
            <p className="text-xl font-semibold text-white">
              {format(arrivalTime, 'HH:mm')}
            </p>
            <p className="text-gray-400 text-sm">{flight.arrival_airport}</p>
          </div>
        </div>
        <div className="text-right">
          <div className="flex items-center justify-end mb-1">
            <FaStar className="w-4 h-4 text-yellow-400 mr-1" />
            <span className="text-white font-medium">{flight.flight_rating.toFixed(1)}</span>
          </div>
          <p className="text-2xl font-bold text-primary-400">${flight.ticket_price.toFixed(0)}</p>
          <p className="text-gray-500 text-sm mb-2">per person</p>
          <button className="btn-primary text-sm">Select Flight</button>
        </div>
      </div>
    </motion.div>
  );
};

const HotelCard: React.FC<{ hotel: HotelResult; index: number }> = ({ hotel, index }) => {
  const amenitiesList = hotel.amenities ? hotel.amenities.split(',').map(a => a.trim().toLowerCase()) : [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="card-hover p-6"
    >
      <div className="flex items-start space-x-6">
        <div className="w-32 h-24 bg-gradient-to-br from-secondary-500/20 to-secondary-600/20 rounded-xl flex items-center justify-center">
          <FaHotel className="w-12 h-12 text-secondary-400" />
        </div>
        <div className="flex-1">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white mb-1">{hotel.hotel_name}</h3>
              <div className="flex items-center space-x-1 mb-2">
                {Array.from({ length: hotel.star_rating }).map((_, i) => (
                  <FaStar key={i} className="w-4 h-4 text-yellow-400" />
                ))}
              </div>
              <div className="flex items-center text-gray-400 text-sm mb-2">
                <HiLocationMarker className="w-4 h-4 mr-1" />
                {hotel.city}, {hotel.state}
              </div>
              <div className="flex items-center space-x-3">
                {amenitiesList.includes('wi-fi') && (
                  <span className="flex items-center text-gray-400 text-sm">
                    <FaWifi className="w-4 h-4 mr-1" /> WiFi
                  </span>
                )}
                {amenitiesList.includes('parking') && (
                  <span className="flex items-center text-gray-400 text-sm">
                    <FaParking className="w-4 h-4 mr-1" /> Parking
                  </span>
                )}
                {amenitiesList.includes('pool') && (
                  <span className="flex items-center text-gray-400 text-sm">
                    <FaSwimmingPool className="w-4 h-4 mr-1" /> Pool
                  </span>
                )}
              </div>
              <p className="text-gray-500 text-sm mt-2">
                {hotel.current_available_rooms} rooms available
              </p>
            </div>
            <div className="text-right">
              <div className="flex items-center justify-end mb-2">
                <span className="bg-primary-500/20 text-primary-400 px-2 py-1 rounded text-sm font-medium">
                  {hotel.hotel_rating.toFixed(1)}
                </span>
              </div>
              <p className="text-2xl font-bold text-primary-400">${hotel.price_per_night.toFixed(0)}</p>
              <p className="text-gray-500 text-sm mb-2">per night</p>
              <button className="btn-primary text-sm">Book Now</button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

const CarCard: React.FC<{ car: CarResult; index: number }> = ({ car, index }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="card-hover p-6"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-6">
          <div className="w-24 h-16 bg-gradient-to-br from-accent-emerald/20 to-accent-emerald/30 rounded-xl flex items-center justify-center">
            <FaCar className="w-10 h-10 text-accent-emerald" />
          </div>
          <div>
            <span className={`badge ${
              car.car_type === 'SUV' ? 'badge-primary' :
              car.car_type === 'Luxury' ? 'badge-warning' : 'badge-success'
            } mb-1`}>
              {car.car_type}
            </span>
            <h3 className="text-lg font-semibold text-white">{car.model_and_year}</h3>
            <p className="text-gray-400 text-sm">{car.company_provider_name}</p>
          </div>
          <div className="flex items-center space-x-4 text-gray-400 text-sm">
            <span className="flex items-center">
              <HiUsers className="w-4 h-4 mr-1" />
              {car.number_of_seats} seats
            </span>
            <span>⚙️ {car.transmission_type}</span>
          </div>
        </div>
        <div className="text-right">
          <div className="flex items-center justify-end mb-1">
            <FaStar className="w-4 h-4 text-yellow-400 mr-1" />
            <span className="text-white font-medium">{car.car_rating.toFixed(1)}</span>
          </div>
          <span className={`badge ${
            car.availability_status === 'Available' ? 'badge-success' : 'badge-error'
          } mb-2`}>
            {car.availability_status}
          </span>
          <p className="text-2xl font-bold text-primary-400">${car.daily_rental_price.toFixed(0)}</p>
          <p className="text-gray-500 text-sm mb-2">per day</p>
          <button 
            className="btn-primary text-sm"
            disabled={car.availability_status !== 'Available'}
          >
            Rent Now
          </button>
        </div>
      </div>
    </motion.div>
  );
};

// Loading Skeleton
const ResultSkeleton: React.FC = () => (
  <div className="card p-6 animate-pulse">
    <div className="flex items-center justify-between">
      <div className="flex items-center space-x-6">
        <div className="w-16 h-16 bg-dark-700 rounded-xl"></div>
        <div className="space-y-2">
          <div className="w-32 h-5 bg-dark-700 rounded"></div>
          <div className="w-24 h-4 bg-dark-700 rounded"></div>
        </div>
      </div>
      <div className="text-right space-y-2">
        <div className="w-20 h-8 bg-dark-700 rounded ml-auto"></div>
        <div className="w-24 h-10 bg-dark-700 rounded"></div>
      </div>
    </div>
  </div>
);

// Filters Sidebar
const FiltersSidebar: React.FC<{
  type: string;
  filters: any;
  setFilters: (f: any) => void;
}> = ({ type, filters, setFilters }) => {
  return (
    <div className="card p-6 sticky top-24">
      <div className="flex items-center space-x-2 mb-6">
        <HiAdjustments className="w-5 h-5 text-primary-400" />
        <h2 className="font-semibold text-white">Filters</h2>
      </div>

      <div className="space-y-6">
        <div>
          <label className="label">Price Range</label>
          <div className="flex items-center space-x-2">
            <input
              type="number"
              placeholder="Min"
              value={filters.minPrice || ''}
              onChange={(e) => setFilters({ ...filters, minPrice: e.target.value })}
              className="input text-sm py-2"
            />
            <span className="text-gray-500">-</span>
            <input
              type="number"
              placeholder="Max"
              value={filters.maxPrice || ''}
              onChange={(e) => setFilters({ ...filters, maxPrice: e.target.value })}
              className="input text-sm py-2"
            />
          </div>
        </div>

        {type === 'hotels' && (
          <div>
            <label className="label">Star Rating</label>
            <div className="flex space-x-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  className={`w-10 h-10 rounded-lg border transition-all ${
                    filters.stars >= star
                      ? 'bg-primary-500 border-primary-500 text-dark-950'
                      : 'border-dark-600 text-gray-400 hover:border-primary-500'
                  }`}
                  onClick={() => setFilters({ ...filters, stars: star })}
                >
                  {star}
                </button>
              ))}
            </div>
          </div>
        )}

        {type === 'flights' && (
          <div>
            <label className="label">Flight Class</label>
            <div className="space-y-2">
              {['Any', 'Economy', 'Business', 'First'].map((option) => (
                <label key={option} className="flex items-center space-x-2">
                  <input
                    type="radio"
                    name="class"
                    checked={filters.flightClass === option || (!filters.flightClass && option === 'Any')}
                    onChange={() => setFilters({ ...filters, flightClass: option === 'Any' ? '' : option })}
                    className="w-4 h-4 text-primary-500"
                  />
                  <span className="text-gray-300">{option}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {type === 'cars' && (
          <div>
            <label className="label">Transmission</label>
            <div className="space-y-2">
              {['Any', 'Automatic', 'Manual'].map((option) => (
                <label key={option} className="flex items-center space-x-2">
                  <input
                    type="radio"
                    name="transmission"
                    checked={filters.transmission === option || (!filters.transmission && option === 'Any')}
                    onChange={() => setFilters({ ...filters, transmission: option === 'Any' ? '' : option })}
                    className="w-4 h-4 text-primary-500"
                  />
                  <span className="text-gray-300">{option}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        <button 
          onClick={() => setFilters({})}
          className="btn-secondary w-full"
        >
          Clear Filters
        </button>
      </div>
    </div>
  );
};

// Main Search Page Component
const SearchPage: React.FC = () => {
  const { type = 'flights' } = useParams<{ type: string }>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useState<any>({});
  const [filters, setFilters] = useState<any>({});
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState('price');
  const pageSize = 10;

  // Build query params
  const queryParams = {
    ...searchParams,
    min_price: filters.minPrice || undefined,
    max_price: filters.maxPrice || undefined,
    flight_class: filters.flightClass || undefined,
    min_stars: filters.stars || undefined,
    transmission_type: filters.transmission || undefined,
    page,
    page_size: pageSize,
  };

  // Flights Query
  const flightsQuery = useQuery({
    queryKey: ['flights', queryParams],
    queryFn: () => flightService.search(queryParams),
    enabled: type === 'flights',
    staleTime: 30000,
  });

  // Hotels Query
  const hotelsQuery = useQuery({
    queryKey: ['hotels', queryParams],
    queryFn: () => hotelService.search(queryParams),
    enabled: type === 'hotels',
    staleTime: 30000,
  });

  // Cars Query
  const carsQuery = useQuery({
    queryKey: ['cars', queryParams],
    queryFn: () => carService.search(queryParams),
    enabled: type === 'cars',
    staleTime: 30000,
  });

  // Get current query based on type
  const currentQuery = type === 'flights' ? flightsQuery : type === 'hotels' ? hotelsQuery : carsQuery;
  const isLoading = currentQuery.isLoading;
  const isError = currentQuery.isError;

  // Get results
  const results = currentQuery.data;
  const flights = results?.flights || [];
  const hotels = results?.hotels || [];
  const cars = results?.cars || [];
  const totalResults = results?.total || 0;
  const totalPages = results?.total_pages || 1;

  // Handle search
  const handleSearch = (params: any) => {
    setSearchParams(params);
    setPage(1);
  };

  // Sort results
  const sortResults = (items: any[]) => {
    return [...items].sort((a, b) => {
      switch (sortBy) {
        case 'price':
          const priceA = a.ticket_price || a.price_per_night || a.daily_rental_price;
          const priceB = b.ticket_price || b.price_per_night || b.daily_rental_price;
          return priceA - priceB;
        case 'price-desc':
          const priceA2 = a.ticket_price || a.price_per_night || a.daily_rental_price;
          const priceB2 = b.ticket_price || b.price_per_night || b.daily_rental_price;
          return priceB2 - priceA2;
        case 'rating':
          const ratingA = a.flight_rating || a.hotel_rating || a.car_rating;
          const ratingB = b.flight_rating || b.hotel_rating || b.car_rating;
          return ratingB - ratingA;
        default:
          return 0;
      }
    });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Tab Navigation */}
      <div className="flex space-x-2 mb-6">
        {[
          { key: 'flights', label: 'Flights', icon: FaPlane },
          { key: 'hotels', label: 'Hotels', icon: FaHotel },
          { key: 'cars', label: 'Cars', icon: FaCar },
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => {
              navigate(`/search/${key}`);
              setSearchParams({});
              setFilters({});
              setPage(1);
            }}
            className={`flex items-center px-6 py-3 rounded-xl font-medium transition-all ${
              type === key
                ? 'bg-primary-500 text-dark-950'
                : 'bg-dark-800 text-gray-300 hover:bg-dark-700'
            }`}
          >
            <Icon className="w-4 h-4 mr-2" />
            {label}
          </button>
        ))}
      </div>

      {/* Search Forms */}
      {type === 'flights' && <FlightSearchForm onSearch={handleSearch} />}
      {type === 'hotels' && <HotelSearchForm onSearch={handleSearch} />}
      {type === 'cars' && <CarSearchForm onSearch={handleSearch} />}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1">
          <FiltersSidebar type={type} filters={filters} setFilters={setFilters} />
        </div>

        {/* Results */}
        <div className="lg:col-span-3">
          {/* Results Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-display font-bold text-white mb-1">
                {type === 'flights' && 'Flight Results'}
                {type === 'hotels' && 'Hotel Results'}
                {type === 'cars' && 'Car Rental Results'}
              </h1>
              <p className="text-gray-400">
                {isLoading ? 'Searching...' : `${totalResults} results found`}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => currentQuery.refetch()}
                className="p-2 text-gray-400 hover:text-white transition-colors"
                disabled={isLoading}
              >
                <HiRefresh className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
              </button>
              <div className="flex items-center space-x-2">
                <HiSortDescending className="w-5 h-5 text-gray-400" />
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="input py-2 text-sm w-40"
                >
                  <option value="price">Price: Low to High</option>
                  <option value="price-desc">Price: High to Low</option>
                  <option value="rating">Rating</option>
                </select>
              </div>
            </div>
          </div>

          {/* Error State */}
          {isError && (
            <div className="card p-8 text-center">
              <div className="text-5xl mb-4">😕</div>
              <h3 className="text-xl font-semibold text-white mb-2">Something went wrong</h3>
              <p className="text-gray-400 mb-4">We couldn't fetch the results. Please try again.</p>
              <button onClick={() => currentQuery.refetch()} className="btn-primary">
                Try Again
              </button>
            </div>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <ResultSkeleton key={i} />
              ))}
            </div>
          )}

          {/* Results List */}
          {!isLoading && !isError && (
            <AnimatePresence mode="wait">
              <div className="space-y-4">
                {type === 'flights' && sortResults(flights).map((flight, index) => (
                  <FlightCard key={flight.flight_id} flight={flight} index={index} />
                ))}
                {type === 'hotels' && sortResults(hotels).map((hotel, index) => (
                  <HotelCard key={hotel.hotel_id} hotel={hotel} index={index} />
                ))}
                {type === 'cars' && sortResults(cars).map((car, index) => (
                  <CarCard key={car.car_id} car={car} index={index} />
                ))}

                {/* Empty State */}
                {totalResults === 0 && (
                  <div className="card p-12 text-center">
                    <div className="text-6xl mb-4">
                      {type === 'flights' ? '✈️' : type === 'hotels' ? '🏨' : '🚗'}
                    </div>
                    <h3 className="text-xl font-semibold text-white mb-2">No results found</h3>
                    <p className="text-gray-400">
                      Try adjusting your search criteria or filters.
                    </p>
                  </div>
                )}
              </div>
            </AnimatePresence>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center space-x-2 mt-8">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-2 rounded-lg bg-dark-800 text-gray-400 hover:text-white hover:bg-dark-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <HiChevronLeft className="w-5 h-5" />
              </button>
              
              {[...Array(Math.min(5, totalPages))].map((_, i) => {
                const pageNum = i + 1;
                return (
                  <button
                    key={pageNum}
                    onClick={() => setPage(pageNum)}
                    className={`w-10 h-10 rounded-lg font-medium transition-all ${
                      page === pageNum
                        ? 'bg-primary-500 text-dark-950'
                        : 'bg-dark-800 text-gray-400 hover:bg-dark-700'
                    }`}
                  >
                    {pageNum}
                  </button>
                );
              })}

              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-2 rounded-lg bg-dark-800 text-gray-400 hover:text-white hover:bg-dark-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <HiChevronRight className="w-5 h-5" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchPage;
