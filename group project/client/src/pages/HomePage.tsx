import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaPlane, FaHotel, FaCar, FaStar, FaShieldAlt, FaClock } from 'react-icons/fa';
import { HiArrowRight, HiLocationMarker, HiCalendar } from 'react-icons/hi';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [searchType, setSearchType] = React.useState<'flights' | 'hotels' | 'cars'>('flights');

  const features = [
    {
      icon: FaStar,
      title: 'Best Prices',
      description: 'Compare prices from hundreds of travel sites at once.',
    },
    {
      icon: FaShieldAlt,
      title: 'Secure Booking',
      description: 'Your transactions are protected with bank-level security.',
    },
    {
      icon: FaClock,
      title: 'Price Alerts',
      description: 'Get notified when prices drop for your favorite routes.',
    },
  ];

  const popularDestinations = [
    { city: 'New York', country: 'USA', image: '🗽', price: '$199' },
    { city: 'Paris', country: 'France', image: '🗼', price: '$499' },
    { city: 'Tokyo', country: 'Japan', image: '🏯', price: '$799' },
    { city: 'Dubai', country: 'UAE', image: '🏙️', price: '$649' },
  ];

  return (
    <div className="overflow-hidden">
      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-hero-pattern opacity-30"></div>
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-500/20 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary-500/20 rounded-full blur-3xl"></div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center mb-12">
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-5xl md:text-7xl font-display font-bold text-white mb-6"
            >
              Find Your Next
              <span className="block gradient-text">Adventure</span>
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-xl text-gray-400 max-w-2xl mx-auto"
            >
              Search hundreds of travel sites at once. Compare flights, hotels, and car rentals.
            </motion.p>
          </div>

          {/* Search Box */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="max-w-4xl mx-auto"
          >
            <div className="card p-6">
              {/* Search Type Tabs */}
              <div className="flex space-x-2 mb-6">
                {[
                  { type: 'flights' as const, icon: FaPlane, label: 'Flights' },
                  { type: 'hotels' as const, icon: FaHotel, label: 'Hotels' },
                  { type: 'cars' as const, icon: FaCar, label: 'Cars' },
                ].map((tab) => (
                  <button
                    key={tab.type}
                    onClick={() => setSearchType(tab.type)}
                    className={`flex items-center space-x-2 px-5 py-3 rounded-xl font-medium transition-all duration-200 ${
                      searchType === tab.type
                        ? 'bg-primary-500 text-dark-950'
                        : 'bg-dark-800 text-gray-300 hover:bg-dark-700'
                    }`}
                  >
                    <tab.icon className="w-4 h-4" />
                    <span>{tab.label}</span>
                  </button>
                ))}
              </div>

              {/* Search Form */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="md:col-span-1">
                  <label className="label">From</label>
                  <div className="relative">
                    <HiLocationMarker className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                    <input
                      type="text"
                      placeholder="City or airport"
                      className="input pl-10"
                    />
                  </div>
                </div>
                <div className="md:col-span-1">
                  <label className="label">To</label>
                  <div className="relative">
                    <HiLocationMarker className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                    <input
                      type="text"
                      placeholder="City or airport"
                      className="input pl-10"
                    />
                  </div>
                </div>
                <div className="md:col-span-1">
                  <label className="label">Date</label>
                  <div className="relative">
                    <HiCalendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                    <input type="date" className="input pl-10" />
                  </div>
                </div>
                <div className="md:col-span-1 flex items-end">
                  <button
                    onClick={() => navigate(`/search/${searchType}`)}
                    className="btn-primary w-full"
                  >
                    Search
                    <HiArrowRight className="w-5 h-5 ml-2" />
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-dark-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-display font-bold text-white mb-4">
              Why Choose Us
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              We make travel planning simple, fast, and rewarding.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="card-hover p-8 text-center"
              >
                <div className="w-16 h-16 bg-gradient-to-br from-primary-500/20 to-secondary-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <feature.icon className="w-8 h-8 text-primary-400" />
                </div>
                <h3 className="text-xl font-display font-semibold text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-400">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Popular Destinations */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center mb-12">
            <div>
              <h2 className="text-3xl font-display font-bold text-white mb-2">
                Popular Destinations
              </h2>
              <p className="text-gray-400">Explore trending places to visit</p>
            </div>
            <Link to="/search" className="link flex items-center space-x-2">
              <span>View all</span>
              <HiArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {popularDestinations.map((dest, index) => (
              <motion.div
                key={dest.city}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="card-hover group overflow-hidden"
              >
                <div className="h-48 bg-gradient-to-br from-dark-700 to-dark-800 flex items-center justify-center text-6xl">
                  {dest.image}
                </div>
                <div className="p-5">
                  <h3 className="text-lg font-display font-semibold text-white mb-1">
                    {dest.city}
                  </h3>
                  <p className="text-gray-500 text-sm mb-3">{dest.country}</p>
                  <div className="flex justify-between items-center">
                    <span className="text-primary-400 font-semibold">
                      From {dest.price}
                    </span>
                    <button className="text-gray-400 hover:text-primary-400 transition-colors">
                      <HiArrowRight className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="card p-12 text-center bg-gradient-to-br from-primary-500/10 to-secondary-500/10 border-primary-500/20">
            <h2 className="text-3xl md:text-4xl font-display font-bold text-white mb-4">
              Ready to Start Your Journey?
            </h2>
            <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
              Join thousands of travelers who save money and time booking through Kayak.
            </p>
            <Link to="/register" className="btn-primary text-lg px-8 py-4">
              Create Free Account
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;


