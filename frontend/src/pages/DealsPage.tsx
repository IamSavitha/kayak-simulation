import React, { useState, useEffect } from 'react';
import { TrendingDown, Plane, Hotel, Car, Filter, Star, Tag, Loader2, X, AlertCircle, Sparkles, ArrowRight } from 'lucide-react';
import { getDeals, Deal } from '../api/deals';
import { useNavigate } from 'react-router-dom';

const DealsPage: React.FC = () => {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [filteredDeals, setFilteredDeals] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const navigate = useNavigate();

  // Filter state
  const [filters, setFilters] = useState({
    listing_type: undefined as 'flight' | 'hotel' | 'car' | undefined,
    min_score: 0,
    sort_by: 'score' as 'score' | 'discount' | 'price'
  });

  // Load deals on component mount
  useEffect(() => {
    loadDeals();
  }, []);

  // Apply filters when deals or filters change
  useEffect(() => {
    applyFilters();
  }, [deals, filters]);

  const loadDeals = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getDeals({
        listing_type: filters.listing_type,
        min_score: filters.min_score,
        limit: 100 // Get more deals, we'll filter client-side
      });
      setDeals(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load deals. Please try again.');
      console.error('Error loading deals:', err);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...deals];

    // Apply listing type filter
    if (filters.listing_type) {
      filtered = filtered.filter(deal => deal.listing_type === filters.listing_type);
    }

    // Apply minimum score filter
    if (filters.min_score > 0) {
      filtered = filtered.filter(deal => deal.deal_score >= filters.min_score);
    }

    // Sort deals
    filtered.sort((a, b) => {
      switch (filters.sort_by) {
        case 'score':
          return b.deal_score - a.deal_score;
        case 'discount':
          return b.discount_pct - a.discount_pct;
        case 'price':
          return a.current_price - b.current_price;
        default:
          return 0;
      }
    });

    setFilteredDeals(filtered);
  };

  const handleDealClick = (deal: Deal) => {
    // Navigate to the appropriate page based on listing type
    if (deal.listing_type === 'flight') {
      navigate(`/flights?flight_id=${deal.listing_id}`);
    } else if (deal.listing_type === 'hotel') {
      navigate(`/hotels?hotel_id=${deal.listing_id}`);
    } else if (deal.listing_type === 'car') {
      navigate(`/cars?car_id=${deal.listing_id}`);
    }
  };

  const getDealIcon = (type: string) => {
    switch (type) {
      case 'flight':
        return <Plane className="w-5 h-5" />;
      case 'hotel':
        return <Hotel className="w-5 h-5" />;
      case 'car':
        return <Car className="w-5 h-5" />;
      default:
        return <Tag className="w-5 h-5" />;
    }
  };

  const getDealColor = (type: string) => {
    switch (type) {
      case 'flight':
        return 'from-blue-500 to-blue-600';
      case 'hotel':
        return 'from-purple-500 to-purple-600';
      case 'car':
        return 'from-green-500 to-green-600';
      default:
        return 'from-slate-500 to-slate-600';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-green-600 bg-green-100';
    if (score >= 50) return 'text-blue-600 bg-blue-100';
    if (score >= 30) return 'text-orange-600 bg-orange-100';
    return 'text-slate-600 bg-slate-100';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-3 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl shadow-lg">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-slate-900">Exclusive Deals</h1>
              <p className="text-slate-600 mt-1">Save big on flights, hotels, and car rentals</p>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="mb-6">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-4 py-2 bg-white border-2 border-slate-300 rounded-xl text-slate-700 font-semibold hover:border-slate-400 transition-all"
          >
            <Filter className="w-5 h-5" />
            <span>Filters</span>
            {showFilters && <X className="w-4 h-4" />}
          </button>

          {showFilters && (
            <div className="mt-4 p-6 bg-white border-2 border-slate-300 rounded-xl shadow-lg">
              <div className="grid md:grid-cols-3 gap-6">
                {/* Listing Type Filter */}
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">
                    Category
                  </label>
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => setFilters({ ...filters, listing_type: undefined })}
                      className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                        !filters.listing_type
                          ? 'bg-gradient-to-r from-slate-700 to-slate-800 text-white shadow-md'
                          : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                      }`}
                    >
                      All
                    </button>
                    <button
                      onClick={() => setFilters({ ...filters, listing_type: 'flight' })}
                      className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center space-x-2 ${
                        filters.listing_type === 'flight'
                          ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-md'
                          : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                      }`}
                    >
                      <Plane className="w-4 h-4" />
                      <span>Flights</span>
                    </button>
                    <button
                      onClick={() => setFilters({ ...filters, listing_type: 'hotel' })}
                      className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center space-x-2 ${
                        filters.listing_type === 'hotel'
                          ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-md'
                          : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                      }`}
                    >
                      <Hotel className="w-4 h-4" />
                      <span>Hotels</span>
                    </button>
                    <button
                      onClick={() => setFilters({ ...filters, listing_type: 'car' })}
                      className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center space-x-2 ${
                        filters.listing_type === 'car'
                          ? 'bg-gradient-to-r from-green-600 to-green-700 text-white shadow-md'
                          : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                      }`}
                    >
                      <Car className="w-4 h-4" />
                      <span>Cars</span>
                    </button>
                  </div>
                </div>

                {/* Minimum Score Filter */}
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">
                    Minimum Deal Score: {filters.min_score}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={filters.min_score}
                    onChange={(e) => setFilters({ ...filters, min_score: parseInt(e.target.value) })}
                    className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-slate-500 mt-1">
                    <span>0</span>
                    <span>100</span>
                  </div>
                </div>

                {/* Sort By */}
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">
                    Sort By
                  </label>
                  <select
                    value={filters.sort_by}
                    onChange={(e) => setFilters({ ...filters, sort_by: e.target.value as any })}
                    className="w-full px-4 py-2 border-2 border-slate-300 rounded-lg text-slate-700 font-semibold focus:border-slate-700 focus:outline-none"
                  >
                    <option value="score">Deal Score</option>
                    <option value="discount">Discount %</option>
                    <option value="price">Price (Low to High)</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border-2 border-red-200 rounded-xl flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
            <p className="text-red-700">{error}</p>
            <button
              onClick={loadDeals}
              className="ml-auto px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-semibold hover:bg-red-700 transition-colors"
            >
              Retry
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
            <span className="ml-3 text-slate-700 font-semibold">Loading amazing deals...</span>
          </div>
        )}

        {/* Deals Grid */}
        {!loading && !error && (
          <>
            <div className="mb-6 flex items-center justify-between">
              <p className="text-slate-600">
                Found <span className="font-bold text-slate-900">{filteredDeals.length}</span> deals
              </p>
            </div>

            {filteredDeals.length === 0 ? (
              <div className="text-center py-20">
                <TrendingDown className="w-16 h-16 text-slate-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-slate-700 mb-2">No deals found</h3>
                <p className="text-slate-600">Try adjusting your filters to see more deals</p>
              </div>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredDeals.map((deal) => (
                  <div
                    key={`${deal.listing_type}-${deal.listing_id}`}
                    onClick={() => handleDealClick(deal)}
                    className="bg-white border-2 border-slate-300 rounded-xl p-6 cursor-pointer hover:shadow-xl hover:border-slate-400 transition-all duration-300 group"
                  >
                    {/* Deal Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className={`p-3 bg-gradient-to-br ${getDealColor(deal.listing_type)} rounded-lg text-white`}>
                        {getDealIcon(deal.listing_type)}
                      </div>
                      <div className={`px-3 py-1 rounded-full text-xs font-bold ${getScoreColor(deal.deal_score)}`}>
                        Score: {deal.deal_score.toFixed(1)}
                      </div>
                    </div>

                    {/* Deal Info */}
                    <div className="mb-4">
                      <h3 className="text-lg font-bold text-slate-900 mb-2 capitalize">
                        {deal.listing_type} Deal
                      </h3>
                      <p className="text-sm text-slate-600 font-semibold">
                        ID: {deal.listing_id}
                      </p>
                    </div>

                    {/* Price Info */}
                    <div className="mb-4 p-4 bg-slate-50 rounded-lg">
                      <div className="flex items-baseline justify-between mb-2">
                        <span className="text-sm text-slate-600">Current Price</span>
                        <span className="text-2xl font-bold text-slate-900">
                          ${deal.current_price.toFixed(2)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-slate-500 line-through">
                          ${deal.avg_price.toFixed(2)}
                        </span>
                        <span className="text-sm font-bold text-green-600 flex items-center space-x-1">
                          <TrendingDown className="w-4 h-4" />
                          <span>{deal.discount_pct.toFixed(1)}% OFF</span>
                        </span>
                      </div>
                    </div>

                    {/* Tags */}
                    {deal.tags && deal.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-4">
                        {deal.tags.slice(0, 3).map((tag, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded-full"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* View Deal Button */}
                    <button 
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDealClick(deal);
                      }}
                      className="w-full mt-4 px-4 py-2 bg-gradient-to-r from-slate-700 to-slate-800 text-white rounded-lg font-semibold hover:from-slate-800 hover:to-slate-900 transition-all flex items-center justify-center space-x-2 group-hover:shadow-lg"
                    >
                      <span>View Deal</span>
                      <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default DealsPage;

