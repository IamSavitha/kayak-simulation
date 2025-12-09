import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, DollarSign, BarChart3, PieChart as PieChartIcon, ArrowLeft, Calendar, MapPin } from 'lucide-react';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const API_BASE_URL = 'http://localhost:8006'; // Admin service port

interface PropertyRevenue {
  listing_id: string;
  type: string;
  revenue: number;
  bookings: number;
}

interface CityRevenue {
  city: string;
  revenue: number;
}

interface ProviderData {
  provider: string;
  sales: number;
  revenue: number;
}

interface RevenueAnalytics {
  period: string;
  total_revenue: number;
  total_transactions: number;
  by_type: Array<{
    type: string;
    revenue: number;
    count: number;
  }>;
}

const AdminAnalyticsPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [year, setYear] = useState(new Date().getFullYear());
  
  // Data states
  const [topProperties, setTopProperties] = useState<PropertyRevenue[]>([]);
  const [cityRevenue, setCityRevenue] = useState<CityRevenue[]>([]);
  const [topProviders, setTopProviders] = useState<ProviderData[]>([]);
  const [revenueAnalytics, setRevenueAnalytics] = useState<RevenueAnalytics | null>(null);

  // Chart colors
  const COLORS = [
    '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
    '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#84cc16'
  ];

  useEffect(() => {
    const adminToken = localStorage.getItem('admin_token');
    const isAdmin = localStorage.getItem('is_admin');

    if (!adminToken || isAdmin !== 'true') {
      navigate('/admin/login');
      return;
    }

    loadAnalyticsData();
  }, [navigate, year]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    const adminToken = localStorage.getItem('admin_token');

    try {
      // Load top properties
      const propertiesRes = await fetch(
        `${API_BASE_URL}/analytics/top-properties?limit=10&year=${year}`,
        {
          headers: { Authorization: `Bearer ${adminToken}` }
        }
      );
      if (propertiesRes.ok) {
        const data = await propertiesRes.json();
        setTopProperties(data);
      }

      // Load city revenue
      const cityRes = await fetch(
        `${API_BASE_URL}/analytics/city-revenue?year=${year}`,
        {
          headers: { Authorization: `Bearer ${adminToken}` }
        }
      );
      if (cityRes.ok) {
        const data = await cityRes.json();
        // Sort and take top 10
        const sorted = data.sort((a: CityRevenue, b: CityRevenue) => b.revenue - a.revenue).slice(0, 10);
        setCityRevenue(sorted);
      }

      // Load top providers
      const providersRes = await fetch(
        `${API_BASE_URL}/analytics/top-providers?limit=10&year=${year}`,
        {
          headers: { Authorization: `Bearer ${adminToken}` }
        }
      );
      if (providersRes.ok) {
        const data = await providersRes.json();
        setTopProviders(data);
      }

      // Load revenue analytics
      const revenueRes = await fetch(
        `${API_BASE_URL}/analytics/revenue?period=monthly&year=${year}`,
        {
          headers: { Authorization: `Bearer ${adminToken}` }
        }
      );
      if (revenueRes.ok) {
        const data = await revenueRes.json();
        setRevenueAnalytics(data);
      }
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  // Format currency
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  // Custom tooltip for charts
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border-2 border-slate-200">
          <p className="font-semibold text-slate-900">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {entry.name}: {typeof entry.value === 'number' ? formatCurrency(entry.value) : entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-white to-slate-100/30">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-600 mx-auto"></div>
          <p className="mt-4 text-slate-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/admin/dashboard')}
            className="mb-4 flex items-center text-blue-600 hover:text-blue-700 font-medium"
          >
            <ArrowLeft size={20} className="mr-2" />
            Back to Dashboard
          </button>
          
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-slate-900 flex items-center">
                <BarChart3 className="mr-3 text-slate-600" size={36} />
                Analytics & Reports
              </h1>
              <p className="mt-2 text-slate-600">
                Comprehensive revenue and performance analytics
              </p>
            </div>
            
            {/* Year Selector */}
            <div className="flex items-center space-x-2">
              <Calendar className="text-slate-600" size={20} />
              <select
                value={year}
                onChange={(e) => setYear(Number(e.target.value))}
                className="px-4 py-2 border-2 border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {[2025, 2024, 2023, 2022].map(y => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Revenue Overview Cards */}
        {revenueAnalytics && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm mb-1">Total Revenue</p>
                  <p className="text-3xl font-bold">{formatCurrency(revenueAnalytics.total_revenue)}</p>
                </div>
                <DollarSign size={40} className="text-blue-200" />
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100 text-sm mb-1">Total Transactions</p>
                  <p className="text-3xl font-bold">{revenueAnalytics.total_transactions.toLocaleString()}</p>
                </div>
                <TrendingUp size={40} className="text-green-200" />
              </div>
            </div>

            <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl shadow-lg p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-orange-100 text-sm mb-1">Avg Transaction</p>
                  <p className="text-3xl font-bold">
                    {formatCurrency(revenueAnalytics.total_revenue / revenueAnalytics.total_transactions || 0)}
                  </p>
                </div>
                <BarChart3 size={40} className="text-orange-200" />
              </div>
            </div>
          </div>
        )}

        {/* Top 10 Properties Revenue - Bar Chart */}
        <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-slate-200 mb-8">
          <div className="flex items-center mb-6">
            <BarChart3 className="text-blue-600 mr-3" size={24} />
            <h2 className="text-2xl font-bold text-slate-900">Top 10 Properties by Revenue</h2>
          </div>
          
          {topProperties.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={topProperties}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="listing_id" 
                  angle={-45}
                  textAnchor="end"
                  height={100}
                />
                <YAxis 
                  tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                />
                <Tooltip content={CustomTooltip} />
                <Legend />
                <Bar dataKey="revenue" fill="#3b82f6" name="Revenue" />
                <Bar dataKey="bookings" fill="#10b981" name="Bookings" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center py-12 text-slate-600">
              <BarChart3 className="w-16 h-16 mx-auto mb-4 text-slate-400" />
              <p>No property data available for {year}</p>
            </div>
          )}
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* City Revenue - Pie Chart */}
          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-slate-200">
            <div className="flex items-center mb-6">
              <PieChartIcon className="text-green-600 mr-3" size={24} />
              <h2 className="text-2xl font-bold text-slate-900">City-wise Revenue</h2>
            </div>
            
            {cityRevenue.length > 0 ? (
              <ResponsiveContainer width="100%" height={350}>
                <PieChart>
                  <Pie
                    data={cityRevenue}
                    dataKey="revenue"
                    nameKey="city"
                    cx="50%"
                    cy="50%"
                    outerRadius={120}
                    label={(entry) => `${entry.city}: ${formatCurrency(entry.revenue)}`}
                  >
                    {cityRevenue.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip content={CustomTooltip} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center py-12 text-slate-600">
                <MapPin className="w-16 h-16 mx-auto mb-4 text-slate-400" />
                <p>No city data available for {year}</p>
              </div>
            )}
          </div>

          {/* Revenue by Type - Pie Chart */}
          {revenueAnalytics && revenueAnalytics.by_type.length > 0 && (
            <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-slate-200">
              <div className="flex items-center mb-6">
                <PieChartIcon className="text-purple-600 mr-3" size={24} />
                <h2 className="text-2xl font-bold text-slate-900">Revenue by Booking Type</h2>
              </div>
              
              <ResponsiveContainer width="100%" height={350}>
                <PieChart>
                  <Pie
                    data={revenueAnalytics.by_type}
                    dataKey="revenue"
                    nameKey="type"
                    cx="50%"
                    cy="50%"
                    outerRadius={120}
                    label={(entry) => `${entry.type}: ${formatCurrency(entry.revenue)}`}
                  >
                    {revenueAnalytics.by_type.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip content={CustomTooltip} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Top 10 Providers/Hosts - Bar Chart */}
        <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-slate-200">
          <div className="flex items-center mb-6">
            <TrendingUp className="text-orange-600 mr-3" size={24} />
            <h2 className="text-2xl font-bold text-slate-900">Top 10 Providers by Sales</h2>
          </div>
          
          {topProviders.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={topProviders}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="provider" 
                  angle={-45}
                  textAnchor="end"
                  height={100}
                />
                <YAxis 
                  yAxisId="left"
                  tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                />
                <YAxis 
                  yAxisId="right"
                  orientation="right"
                />
                <Tooltip content={CustomTooltip} />
                <Legend />
                <Bar yAxisId="left" dataKey="revenue" fill="#f59e0b" name="Revenue" />
                <Bar yAxisId="right" dataKey="sales" fill="#8b5cf6" name="Sales Count" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center py-12 text-slate-600">
              <TrendingUp className="w-16 h-16 mx-auto mb-4 text-slate-400" />
              <p>No provider data available for {year}</p>
            </div>
          )}
        </div>

        {/* Summary Table */}
        <div className="mt-8 bg-white rounded-xl shadow-lg p-6 border-2 border-slate-200">
          <h2 className="text-2xl font-bold text-slate-900 mb-4">Top Properties Details</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-slate-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Rank</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Property ID</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Type</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-slate-700">Revenue</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-slate-700">Bookings</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-slate-700">Avg/Booking</th>
                </tr>
              </thead>
              <tbody>
                {topProperties.map((property, index) => (
                  <tr key={property.listing_id} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="py-3 px-4 text-sm font-bold text-slate-900">{index + 1}</td>
                    <td className="py-3 px-4 text-sm text-slate-900 font-mono">{property.listing_id}</td>
                    <td className="py-3 px-4 text-sm text-slate-700 capitalize">{property.type}</td>
                    <td className="py-3 px-4 text-sm text-slate-900 font-semibold text-right">
                      {formatCurrency(property.revenue)}
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-700 text-right">
                      {property.bookings}
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-700 text-right">
                      {formatCurrency(property.revenue / property.bookings)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminAnalyticsPage;
