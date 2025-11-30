import React from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
} from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';
import { HiDownload, HiCalendar } from 'react-icons/hi';
import { adminService } from '../../services/api';
import { mockBillingService } from '../../services/mockData';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
);

const AdminReports: React.FC = () => {
  const [selectedYear, setSelectedYear] = React.useState(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = React.useState(new Date().getMonth() + 1);

  const { data: topProperties } = useQuery({
    queryKey: ['top-properties', selectedYear],
    queryFn: async () => {
      try {
        return await adminService.getTopProperties(selectedYear);
      } catch {
        // Return mock data when API fails
        return {
          properties: [
            { property_name: 'Marriott Times Square', revenue: 125000 },
            { property_name: 'Hilton Downtown', revenue: 98000 },
            { property_name: 'Grand Hyatt NYC', revenue: 87000 },
            { property_name: 'Sheraton LA', revenue: 76000 },
            { property_name: 'Westin SF', revenue: 65000 },
            { property_name: 'Ritz Carlton Miami', revenue: 58000 },
            { property_name: 'Four Seasons Chicago', revenue: 52000 },
            { property_name: 'W Hotel Seattle', revenue: 48000 },
            { property_name: 'Hyatt Boston', revenue: 44000 },
            { property_name: 'Marriott Denver', revenue: 40000 },
          ],
          total_revenue: 693000,
        };
      }
    },
  });

  const { data: cityRevenue } = useQuery({
    queryKey: ['city-revenue', selectedYear],
    queryFn: async () => {
      try {
        return await adminService.getCityRevenue(selectedYear);
      } catch {
        const mockCities = await mockBillingService.getRevenueByCity(selectedYear);
        return { cities: mockCities };
      }
    },
  });

  const { data: providerAnalysis } = useQuery({
    queryKey: ['provider-analysis', selectedMonth, selectedYear],
    queryFn: async () => {
      try {
        return await adminService.getProviderAnalysis(selectedMonth, selectedYear);
      } catch {
        // Return mock provider data
        return {
          providers: [
            { provider_name: 'Marriott Int.', properties_sold: 50, revenue: 125000 },
            { provider_name: 'Hilton Hotels', properties_sold: 45, revenue: 110000 },
            { provider_name: 'Hyatt Corp', properties_sold: 42, revenue: 95000 },
            { provider_name: 'IHG Hotels', properties_sold: 38, revenue: 85000 },
            { provider_name: 'Wyndham', properties_sold: 35, revenue: 78000 },
            { provider_name: 'Choice Hotels', properties_sold: 32, revenue: 72000 },
            { provider_name: 'Best Western', properties_sold: 30, revenue: 65000 },
            { provider_name: 'Radisson', properties_sold: 28, revenue: 58000 },
            { provider_name: 'Accor Hotels', properties_sold: 25, revenue: 52000 },
            { provider_name: 'MGM Resorts', properties_sold: 22, revenue: 48000 },
          ],
        };
      }
    },
  });

  // Top 10 Properties Chart
  const propertiesChartData = {
    labels: topProperties?.properties?.map((p: any) => p.property_name.slice(0, 15)) || 
      Array.from({ length: 10 }, (_, i) => `Property ${i + 1}`),
    datasets: [
      {
        label: 'Revenue ($)',
        data: topProperties?.properties?.map((p: any) => p.revenue) || 
          [10000, 9000, 8500, 7800, 7200, 6800, 6200, 5800, 5400, 5000],
        backgroundColor: 'rgba(249, 168, 37, 0.8)',
        borderColor: 'rgba(249, 168, 37, 1)',
        borderWidth: 1,
        borderRadius: 8,
      },
    ],
  };

  // City Revenue Pie Chart
  const cityChartData = {
    labels: cityRevenue?.cities?.slice(0, 8).map((c: any) => c.city) || 
      ['New York', 'Los Angeles', 'San Francisco', 'Miami', 'Las Vegas', 'Chicago', 'Seattle', 'Boston'],
    datasets: [
      {
        data: cityRevenue?.cities?.slice(0, 8).map((c: any) => c.revenue) || 
          [50000, 45000, 40000, 35000, 30000, 28000, 25000, 22000],
        backgroundColor: [
          'rgba(249, 168, 37, 0.8)',
          'rgba(62, 167, 232, 0.8)',
          'rgba(168, 85, 247, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(255, 107, 107, 0.8)',
          'rgba(78, 205, 196, 0.8)',
          'rgba(255, 177, 66, 0.8)',
          'rgba(99, 102, 241, 0.8)',
        ],
        borderWidth: 0,
      },
    ],
  };

  // Provider Analysis Chart
  const providerChartData = {
    labels: providerAnalysis?.providers?.map((p: any) => p.provider_name.slice(0, 12)) || 
      Array.from({ length: 10 }, (_, i) => `Provider ${i + 1}`),
    datasets: [
      {
        label: 'Properties Sold',
        data: providerAnalysis?.providers?.map((p: any) => p.properties_sold) || 
          [50, 45, 42, 38, 35, 32, 30, 28, 25, 22],
        backgroundColor: 'rgba(62, 167, 232, 0.8)',
        borderColor: 'rgba(62, 167, 232, 1)',
        borderWidth: 1,
        borderRadius: 8,
      },
      {
        label: 'Revenue ($K)',
        data: providerAnalysis?.providers?.map((p: any) => p.revenue / 1000) || 
          [25, 22, 20, 18, 16, 15, 14, 13, 12, 11],
        backgroundColor: 'rgba(168, 85, 247, 0.8)',
        borderColor: 'rgba(168, 85, 247, 1)',
        borderWidth: 1,
        borderRadius: 8,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: { color: '#9ca3af' },
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
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">Analytics & Reports</h2>
          <p className="text-gray-400 text-sm">View detailed analytics and generate reports</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <HiCalendar className="w-5 h-5 text-gray-400" />
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              className="input py-2 text-sm"
            >
              {[2025, 2024, 2023].map((year) => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>
          <button className="btn-secondary">
            <HiDownload className="w-5 h-5 mr-2" />
            Export Report
          </button>
        </div>
      </div>

      {/* Top 10 Properties */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-white">Top 10 Properties by Revenue</h3>
            <p className="text-gray-400 text-sm">Year {selectedYear}</p>
          </div>
          <span className="text-primary-400 font-semibold">
            Total: ${topProperties?.total_revenue?.toLocaleString() || '75,000'}
          </span>
        </div>
        <div className="h-80">
          <Bar data={propertiesChartData} options={chartOptions} />
        </div>
      </motion.div>

      {/* City Revenue & Provider Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* City Revenue */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card p-6"
        >
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-white">City-wise Revenue</h3>
            <p className="text-gray-400 text-sm">Revenue distribution by city</p>
          </div>
          <div className="h-72">
            <Pie data={cityChartData} options={{ ...chartOptions, scales: undefined }} />
          </div>
        </motion.div>

        {/* Provider Analysis */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-white">Top 10 Providers</h3>
              <p className="text-gray-400 text-sm">Properties sold last month</p>
            </div>
            <select
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(Number(e.target.value))}
              className="input py-2 text-sm w-32"
            >
              {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].map((month, i) => (
                <option key={i} value={i + 1}>{month}</option>
              ))}
            </select>
          </div>
          <div className="h-72">
            <Bar data={providerChartData} options={chartOptions} />
          </div>
        </motion.div>
      </div>

      {/* Summary Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        <div className="card p-6">
          <h4 className="text-gray-400 text-sm mb-2">Total Revenue (YTD)</h4>
          <p className="text-3xl font-bold text-primary-400">
            ${topProperties?.total_revenue?.toLocaleString() || '543,210'}
          </p>
          <p className="text-accent-emerald text-sm mt-2">+23% from last year</p>
        </div>
        <div className="card p-6">
          <h4 className="text-gray-400 text-sm mb-2">Top Performing City</h4>
          <p className="text-3xl font-bold text-secondary-400">
            {cityRevenue?.cities?.[0]?.city || 'New York'}
          </p>
          <p className="text-gray-400 text-sm mt-2">
            ${cityRevenue?.cities?.[0]?.revenue?.toLocaleString() || '50,000'} revenue
          </p>
        </div>
        <div className="card p-6">
          <h4 className="text-gray-400 text-sm mb-2">Top Provider</h4>
          <p className="text-3xl font-bold text-accent-purple">
            {providerAnalysis?.providers?.[0]?.provider_name || 'Provider 1'}
          </p>
          <p className="text-gray-400 text-sm mt-2">
            {providerAnalysis?.providers?.[0]?.properties_sold || '50'} properties sold
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default AdminReports;


