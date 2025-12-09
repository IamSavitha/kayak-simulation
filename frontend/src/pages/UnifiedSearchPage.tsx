import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Search, Plane, Hotel, Car, MapPin, Calendar, DollarSign, Loader2, AlertCircle, ArrowRight } from 'lucide-react';
import { unifiedSearch, UnifiedSearchParams } from '../api/search';

const UnifiedSearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<{
    flights: any[];
    hotels: any[];
    cars: any[];
    total_results: number;
  } | null>(null);

  const [formData, setFormData] = useState({
    query: searchParams.get('query') || '',
    city: searchParams.get('city') || '',
    departure_airport: searchParams.get('departure_airport') || '',
    arrival_airport: searchParams.get('arrival_airport') || '',
    check_in: searchParams.get('check_in') || '',
    check_out: searchParams.get('check_out') || '',
    min_price: searchParams.get('min_price') || '',
    max_price: searchParams.get('max_price') || '',
  });

  useEffect(() => {
    // If there are search params, perform search on mount
    if (searchParams.get('city') || searchParams.get('query') || searchParams.get('departure_airport')) {
      handleSearch();
    }
  }, []);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params: UnifiedSearchParams = {
        page: 1,
        page_size: 20,
      };

      if (formData.query) params.query = formData.query;
      if (formData.city) params.city = formData.city;
      // Backend will handle both codes and city names
      if (formData.departure_airport) params.departure_airport = formData.departure_airport;
      if (formData.arrival_airport) params.arrival_airport = formData.arrival_airport;
      if (formData.check_in) params.check_in = formData.check_in;
      if (formData.check_out) params.check_out = formData.check_out;
      if (formData.min_price) params.min_price = parseFloat(formData.min_price);
      if (formData.max_price) params.max_price = parseFloat(formData.max_price);

      const data = await unifiedSearch(params);
      setResults(data);
      
      // Update URL with search params
      const newParams = new URLSearchParams();
      Object.entries(formData).forEach(([key, value]) => {
        if (value) newParams.append(key, value);
      });
      setSearchParams(newParams);
    } catch (err: any) {
      setError(err.message || 'Search failed. Please try again.');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-slate-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Unified Search</h1>
          <p className="text-slate-600">Search across flights, hotels, and cars in one place</p>
        </div>

        {/* Search Form */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="bg-white rounded-2xl border-2 border-slate-300 shadow-xl p-6">
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">City or Query</label>
                <div className="flex items-center border-2 border-slate-300 rounded-lg px-4 py-2 bg-white">
                  <MapPin className="text-slate-500 mr-2" size={18} />
                  <input
                    type="text"
                    name="query"
                    value={formData.query}
                    onChange={handleInputChange}
                    placeholder="e.g., San Francisco"
                    className="flex-1 outline-none text-slate-900"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">City (for hotels/cars)</label>
                <div className="flex items-center border-2 border-slate-300 rounded-lg px-4 py-2 bg-white">
                  <MapPin className="text-slate-500 mr-2" size={18} />
                  <input
                    type="text"
                    name="city"
                    value={formData.city}
                    onChange={handleInputChange}
                    placeholder="e.g., San Francisco"
                    className="flex-1 outline-none text-slate-900"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Departure Airport</label>
                <div className="flex items-center border-2 border-slate-300 rounded-lg px-4 py-2 bg-white">
                  <Plane className="text-slate-500 mr-2" size={18} />
                  <input
                    type="text"
                    name="departure_airport"
                    value={formData.departure_airport}
                    onChange={handleInputChange}
                    placeholder="e.g., SFO"
                    className="flex-1 outline-none text-slate-900 uppercase"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Arrival Airport</label>
                <div className="flex items-center border-2 border-slate-300 rounded-lg px-4 py-2 bg-white">
                  <Plane className="text-slate-500 mr-2" size={18} />
                  <input
                    type="text"
                    name="arrival_airport"
                    value={formData.arrival_airport}
                    onChange={handleInputChange}
                    placeholder="e.g., NYC"
                    className="flex-1 outline-none text-slate-900 uppercase"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Check-in Date</label>
                <div className="flex items-center border-2 border-slate-300 rounded-lg px-4 py-2 bg-white">
                  <Calendar className="text-slate-500 mr-2" size={18} />
                  <input
                    type="date"
                    name="check_in"
                    value={formData.check_in}
                    onChange={handleInputChange}
                    className="flex-1 outline-none text-slate-900"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Check-out Date</label>
                <div className="flex items-center border-2 border-slate-300 rounded-lg px-4 py-2 bg-white">
                  <Calendar className="text-slate-500 mr-2" size={18} />
                  <input
                    type="date"
                    name="check_out"
                    value={formData.check_out}
                    onChange={handleInputChange}
                    className="flex-1 outline-none text-slate-900"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Min Price</label>
                <div className="flex items-center border-2 border-slate-300 rounded-lg px-4 py-2 bg-white">
                  <DollarSign className="text-slate-500 mr-2" size={18} />
                  <input
                    type="number"
                    name="min_price"
                    value={formData.min_price}
                    onChange={handleInputChange}
                    placeholder="0"
                    className="flex-1 outline-none text-slate-900"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Max Price</label>
                <div className="flex items-center border-2 border-slate-300 rounded-lg px-4 py-2 bg-white">
                  <DollarSign className="text-slate-500 mr-2" size={18} />
                  <input
                    type="number"
                    name="max_price"
                    value={formData.max_price}
                    onChange={handleInputChange}
                    placeholder="10000"
                    className="flex-1 outline-none text-slate-900"
                  />
                </div>
              </div>
            </div>

            <button
              onClick={handleSearch}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg flex items-center justify-center space-x-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <Search size={20} />
                  <span>Search All</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="max-w-4xl mx-auto mb-6">
            <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4 flex items-center space-x-2">
              <AlertCircle className="text-red-600" size={20} />
              <span className="text-red-800">{error}</span>
            </div>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="max-w-6xl mx-auto">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-slate-900 mb-2">
                Search Results
              </h2>
              <p className="text-slate-600">
                Found <span className="font-semibold">{results.total_results}</span> total results
              </p>
            </div>

            {/* Flights Section */}
            {results.flights.length > 0 && (
              <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-slate-900 flex items-center">
                    <Plane className="mr-2 text-blue-600" size={24} />
                    Flights ({results.flights.length})
                  </h3>
                  <button
                    onClick={() => navigate('/flights')}
                    className="text-blue-600 hover:text-blue-700 font-semibold flex items-center"
                  >
                    View All <ArrowRight size={16} className="ml-1" />
                  </button>
                </div>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {results.flights.slice(0, 6).map((flight: any) => (
                    <div key={flight.flight_id} className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
                      <div className="font-semibold text-slate-900">
                        {flight.departure_airport} → {flight.arrival_airport}
                      </div>
                      <div className="text-sm text-slate-600 mt-1">{flight.airline_name}</div>
                      <div className="text-lg font-bold text-blue-600 mt-2">${flight.base_price}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Hotels Section */}
            {results.hotels.length > 0 && (
              <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-slate-900 flex items-center">
                    <Hotel className="mr-2 text-blue-600" size={24} />
                    Hotels ({results.hotels.length})
                  </h3>
                  <button
                    onClick={() => navigate('/hotels')}
                    className="text-blue-600 hover:text-blue-700 font-semibold flex items-center"
                  >
                    View All <ArrowRight size={16} className="ml-1" />
                  </button>
                </div>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {results.hotels.slice(0, 6).map((hotel: any) => (
                    <div key={hotel.hotel_id} className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
                      <div className="font-semibold text-slate-900">{hotel.hotel_name}</div>
                      <div className="text-sm text-slate-600 mt-1">{hotel.city}, {hotel.state}</div>
                      <div className="text-lg font-bold text-blue-600 mt-2">${hotel.star_rating}★</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Cars Section */}
            {results.cars.length > 0 && (
              <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-slate-900 flex items-center">
                    <Car className="mr-2 text-blue-600" size={24} />
                    Cars ({results.cars.length})
                  </h3>
                  <button
                    onClick={() => navigate('/cars')}
                    className="text-blue-600 hover:text-blue-700 font-semibold flex items-center"
                  >
                    View All <ArrowRight size={16} className="ml-1" />
                  </button>
                </div>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {results.cars.slice(0, 6).map((car: any) => (
                    <div key={car.car_id} className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
                      <div className="font-semibold text-slate-900">{car.make} {car.model}</div>
                      <div className="text-sm text-slate-600 mt-1">{car.city}, {car.state}</div>
                      <div className="text-lg font-bold text-blue-600 mt-2">${car.daily_rental_price}/day</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* No Results */}
            {results.total_results === 0 && (
              <div className="text-center py-12">
                <AlertCircle className="mx-auto text-slate-400 mb-4" size={48} />
                <h3 className="text-xl font-semibold text-slate-700 mb-2">No results found</h3>
                <p className="text-slate-600">Try adjusting your search criteria</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default UnifiedSearchPage;

