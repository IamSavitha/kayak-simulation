import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Plane, Calendar, MapPin, Users, Search, Filter, ArrowRight, Clock, DollarSign, Star, Loader2 } from 'lucide-react';
import { searchFlights, Flight as FlightAPI, FlightSearchParams } from '../api/flights';
import BookingModal from '../components/BookingModal';
import { usePriceUpdates } from '../hooks/usePriceUpdates';

interface Flight {
  id: string;
  airline: string;
  from: string;
  to: string;
  departure: string;
  arrival: string;
  departure_datetime: string; // Full ISO datetime string
  arrival_datetime: string; // Full ISO datetime string
  duration: string;
  price: number;
  class: string;
  stops: number;
  rating: number;
  available_seats?: number; // Available seats
  total_seats?: number; // Total seats
}

const FlightsPage: React.FC = () => {
  const [urlParams] = useSearchParams();
  const [showFilters, setShowFilters] = useState(false);
  const [flights, setFlights] = useState<Flight[]>([]);
  const [filteredFlights, setFilteredFlights] = useState<Flight[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFlight, setSelectedFlight] = useState<Flight | null>(null);
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [highlightedFlightId, setHighlightedFlightId] = useState<string | null>(null);
  const [searchParams, setSearchParams] = useState({
    from: '',
    to: '',
    departure: '',
    return: '',
    travelers: '1'
  });
  
  // Filter state
  const [filters, setFilters] = useState({
    stops: [] as string[],
    priceRange: [0, 1000] as [number, number],
    airlines: [] as string[],
    flightClass: [] as string[]
  });

  // Convert API flight to display format
  const convertFlight = (flight: FlightAPI): Flight => {
    const depDate = new Date(flight.departure_datetime);
    const arrDate = new Date(flight.arrival_datetime);
    const durationMs = arrDate.getTime() - depDate.getTime();
    const hours = Math.floor(durationMs / (1000 * 60 * 60));
    const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));
    
    return {
      id: flight.flight_id,
      airline: flight.airline_name,
      from: flight.departure_airport,
      to: flight.arrival_airport,
      departure: depDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      arrival: arrDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      departure_datetime: flight.departure_datetime, // Keep full datetime
      arrival_datetime: flight.arrival_datetime, // Keep full datetime
      duration: `${hours}h ${minutes}m`,
      price: flight.base_price,
      class: flight.flight_class,
      stops: flight.stops || 0,
      rating: flight.rating || 4.0,
      available_seats: flight.available_seats,
      total_seats: flight.total_seats
    };
  };

  // Load flights on mount
  useEffect(() => {
    loadFlights();
  }, []);

  const loadFlights = async () => {
    setLoading(true);
    setError(null);
    try {
      const params: FlightSearchParams = {
        page: 1,
        page_size: 1000 // Show all flights
      };
      
      if (searchParams.from) {
        // Backend will handle both codes and city names
        params.departure_airport = searchParams.from;
      }
      if (searchParams.to) {
        // Backend will handle both codes and city names
        params.arrival_airport = searchParams.to;
      }
      // Date inputs return YYYY-MM-DD format, which is what the API expects
      if (searchParams.departure) {
        params.departure_date = searchParams.departure; // Already in YYYY-MM-DD format
      }
      if (searchParams.return) {
        params.return_date = searchParams.return; // Already in YYYY-MM-DD format
      }
      if (searchParams.travelers) {
        params.num_passengers = parseInt(searchParams.travelers) || 1;
      }

      const response = await searchFlights(params);
      if (response && response.flights) {
        const convertedFlights = response.flights.map(convertFlight);
        setFlights(convertedFlights);
        setFilteredFlights(convertedFlights);
        setError(null);
      } else {
        setFlights([]);
        setFilteredFlights([]);
        setError(null);
      }
    } catch (err: any) {
      // Handle nested error detail structure
      let errorMessage = 'Failed to load flights';
      if (err.message) {
        errorMessage = err.message;
        // If error is "Flight not found" or "NOT_FOUND", treat as empty result
        if (errorMessage.toLowerCase().includes('not found') || errorMessage.includes('NOT_FOUND')) {
          setFlights([]);
          setError(null);
          return;
        }
      } else if (err.detail) {
        errorMessage = typeof err.detail === 'string' ? err.detail : err.detail.message || errorMessage;
        // If error is "Flight not found", treat as empty result
        if (errorMessage.toLowerCase().includes('not found') || err.detail.error_code === 'NOT_FOUND') {
          setFlights([]);
          setError(null);
          return;
        }
      }
      setError(errorMessage);
      setFlights([]);
      setFilteredFlights([]);
      console.error('Error loading flights:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    loadFlights();
  };

  // Apply filters to flights
  useEffect(() => {
    let filtered = [...flights];

    // Filter by stops
    if (filters.stops.length > 0) {
      filtered = filtered.filter(flight => {
        if (filters.stops.includes('Non-stop') && flight.stops === 0) return true;
        if (filters.stops.includes('1 stop') && flight.stops === 1) return true;
        if (filters.stops.includes('2+ stops') && flight.stops >= 2) return true;
        return false;
      });
    }

    // Filter by price range
    filtered = filtered.filter(flight => 
      flight.price >= filters.priceRange[0] && flight.price <= filters.priceRange[1]
    );

    // Filter by airlines
    if (filters.airlines.length > 0) {
      filtered = filtered.filter(flight => 
        filters.airlines.some(airline => flight.airline.toLowerCase().includes(airline.toLowerCase()))
      );
    }

    // Filter by flight class
    if (filters.flightClass.length > 0) {
      filtered = filtered.filter(flight => 
        filters.flightClass.includes(flight.class)
      );
    }

    setFilteredFlights(filtered);
  }, [flights, filters]);

  // Handle flight_id from URL (when coming from deals page)
  useEffect(() => {
    const flightId = urlParams.get('flight_id');
    if (flightId && filteredFlights.length > 0) {
      setHighlightedFlightId(flightId);
      
      // Find and scroll to the flight
      setTimeout(() => {
        const element = document.getElementById(`flight-${flightId}`);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 300);
      
      // Clear highlight after 3 seconds
      setTimeout(() => {
        setHighlightedFlightId(null);
      }, 3000);
    }
  }, [urlParams, filteredFlights]);

  const handleSelectFlight = (flight: Flight) => {
    // Store selected flight with travelers info
    const flightWithTravelers = {
      ...flight,
      travelers: searchParams.travelers
    };
    setSelectedFlight(flightWithTravelers);
    setShowBookingModal(true);
  };

  const handleBookingSuccess = () => {
    // Reload flights to update availability
    loadFlights();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30">
      {/* Search Header */}
      <div className="bg-gradient-to-r from-slate-700 to-slate-800 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-8 animate-slide-down">Search Flights</h1>

          {/* Search Form */}
          <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-6 border-2 border-white/40 shadow-2xl animate-scale-in">
            <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700">From</label>
                <div className="flex items-center border-2 border-slate-300 rounded-xl px-4 py-3 bg-white hover:border-slate-500 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200 transition-all shadow-sm">
                  <MapPin className="text-slate-600 mr-3 flex-shrink-0" size={18} />
                  <input
                    type="text"
                    placeholder="SFO or San Francisco"
                    value={searchParams.from}
                    onChange={(e) => setSearchParams({ ...searchParams, from: e.target.value })}
                    className="w-full outline-none text-sm font-semibold text-slate-900 placeholder:text-slate-400 bg-transparent"
                  />
                </div>
                <p className="text-xs text-slate-500">Enter code (SFO) or city name</p>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700">To</label>
                <div className="flex items-center border-2 border-slate-300 rounded-xl px-4 py-3 bg-white hover:border-slate-500 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200 transition-all shadow-sm">
                  <MapPin className="text-slate-600 mr-3 flex-shrink-0" size={18} />
                  <input
                    type="text"
                    placeholder="LAX or Los Angeles"
                    value={searchParams.to}
                    onChange={(e) => setSearchParams({ ...searchParams, to: e.target.value })}
                    className="w-full outline-none text-sm font-semibold text-slate-900 placeholder:text-slate-400 bg-transparent"
                  />
                </div>
                <p className="text-xs text-slate-500">Enter code (LAX) or city name</p>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700">Departure</label>
                <div className="flex items-center border-2 border-slate-300 rounded-xl px-4 py-3 bg-white hover:border-slate-500 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200 transition-all shadow-sm">
                  <Calendar className="text-slate-600 mr-3 flex-shrink-0" size={18} />
                  <input
                    type="date"
                    value={searchParams.departure}
                    onChange={(e) => setSearchParams({ ...searchParams, departure: e.target.value })}
                    className="w-full outline-none text-sm font-semibold text-slate-900 placeholder:text-slate-400 bg-transparent [color-scheme:light]"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700">Return</label>
                <div className="flex items-center border-2 border-slate-300 rounded-xl px-4 py-3 bg-white hover:border-slate-500 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200 transition-all shadow-sm">
                  <Calendar className="text-slate-600 mr-3 flex-shrink-0" size={18} />
                  <input
                    type="date"
                    value={searchParams.return}
                    onChange={(e) => setSearchParams({ ...searchParams, return: e.target.value })}
                    className="w-full outline-none text-sm font-semibold text-slate-900 placeholder:text-slate-400 bg-transparent [color-scheme:light]"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700">Travelers</label>
                <div className="flex items-center border-2 border-slate-300 rounded-xl px-4 py-3 bg-white hover:border-slate-500 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200 transition-all shadow-sm">
                  <Users className="text-slate-600 mr-3 flex-shrink-0" size={18} />
                  <input
                    type="number"
                    placeholder="1"
                    min="1"
                    value={searchParams.travelers}
                    onChange={(e) => setSearchParams({ ...searchParams, travelers: e.target.value })}
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
              <span className="text-base">{loading ? 'Searching...' : 'Search Flights'}</span>
              {!loading && <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform duration-300" />}
            </button>
          </div>
        </div>
      </div>

      {/* Results Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold text-slate-900">Available Flights</h2>
            {error ? (
              <p className="text-red-600 mt-1">{String(error)}</p>
            ) : (
              <p className="text-slate-600 mt-1">{filteredFlights.length} flights found</p>
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

                {/* Stops Filter */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Stops</h4>
                  <div className="space-y-2">
                    {['Non-stop', '1 stop', '2+ stops'].map((option) => (
                      <label key={option} className="flex items-center space-x-2 cursor-pointer group">
                        <input 
                          type="checkbox" 
                          className="rounded text-slate-600 focus:ring-slate-500"
                          checked={filters.stops.includes(option)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setFilters({ ...filters, stops: [...filters.stops, option] });
                            } else {
                              setFilters({ ...filters, stops: filters.stops.filter(s => s !== option) });
                            }
                          }}
                        />
                        <span className="text-sm text-slate-600 group-hover:text-slate-900">{option}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Price Range */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Price Range</h4>
                  <input 
                    type="range" 
                    min="0" 
                    max="1000" 
                    className="w-full"
                    value={filters.priceRange[1]}
                    onChange={(e) => {
                      setFilters({ ...filters, priceRange: [filters.priceRange[0], parseInt(e.target.value)] });
                    }}
                  />
                  <div className="flex justify-between text-xs text-slate-600 mt-2">
                    <span>${filters.priceRange[0]}</span>
                    <span>${filters.priceRange[1]}+</span>
                  </div>
                </div>

                {/* Airlines */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Airlines</h4>
                  <div className="space-y-2">
                    {['United Airlines', 'Delta', 'American Airlines', 'Southwest Airlines', 'JetBlue Airways', 'Alaska Airlines'].map((airline) => (
                      <label key={airline} className="flex items-center space-x-2 cursor-pointer group">
                        <input 
                          type="checkbox" 
                          className="rounded text-slate-600 focus:ring-slate-500"
                          checked={filters.airlines.includes(airline)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setFilters({ ...filters, airlines: [...filters.airlines, airline] });
                            } else {
                              setFilters({ ...filters, airlines: filters.airlines.filter(a => a !== airline) });
                            }
                          }}
                        />
                        <span className="text-sm text-slate-600 group-hover:text-slate-900">{airline}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Flight Class */}
                <div>
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Class</h4>
                  <div className="space-y-2">
                    {['economy', 'business', 'first'].map((flightClass) => (
                      <label key={flightClass} className="flex items-center space-x-2 cursor-pointer group">
                        <input 
                          type="checkbox" 
                          className="rounded text-slate-600 focus:ring-slate-500"
                          checked={filters.flightClass.includes(flightClass)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setFilters({ ...filters, flightClass: [...filters.flightClass, flightClass] });
                            } else {
                              setFilters({ ...filters, flightClass: filters.flightClass.filter(c => c !== flightClass) });
                            }
                          }}
                        />
                        <span className="text-sm text-slate-600 group-hover:text-slate-900 capitalize">{flightClass}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Clear Filters Button */}
                {(filters.stops.length > 0 || filters.airlines.length > 0 || filters.flightClass.length > 0 || filters.priceRange[1] < 1000) && (
                  <button
                    onClick={() => setFilters({ stops: [], priceRange: [0, 1000], airlines: [], flightClass: [] })}
                    className="w-full mt-4 px-4 py-2 text-sm text-slate-600 hover:text-slate-900 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
                  >
                    Clear Filters
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Flight Results */}
          <div className={showFilters ? 'lg:col-span-2' : 'lg:col-span-3'}>
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 size={32} className="animate-spin text-slate-600" />
              </div>
            ) : filteredFlights.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-slate-600 text-lg">No flights found. Try adjusting your search criteria or filters.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredFlights.map((flight, index) => (
                  <FlightCard 
                    key={flight.id} 
                    flight={flight} 
                    delay={index * 100}
                    onSelect={() => handleSelectFlight(flight)}
                    isHighlighted={highlightedFlightId === flight.id}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Booking Modal */}
      <BookingModal
        flight={selectedFlight}
        isOpen={showBookingModal}
        onClose={() => {
          setShowBookingModal(false);
          setSelectedFlight(null);
        }}
        onSuccess={handleBookingSuccess}
      />
    </div>
  );
};

interface FlightCardProps {
  flight: Flight;
  delay: number;
  onSelect: () => void;
  isHighlighted?: boolean;
}

const FlightCard: React.FC<FlightCardProps> = ({ flight, delay, onSelect, isHighlighted }) => (
  <div
    id={`flight-${flight.id}`}
    className={`card-interactive p-6 animate-slide-up ${isHighlighted ? 'ring-4 ring-blue-500 ring-offset-2' : ''}`}
    style={{ animationDelay: `${delay}ms` }}
  >
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
      {/* Flight Info */}
      <div className="flex-1">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-slate-100 rounded-lg">
            <Plane className="text-slate-700" size={24} />
          </div>
          <div>
            <h3 className="font-bold text-lg text-slate-900">{flight.airline}</h3>
            <div className="flex items-center space-x-2 text-sm text-slate-600">
              <span className="flex items-center">
                <Star className="w-4 h-4 fill-yellow-400 text-yellow-400 mr-1" />
                {flight.rating}
              </span>
              <span>•</span>
              <span>{flight.class}</span>
              <span>•</span>
              <span className="flex items-center">
                {flight.stops === 0 ? (
                  <span className="text-green-600 font-medium">Non-stop</span>
                ) : (
                  <span>{flight.stops} stop{flight.stops > 1 ? 's' : ''}</span>
                )}
              </span>
              {flight.available_seats !== undefined && (
                <>
                  <span>•</span>
                  <span className={`font-medium ${
                    flight.available_seats > 10 
                      ? 'text-green-600' 
                      : flight.available_seats > 0 
                        ? 'text-yellow-600' 
                        : 'text-red-600'
                  }`}>
                    {flight.available_seats > 0 
                      ? `${flight.available_seats} seat${flight.available_seats !== 1 ? 's' : ''} available`
                      : 'Sold out'
                    }
                  </span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Route Info */}
        <div className="flex items-center space-x-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-slate-900">{flight.departure}</div>
            <div className="text-sm text-slate-600 font-medium">{flight.from}</div>
          </div>

          <div className="flex-1 flex flex-col items-center">
            <div className="flex items-center space-x-1 text-slate-500 mb-1">
              <Clock size={14} />
              <span className="text-xs font-medium">{flight.duration}</span>
            </div>
            <div className="w-full h-0.5 bg-slate-200 relative">
              <div className="absolute left-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-slate-600 rounded-full"></div>
              <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-slate-600 rounded-full"></div>
            </div>
          </div>

          <div className="text-center">
            <div className="text-2xl font-bold text-slate-900">{flight.arrival}</div>
            <div className="text-sm text-slate-600 font-medium">{flight.to}</div>
          </div>
        </div>
      </div>

      {/* Price and Action */}
      <div className="flex md:flex-col items-center md:items-end justify-between md:justify-center gap-4">
        <div className="text-right">
          <div className="flex items-center text-slate-600 text-sm mb-1">
            <DollarSign size={14} />
            <span>from</span>
          </div>
          <div className="text-3xl font-bold text-slate-800">${flight.price}</div>
          <div className="text-xs text-slate-500">per person</div>
        </div>
        <button 
          onClick={onSelect}
          className="btn-primary px-6 py-3 whitespace-nowrap group"
        >
          <span>Select Flight</span>
          <ArrowRight size={16} className="ml-2 inline group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  </div>
);

export default FlightsPage;
