import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Plane, Hotel, Car, User, LayoutDashboard, Menu, X, Sparkles } from 'lucide-react';

const Navbar: React.FC = () => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className={`sticky top-0 z-50 transition-all duration-300 ${
      scrolled
        ? 'glass border-b border-white/20 shadow-lg'
        : 'bg-white/80 backdrop-blur-md border-b border-slate-200/50 shadow-sm'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-center items-center h-16 relative">
          {/* Logo - Centered */}
          <Link to="/" className="absolute left-0 flex items-center space-x-2.5 group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-slate-700 to-slate-800 rounded-lg blur-md opacity-0 group-hover:opacity-40 transition-opacity duration-300"></div>
              <span className="relative text-2xl font-black gradient-text tracking-tight group-hover:scale-105 transition-transform duration-300 inline-block">
                KAYAK
              </span>
            </div>
            <span className="text-xs text-slate-500 font-medium bg-slate-100 px-2 py-1 rounded">Beta</span>
          </Link>
          
          {/* Desktop Navigation Links - Centered */}
          <div className="hidden md:flex items-center justify-center space-x-1 mx-auto">
            <NavLink to="/flights" icon={<Plane size={16} />} active={isActive('/flights')}>
              Flights
            </NavLink>
            <NavLink to="/hotels" icon={<Hotel size={16} />} active={isActive('/hotels')}>
              Hotels
            </NavLink>
            <NavLink to="/cars" icon={<Car size={16} />} active={isActive('/cars')}>
              Cars
            </NavLink>
            <NavLink to="/billing" icon={<Car size={16} />} active={isActive('/billing')}>
              Billing
            </NavLink>
          </div>
          
          {/* Desktop User Menu - Right Aligned */}
          <div className="hidden md:flex items-center space-x-6 absolute right-0">
            <Link
              to="/bookings"
              className="text-sm text-slate-700 hover:text-slate-900 transition-all font-semibold relative group"
            >
              <span>My Trips</span>
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-slate-700 group-hover:w-full transition-all duration-300"></span>
            </Link>
            <Link
              to="/admin"
              className="flex items-center space-x-1.5 text-sm text-slate-700 hover:text-slate-900 transition-all font-semibold group"
            >
              <LayoutDashboard size={16} className="group-hover:rotate-12 transition-transform" />
              <span>Admin</span>
            </Link>
            <Link
              to="/login"
              className="flex items-center space-x-2 btn-primary py-2 px-5 text-sm group relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
              <User size={16} className="relative z-10" />
              <span className="relative z-10">Sign In</span>
              <Sparkles size={14} className="relative z-10 group-hover:rotate-180 transition-transform duration-500" />
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 text-slate-600 hover:text-blue-600 transition-colors rounded-lg hover:bg-blue-50"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-slate-200/50 animate-slide-down">
            <div className="flex flex-col items-center space-y-3">
              <MobileNavLink to="/flights" icon={<Plane size={18} />} active={isActive('/flights')} onClick={() => setMobileMenuOpen(false)}>
                Flights
              </MobileNavLink>
              <MobileNavLink to="/hotels" icon={<Hotel size={18} />} active={isActive('/hotels')} onClick={() => setMobileMenuOpen(false)}>
                Hotels
              </MobileNavLink>
              <MobileNavLink to="/cars" icon={<Car size={18} />} active={isActive('/cars')} onClick={() => setMobileMenuOpen(false)}>
                Cars
              </MobileNavLink>
              <div className="pt-4 border-t border-slate-200 space-y-3 w-full flex flex-col items-center">
                <Link to="/bookings" className="block text-slate-700 hover:text-blue-600 font-semibold text-center transition-colors" onClick={() => setMobileMenuOpen(false)}>
                  My Trips
                </Link>
                <Link to="/admin" className="flex items-center space-x-2 text-slate-700 hover:text-blue-600 font-semibold transition-colors" onClick={() => setMobileMenuOpen(false)}>
                  <LayoutDashboard size={18} />
                  <span>Admin</span>
                </Link>
                <Link to="/login" className="btn-primary px-6 py-2.5 text-sm flex items-center space-x-2" onClick={() => setMobileMenuOpen(false)}>
                  <User size={18} />
                  <span>Sign In</span>
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

interface NavLinkProps {
  to: string;
  icon: React.ReactNode;
  active: boolean;
  children: React.ReactNode;
}

const NavLink: React.FC<NavLinkProps> = ({ to, icon, active, children }) => (
  <Link
    to={to}
    className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-300 group ${
      active
        ? 'text-white bg-gradient-to-r from-slate-700 to-slate-800 shadow-md shadow-slate-400/20'
        : 'text-slate-700 hover:text-slate-900 hover:bg-slate-50/50'
    }`}
  >
    <span className={`transition-transform ${active ? '' : 'group-hover:scale-110'}`}>{icon}</span>
    <span>{children}</span>
  </Link>
);

interface MobileNavLinkProps {
  to: string;
  icon: React.ReactNode;
  active: boolean;
  children: React.ReactNode;
  onClick: () => void;
}

const MobileNavLink: React.FC<MobileNavLinkProps> = ({ to, icon, active, children, onClick }) => (
  <Link
    to={to}
    onClick={onClick}
    className={`flex items-center space-x-2.5 px-4 py-2.5 rounded-xl font-semibold transition-all duration-300 ${
      active
        ? 'text-white bg-gradient-to-r from-slate-700 to-slate-800 shadow-md shadow-slate-400/20'
        : 'text-slate-700 hover:text-slate-900 hover:bg-slate-50'
    }`}
  >
    {icon}
    <span>{children}</span>
  </Link>
);

export default Navbar;

