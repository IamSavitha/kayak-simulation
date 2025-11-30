import React from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import {
  HiUsers,
  HiCollection,
  HiCurrencyDollar,
  HiTrendingUp,
  HiArrowUp,
  HiArrowDown,
  HiTicket,
} from 'react-icons/hi';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import { adminService } from '../../services/api';
import { getDashboardStats, mockBillingService } from '../../services/mockData';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const AdminDashboard: React.FC = () => {
  // Use mock stats for now until backend is connected
  const mockStats = getDashboardStats();

  const { data: stats } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      try {
        return await adminService.getDashboardStats();
      } catch {
        // Return mock data if API fails
        return mockStats;
      }
    },
  });

  const { data: topProperties } = useQuery({
    queryKey: ['top-properties'],
    queryFn: async () => {
      try {
        return await adminService.getTopProperties();
      } catch {
        // Return mock data
        return [
          { name: 'Marriott Times Square', revenue: 125000 },
          { name: 'Hilton Downtown', revenue: 98000 },
          { name: 'Grand Hyatt', revenue: 87000 },
          { name: 'Sheraton LA', revenue: 76000 },
          { name: 'Westin SF', revenue: 65000 },
        ];
      }
    },
  });

  const { data: cityRevenue } = useQuery({
    queryKey: ['city-revenue'],
    queryFn: async () => {
      try {
        return await adminService.getCityRevenue();
      } catch {
        // Return mock data
        return mockBillingService.getRevenueByCity(2025);
      }
    },
  });

  const statCards = [
    {
      title: 'Total Users',
      value: stats?.total_users?.toLocaleString() || '10,234',
      change: '+12%',
      isPositive: true,
      icon: HiUsers,
      color: 'from-primary-500 to-primary-600',
    },
    {
      title: 'Active Listings',
      value: stats?.active_listings?.toLocaleString() || '3,456',
      change: '+8%',
      isPositive: true,
      icon: HiCollection,
      color: 'from-secondary-500 to-secondary-600',
    },
    {
      title: 'Total Revenue',
      value: `$${(stats?.total_revenue || 543210).toLocaleString()}`,
      change: '+23%',
      isPositive: true,
      icon: HiCurrencyDollar,
      color: 'from-accent-emerald to-teal-500',
    },
    {
      title: 'Total Bookings',
      value: stats?.total_bookings?.toLocaleString() || '12,789',
      change: '-3%',
      isPositive: false,
      icon: HiTrendingUp,
      color: 'from-accent-purple to-purple-600',
    },
  ];

  // Chart data for Top Properties
  const barChartData = {
    labels: topProperties?.properties?.slice(0, 5).map((p: any) => p.property_name) || 
      ['Property 1', 'Property 2', 'Property 3', 'Property 4', 'Property 5'],
    datasets: [
      {
        label: 'Revenue ($)',
        data: topProperties?.properties?.slice(0, 5).map((p: any) => p.revenue) || 
          [10000, 8500, 7200, 6800, 5500],
        backgroundColor: 'rgba(249, 168, 37, 0.8)',
        borderColor: 'rgba(249, 168, 37, 1)',
        borderWidth: 1,
        borderRadius: 8,
      },
    ],
  };

  // Chart data for City Revenue
  const pieChartData = {
    labels: cityRevenue?.cities?.slice(0, 5).map((c: any) => c.city) || 
      ['New York', 'Los Angeles', 'San Francisco', 'Miami', 'Las Vegas'],
    datasets: [
      {
        data: cityRevenue?.cities?.slice(0, 5).map((c: any) => c.revenue) || 
          [50000, 45000, 40000, 35000, 30000],
        backgroundColor: [
          'rgba(249, 168, 37, 0.8)',
          'rgba(62, 167, 232, 0.8)',
          'rgba(168, 85, 247, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(255, 107, 107, 0.8)',
        ],
        borderWidth: 0,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#9ca3af',
        },
      },
    },
    scales: {
      x: {
        ticks: { color: '#9ca3af' },
        grid: { color: 'rgba(75, 85, 99, 0.2)' },
      },
      y: {
        ticks: { color: '#9ca3af' },
        grid: { color: 'rgba(75, 85, 99, 0.2)' },
      },
    },
  };

  return (
    <div className="space-y-8">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card p-6"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-gray-400 text-sm mb-1">{stat.title}</p>
                <p className="text-2xl font-bold text-white">{stat.value}</p>
                <div className={`flex items-center mt-2 text-sm ${
                  stat.isPositive ? 'text-accent-emerald' : 'text-accent-coral'
                }`}>
                  {stat.isPositive ? (
                    <HiArrowUp className="w-4 h-4 mr-1" />
                  ) : (
                    <HiArrowDown className="w-4 h-4 mr-1" />
                  )}
                  {stat.change} from last month
                </div>
              </div>
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Properties Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card p-6"
        >
          <h3 className="text-lg font-semibold text-white mb-6">
            Top 5 Properties by Revenue
          </h3>
          <div className="h-64">
            <Bar data={barChartData} options={chartOptions} />
          </div>
        </motion.div>

        {/* City Revenue Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="card p-6"
        >
          <h3 className="text-lg font-semibold text-white mb-6">
            Revenue by City
          </h3>
          <div className="h-64">
            <Pie data={pieChartData} options={{ ...chartOptions, scales: undefined }} />
          </div>
        </motion.div>
      </div>

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="card p-6"
      >
        <h3 className="text-lg font-semibold text-white mb-6">Recent Activity</h3>
        <div className="space-y-4">
          {[
            { action: 'New user registered', user: 'John Doe', time: '2 minutes ago', type: 'user' },
            { action: 'Booking confirmed', user: 'Jane Smith', time: '15 minutes ago', type: 'booking' },
            { action: 'New listing added', user: 'Admin', time: '1 hour ago', type: 'listing' },
            { action: 'Payment received', user: 'Mike Johnson', time: '2 hours ago', type: 'payment' },
          ].map((activity, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-dark-800 rounded-xl">
              <div className="flex items-center space-x-4">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  activity.type === 'user' ? 'bg-primary-500/20 text-primary-400' :
                  activity.type === 'booking' ? 'bg-secondary-500/20 text-secondary-400' :
                  activity.type === 'listing' ? 'bg-accent-purple/20 text-accent-purple' :
                  'bg-accent-emerald/20 text-accent-emerald'
                }`}>
                  {activity.type === 'user' && <HiUsers className="w-5 h-5" />}
                  {activity.type === 'booking' && <HiCollection className="w-5 h-5" />}
                  {activity.type === 'listing' && <HiCollection className="w-5 h-5" />}
                  {activity.type === 'payment' && <HiCurrencyDollar className="w-5 h-5" />}
                </div>
                <div>
                  <p className="text-white font-medium">{activity.action}</p>
                  <p className="text-gray-400 text-sm">by {activity.user}</p>
                </div>
              </div>
              <span className="text-gray-500 text-sm">{activity.time}</span>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default AdminDashboard;


