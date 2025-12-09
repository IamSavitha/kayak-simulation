import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Pages
import HomePage from './pages/HomePage';
import FlightsPage from './pages/FlightsPage';
import HotelsPage from './pages/HotelsPage';
import CarsPage from './pages/CarsPage';
import DealsPage from './pages/DealsPage';
import BundlesPage from './pages/BundlesPage';
import ChatPage from './pages/ChatPage';
import UnifiedSearchPage from './pages/UnifiedSearchPage';
import BookingsPage from './pages/BookingsPage';
import ProfilePage from './pages/ProfilePage';
import AdminDashboard from './pages/AdminDashboard';
import AdminLoginPage from './pages/AdminLoginPage';
import AdminSignupPage from './pages/AdminSignupPage';
import AdminFlightManagement from './pages/AdminFlightManagement';
import AdminHotelManagement from './pages/AdminHotelManagement';
import AdminCarManagement from './pages/AdminCarManagement';
import AdminBookingsManagement from './pages/AdminBookingsManagement';
import AdminAnalyticsPage from './pages/AdminAnalyticsPage';
import BillingDetailsPage from './pages/BillingDetailsPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';

// Components
import Navbar from './components/Navbar';
import Footer from './components/Footer';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <div className="min-h-screen bg-white flex flex-col">
          <Navbar />
          <main className="flex-grow">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/flights" element={<FlightsPage />} />
              <Route path="/hotels" element={<HotelsPage />} />
              <Route path="/cars" element={<CarsPage />} />
              <Route path="/deals" element={<DealsPage />} />
              <Route path="/bundles" element={<BundlesPage />} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/search" element={<UnifiedSearchPage />} />
              <Route path="/bookings" element={<BookingsPage />} />
              <Route path="/billing" element={<BillingDetailsPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/admin/dashboard" element={<AdminDashboard />} />
              <Route path="/admin/login" element={<AdminLoginPage />} />
              <Route path="/admin/signup" element={<AdminSignupPage />} />
              <Route path="/admin/flights" element={<AdminFlightManagement />} />
              <Route path="/admin/hotels" element={<AdminHotelManagement />} />
              <Route path="/admin/cars" element={<AdminCarManagement />} />
              <Route path="/admin/bookings" element={<AdminBookingsManagement />} />
              <Route path="/admin/analytics" element={<AdminAnalyticsPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<SignupPage />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;

