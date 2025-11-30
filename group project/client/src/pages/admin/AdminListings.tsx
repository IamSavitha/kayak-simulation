import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { FaPlane, FaHotel, FaCar, FaStar } from 'react-icons/fa';
import {
  HiPlus,
  HiSearch,
  HiPencil,
  HiTrash,
  HiX,
  HiRefresh,
  HiCheck,
  HiExclamation,
} from 'react-icons/hi';
import { flightService, hotelService, carService } from '../../services/api';

// Types
type ListingType = 'flight' | 'hotel' | 'car';

interface FlightFormData {
  airline: string;
  departure_airport: string;
  arrival_airport: string;
  departure_date_time: string;
  arrival_date_time: string;
  duration_minutes: number;
  flight_class: 'Economy' | 'Business' | 'First';
  ticket_price: number;
  total_available_seats: number;
}

interface HotelFormData {
  hotel_name: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  star_rating: number;
  number_of_rooms: number;
  room_type: string;
  price_per_night: number;
  amenities: string;
}

interface CarFormData {
  car_type: string;
  company_provider_name: string;
  model_and_year: string;
  transmission_type: 'Automatic' | 'Manual';
  number_of_seats: number;
  daily_rental_price: number;
  location_city: string;
  location_state: string;
  location_address: string;
}

// Flight Form Component
const FlightForm: React.FC<{
  initialData?: any;
  onSubmit: (data: FlightFormData) => void;
  onCancel: () => void;
  isLoading: boolean;
}> = ({ initialData, onSubmit, onCancel, isLoading }) => {
  const [formData, setFormData] = useState<FlightFormData>({
    airline: initialData?.airline || '',
    departure_airport: initialData?.departure_airport || '',
    arrival_airport: initialData?.arrival_airport || '',
    departure_date_time: initialData?.departure_date_time?.slice(0, 16) || '',
    arrival_date_time: initialData?.arrival_date_time?.slice(0, 16) || '',
    duration_minutes: initialData?.duration_minutes || 0,
    flight_class: initialData?.flight_class || 'Economy',
    ticket_price: initialData?.ticket_price || 0,
    total_available_seats: initialData?.total_available_seats || 0,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">Airline</label>
          <input
            type="text"
            value={formData.airline}
            onChange={(e) => setFormData({ ...formData, airline: e.target.value })}
            className="input"
            placeholder="United Airlines"
            required
          />
        </div>
        <div>
          <label className="label">Flight Class</label>
          <select
            value={formData.flight_class}
            onChange={(e) => setFormData({ ...formData, flight_class: e.target.value as any })}
            className="input"
          >
            <option value="Economy">Economy</option>
            <option value="Business">Business</option>
            <option value="First">First</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">Departure Airport</label>
          <input
            type="text"
            value={formData.departure_airport}
            onChange={(e) => setFormData({ ...formData, departure_airport: e.target.value.toUpperCase() })}
            className="input"
            placeholder="SFO"
            maxLength={5}
            required
          />
        </div>
        <div>
          <label className="label">Arrival Airport</label>
          <input
            type="text"
            value={formData.arrival_airport}
            onChange={(e) => setFormData({ ...formData, arrival_airport: e.target.value.toUpperCase() })}
            className="input"
            placeholder="JFK"
            maxLength={5}
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">Departure Date & Time</label>
          <input
            type="datetime-local"
            value={formData.departure_date_time}
            onChange={(e) => setFormData({ ...formData, departure_date_time: e.target.value })}
            className="input"
            required
          />
        </div>
        <div>
          <label className="label">Arrival Date & Time</label>
          <input
            type="datetime-local"
            value={formData.arrival_date_time}
            onChange={(e) => setFormData({ ...formData, arrival_date_time: e.target.value })}
            className="input"
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="label">Duration (minutes)</label>
          <input
            type="number"
            value={formData.duration_minutes}
            onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) })}
            className="input"
            min={0}
            required
          />
        </div>
        <div>
          <label className="label">Ticket Price ($)</label>
          <input
            type="number"
            value={formData.ticket_price}
            onChange={(e) => setFormData({ ...formData, ticket_price: parseFloat(e.target.value) })}
            className="input"
            min={0}
            step={0.01}
            required
          />
        </div>
        <div>
          <label className="label">Total Seats</label>
          <input
            type="number"
            value={formData.total_available_seats}
            onChange={(e) => setFormData({ ...formData, total_available_seats: parseInt(e.target.value) })}
            className="input"
            min={0}
            required
          />
        </div>
      </div>

      <div className="flex space-x-4 pt-4">
        <button type="button" onClick={onCancel} className="btn-secondary flex-1">
          Cancel
        </button>
        <button type="submit" className="btn-primary flex-1" disabled={isLoading}>
          {isLoading ? 'Saving...' : initialData ? 'Update Flight' : 'Create Flight'}
        </button>
      </div>
    </form>
  );
};

// Hotel Form Component
const HotelForm: React.FC<{
  initialData?: any;
  onSubmit: (data: HotelFormData) => void;
  onCancel: () => void;
  isLoading: boolean;
}> = ({ initialData, onSubmit, onCancel, isLoading }) => {
  const [formData, setFormData] = useState<HotelFormData>({
    hotel_name: initialData?.hotel_name || '',
    address: initialData?.address || '',
    city: initialData?.city || '',
    state: initialData?.state || '',
    zip_code: initialData?.zip_code || '',
    star_rating: initialData?.star_rating || 3,
    number_of_rooms: initialData?.number_of_rooms || 0,
    room_type: initialData?.room_type || 'Standard',
    price_per_night: initialData?.price_per_night || 0,
    amenities: initialData?.amenities || '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="label">Hotel Name</label>
        <input
          type="text"
          value={formData.hotel_name}
          onChange={(e) => setFormData({ ...formData, hotel_name: e.target.value })}
          className="input"
          placeholder="Grand Hotel"
          required
        />
      </div>

      <div>
        <label className="label">Address</label>
        <input
          type="text"
          value={formData.address}
          onChange={(e) => setFormData({ ...formData, address: e.target.value })}
          className="input"
          placeholder="123 Main Street"
          required
        />
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="label">City</label>
          <input
            type="text"
            value={formData.city}
            onChange={(e) => setFormData({ ...formData, city: e.target.value })}
            className="input"
            placeholder="New York"
            required
          />
        </div>
        <div>
          <label className="label">State</label>
          <input
            type="text"
            value={formData.state}
            onChange={(e) => setFormData({ ...formData, state: e.target.value.toUpperCase() })}
            className="input"
            placeholder="NY"
            maxLength={2}
            required
          />
        </div>
        <div>
          <label className="label">ZIP Code</label>
          <input
            type="text"
            value={formData.zip_code}
            onChange={(e) => setFormData({ ...formData, zip_code: e.target.value })}
            className="input"
            placeholder="10001"
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="label">Star Rating</label>
          <div className="flex space-x-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onClick={() => setFormData({ ...formData, star_rating: star })}
                className={`p-2 rounded transition-all ${
                  formData.star_rating >= star ? 'text-yellow-400' : 'text-gray-600'
                }`}
              >
                <FaStar className="w-5 h-5" />
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="label">Number of Rooms</label>
          <input
            type="number"
            value={formData.number_of_rooms}
            onChange={(e) => setFormData({ ...formData, number_of_rooms: parseInt(e.target.value) })}
            className="input"
            min={0}
            required
          />
        </div>
        <div>
          <label className="label">Room Type</label>
          <select
            value={formData.room_type}
            onChange={(e) => setFormData({ ...formData, room_type: e.target.value })}
            className="input"
          >
            <option value="Standard">Standard</option>
            <option value="Deluxe">Deluxe</option>
            <option value="Suite">Suite</option>
            <option value="Presidential">Presidential</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">Price per Night ($)</label>
          <input
            type="number"
            value={formData.price_per_night}
            onChange={(e) => setFormData({ ...formData, price_per_night: parseFloat(e.target.value) })}
            className="input"
            min={0}
            step={0.01}
            required
          />
        </div>
        <div>
          <label className="label">Amenities (comma-separated)</label>
          <input
            type="text"
            value={formData.amenities}
            onChange={(e) => setFormData({ ...formData, amenities: e.target.value })}
            className="input"
            placeholder="Wi-Fi, Parking, Pool, Breakfast"
          />
        </div>
      </div>

      <div className="flex space-x-4 pt-4">
        <button type="button" onClick={onCancel} className="btn-secondary flex-1">
          Cancel
        </button>
        <button type="submit" className="btn-primary flex-1" disabled={isLoading}>
          {isLoading ? 'Saving...' : initialData ? 'Update Hotel' : 'Create Hotel'}
        </button>
      </div>
    </form>
  );
};

// Car Form Component
const CarForm: React.FC<{
  initialData?: any;
  onSubmit: (data: CarFormData) => void;
  onCancel: () => void;
  isLoading: boolean;
}> = ({ initialData, onSubmit, onCancel, isLoading }) => {
  const [formData, setFormData] = useState<CarFormData>({
    car_type: initialData?.car_type || 'Sedan',
    company_provider_name: initialData?.company_provider_name || '',
    model_and_year: initialData?.model_and_year || '',
    transmission_type: initialData?.transmission_type || 'Automatic',
    number_of_seats: initialData?.number_of_seats || 5,
    daily_rental_price: initialData?.daily_rental_price || 0,
    location_city: initialData?.location_city || '',
    location_state: initialData?.location_state || '',
    location_address: initialData?.location_address || '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">Car Type</label>
          <select
            value={formData.car_type}
            onChange={(e) => setFormData({ ...formData, car_type: e.target.value })}
            className="input"
          >
            <option value="Compact">Compact</option>
            <option value="Sedan">Sedan</option>
            <option value="SUV">SUV</option>
            <option value="Luxury">Luxury</option>
            <option value="Van">Van</option>
          </select>
        </div>
        <div>
          <label className="label">Provider/Company</label>
          <input
            type="text"
            value={formData.company_provider_name}
            onChange={(e) => setFormData({ ...formData, company_provider_name: e.target.value })}
            className="input"
            placeholder="Hertz"
            required
          />
        </div>
      </div>

      <div>
        <label className="label">Model and Year</label>
        <input
          type="text"
          value={formData.model_and_year}
          onChange={(e) => setFormData({ ...formData, model_and_year: e.target.value })}
          className="input"
          placeholder="Toyota RAV4 2023"
          required
        />
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="label">Transmission</label>
          <select
            value={formData.transmission_type}
            onChange={(e) => setFormData({ ...formData, transmission_type: e.target.value as any })}
            className="input"
          >
            <option value="Automatic">Automatic</option>
            <option value="Manual">Manual</option>
          </select>
        </div>
        <div>
          <label className="label">Number of Seats</label>
          <input
            type="number"
            value={formData.number_of_seats}
            onChange={(e) => setFormData({ ...formData, number_of_seats: parseInt(e.target.value) })}
            className="input"
            min={2}
            max={8}
            required
          />
        </div>
        <div>
          <label className="label">Daily Price ($)</label>
          <input
            type="number"
            value={formData.daily_rental_price}
            onChange={(e) => setFormData({ ...formData, daily_rental_price: parseFloat(e.target.value) })}
            className="input"
            min={0}
            step={0.01}
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="label">City</label>
          <input
            type="text"
            value={formData.location_city}
            onChange={(e) => setFormData({ ...formData, location_city: e.target.value })}
            className="input"
            placeholder="Los Angeles"
          />
        </div>
        <div>
          <label className="label">State</label>
          <input
            type="text"
            value={formData.location_state}
            onChange={(e) => setFormData({ ...formData, location_state: e.target.value.toUpperCase() })}
            className="input"
            placeholder="CA"
            maxLength={2}
          />
        </div>
        <div>
          <label className="label">Address</label>
          <input
            type="text"
            value={formData.location_address}
            onChange={(e) => setFormData({ ...formData, location_address: e.target.value })}
            className="input"
            placeholder="123 Rental St"
          />
        </div>
      </div>

      <div className="flex space-x-4 pt-4">
        <button type="button" onClick={onCancel} className="btn-secondary flex-1">
          Cancel
        </button>
        <button type="submit" className="btn-primary flex-1" disabled={isLoading}>
          {isLoading ? 'Saving...' : initialData ? 'Update Car' : 'Create Car'}
        </button>
      </div>
    </form>
  );
};

// Listing Card Component
const ListingCard: React.FC<{
  listing: any;
  type: ListingType;
  onEdit: () => void;
  onDelete: () => void;
}> = ({ listing, type, onEdit, onDelete }) => {
  const getTypeIcon = () => {
    switch (type) {
      case 'flight': return FaPlane;
      case 'hotel': return FaHotel;
      case 'car': return FaCar;
    }
  };

  const TypeIcon = getTypeIcon();

  const getTitle = () => {
    switch (type) {
      case 'flight': return `${listing.departure_airport} → ${listing.arrival_airport}`;
      case 'hotel': return listing.hotel_name;
      case 'car': return listing.model_and_year;
    }
  };

  const getSubtitle = () => {
    switch (type) {
      case 'flight': return listing.airline;
      case 'hotel': return `${listing.city}, ${listing.state}`;
      case 'car': return listing.company_provider_name;
    }
  };

  const getPrice = () => {
    switch (type) {
      case 'flight': return `$${listing.ticket_price}`;
      case 'hotel': return `$${listing.price_per_night}/night`;
      case 'car': return `$${listing.daily_rental_price}/day`;
    }
  };

  const getRating = () => {
    switch (type) {
      case 'flight': return listing.flight_rating;
      case 'hotel': return listing.hotel_rating;
      case 'car': return listing.car_rating;
    }
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="card-hover p-6"
    >
      <div className="flex items-start justify-between mb-4">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
          type === 'flight' ? 'bg-primary-500/20 text-primary-400' :
          type === 'hotel' ? 'bg-secondary-500/20 text-secondary-400' :
          'bg-accent-emerald/20 text-accent-emerald'
        }`}>
          <TypeIcon className="w-6 h-6" />
        </div>
        <div className="flex items-center space-x-1">
          <FaStar className="w-4 h-4 text-yellow-400" />
          <span className="text-white font-medium">{getRating()?.toFixed(1) || '0.0'}</span>
        </div>
      </div>

      <h3 className="text-lg font-semibold text-white mb-1">{getTitle()}</h3>
      <p className="text-gray-400 text-sm mb-2">{getSubtitle()}</p>

      {type === 'flight' && (
        <p className="text-gray-500 text-sm mb-4">
          {listing.flight_class} • {listing.current_available_seats || listing.total_available_seats} seats
        </p>
      )}
      {type === 'hotel' && (
        <div className="flex items-center space-x-1 mb-4">
          {Array.from({ length: listing.star_rating || 0 }).map((_, i) => (
            <FaStar key={i} className="w-3 h-3 text-yellow-400" />
          ))}
        </div>
      )}
      {type === 'car' && (
        <p className="text-gray-500 text-sm mb-4">
          {listing.car_type} • {listing.transmission_type} • {listing.number_of_seats} seats
        </p>
      )}

      <div className="flex items-center justify-between pt-4 border-t border-dark-700">
        <span className="text-xl font-bold text-primary-400">{getPrice()}</span>
        <div className="flex space-x-2">
          <button
            onClick={onEdit}
            className="p-2 text-gray-400 hover:text-white hover:bg-dark-700 rounded-lg transition-colors"
          >
            <HiPencil className="w-4 h-4" />
          </button>
          <button
            onClick={onDelete}
            className="p-2 text-gray-400 hover:text-red-400 hover:bg-dark-700 rounded-lg transition-colors"
          >
            <HiTrash className="w-4 h-4" />
          </button>
        </div>
      </div>
    </motion.div>
  );
};

// Main Admin Listings Component
const AdminListings: React.FC = () => {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState<ListingType | 'all'>('all');
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState<ListingType>('flight');
  const [editingListing, setEditingListing] = useState<any>(null);

  // Queries
  const flightsQuery = useQuery({
    queryKey: ['admin-flights'],
    queryFn: () => flightService.search({ page_size: 100 }),
  });

  const hotelsQuery = useQuery({
    queryKey: ['admin-hotels'],
    queryFn: () => hotelService.search({ page_size: 100 }),
  });

  const carsQuery = useQuery({
    queryKey: ['admin-cars'],
    queryFn: () => carService.search({ page_size: 100 }),
  });

  // Mutations
  const createFlightMutation = useMutation({
    mutationFn: (data: FlightFormData) => flightService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-flights'] });
      toast.success('Flight created successfully');
      closeModal();
    },
    onError: () => toast.error('Failed to create flight'),
  });

  const updateFlightMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => flightService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-flights'] });
      toast.success('Flight updated successfully');
      closeModal();
    },
    onError: () => toast.error('Failed to update flight'),
  });

  const deleteFlightMutation = useMutation({
    mutationFn: (id: string) => flightService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-flights'] });
      toast.success('Flight deleted successfully');
    },
    onError: () => toast.error('Failed to delete flight'),
  });

  const createHotelMutation = useMutation({
    mutationFn: (data: HotelFormData) => hotelService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-hotels'] });
      toast.success('Hotel created successfully');
      closeModal();
    },
    onError: () => toast.error('Failed to create hotel'),
  });

  const updateHotelMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => hotelService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-hotels'] });
      toast.success('Hotel updated successfully');
      closeModal();
    },
    onError: () => toast.error('Failed to update hotel'),
  });

  const deleteHotelMutation = useMutation({
    mutationFn: (id: string) => hotelService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-hotels'] });
      toast.success('Hotel deleted successfully');
    },
    onError: () => toast.error('Failed to delete hotel'),
  });

  const createCarMutation = useMutation({
    mutationFn: (data: CarFormData) => carService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-cars'] });
      toast.success('Car created successfully');
      closeModal();
    },
    onError: () => toast.error('Failed to create car'),
  });

  const updateCarMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => carService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-cars'] });
      toast.success('Car updated successfully');
      closeModal();
    },
    onError: () => toast.error('Failed to update car'),
  });

  const deleteCarMutation = useMutation({
    mutationFn: (id: string) => carService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-cars'] });
      toast.success('Car deleted successfully');
    },
    onError: () => toast.error('Failed to delete car'),
  });

  // Helpers
  const closeModal = () => {
    setShowModal(false);
    setEditingListing(null);
  };

  const openCreateModal = (type: ListingType) => {
    setModalType(type);
    setEditingListing(null);
    setShowModal(true);
  };

  const openEditModal = (listing: any, type: ListingType) => {
    setModalType(type);
    setEditingListing(listing);
    setShowModal(true);
  };

  const handleDelete = async (id: string, type: ListingType) => {
    if (!window.confirm(`Are you sure you want to delete this ${type}?`)) return;
    
    switch (type) {
      case 'flight': deleteFlightMutation.mutate(id); break;
      case 'hotel': deleteHotelMutation.mutate(id); break;
      case 'car': deleteCarMutation.mutate(id); break;
    }
  };

  const handleSubmit = (data: any) => {
    if (editingListing) {
      switch (modalType) {
        case 'flight': updateFlightMutation.mutate({ id: editingListing.flight_id, data }); break;
        case 'hotel': updateHotelMutation.mutate({ id: editingListing.hotel_id, data }); break;
        case 'car': updateCarMutation.mutate({ id: editingListing.car_id, data }); break;
      }
    } else {
      switch (modalType) {
        case 'flight': createFlightMutation.mutate(data); break;
        case 'hotel': createHotelMutation.mutate(data); break;
        case 'car': createCarMutation.mutate(data); break;
      }
    }
  };

  const isLoading = 
    createFlightMutation.isPending || updateFlightMutation.isPending ||
    createHotelMutation.isPending || updateHotelMutation.isPending ||
    createCarMutation.isPending || updateCarMutation.isPending;

  // Get all listings
  const flights = flightsQuery.data?.flights || [];
  const hotels = hotelsQuery.data?.hotels || [];
  const cars = carsQuery.data?.cars || [];

  // Filter listings
  const filterListings = (items: any[], type: ListingType) => {
    return items.filter(item => {
      const searchLower = search.toLowerCase();
      switch (type) {
        case 'flight':
          return item.airline?.toLowerCase().includes(searchLower) ||
                 item.departure_airport?.toLowerCase().includes(searchLower) ||
                 item.arrival_airport?.toLowerCase().includes(searchLower);
        case 'hotel':
          return item.hotel_name?.toLowerCase().includes(searchLower) ||
                 item.city?.toLowerCase().includes(searchLower);
        case 'car':
          return item.model_and_year?.toLowerCase().includes(searchLower) ||
                 item.company_provider_name?.toLowerCase().includes(searchLower);
        default:
          return true;
      }
    });
  };

  const filteredFlights = filterListings(flights, 'flight');
  const filteredHotels = filterListings(hotels, 'hotel');
  const filteredCars = filterListings(cars, 'car');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">Listings Management</h2>
          <p className="text-gray-400 text-sm">Manage flights, hotels, and car rentals</p>
        </div>
        <div className="flex space-x-2">
          <button onClick={() => openCreateModal('flight')} className="btn-primary">
            <FaPlane className="w-4 h-4 mr-2" />
            Add Flight
          </button>
          <button onClick={() => openCreateModal('hotel')} className="btn-secondary">
            <FaHotel className="w-4 h-4 mr-2" />
            Add Hotel
          </button>
          <button onClick={() => openCreateModal('car')} className="btn-ghost">
            <FaCar className="w-4 h-4 mr-2" />
            Add Car
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-md">
          <HiSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input
            type="text"
            placeholder="Search listings..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input pl-10"
          />
        </div>
        <div className="flex space-x-2">
          {(['all', 'flight', 'hotel', 'car'] as const).map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filterType === type
                  ? 'bg-primary-500 text-dark-950'
                  : 'bg-dark-800 text-gray-300 hover:bg-dark-700'
              }`}
            >
              {type === 'all' ? 'All' : type.charAt(0).toUpperCase() + type.slice(1) + 's'}
            </button>
          ))}
        </div>
        <button
          onClick={() => {
            flightsQuery.refetch();
            hotelsQuery.refetch();
            carsQuery.refetch();
          }}
          className="p-2 text-gray-400 hover:text-white transition-colors"
        >
          <HiRefresh className="w-5 h-5" />
        </button>
      </div>

      {/* Listings Grid */}
      <AnimatePresence mode="popLayout">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Flights */}
          {(filterType === 'all' || filterType === 'flight') && 
            filteredFlights.map((flight) => (
              <ListingCard
                key={flight.flight_id}
                listing={flight}
                type="flight"
                onEdit={() => openEditModal(flight, 'flight')}
                onDelete={() => handleDelete(flight.flight_id, 'flight')}
              />
            ))
          }
          
          {/* Hotels */}
          {(filterType === 'all' || filterType === 'hotel') && 
            filteredHotels.map((hotel) => (
              <ListingCard
                key={hotel.hotel_id}
                listing={hotel}
                type="hotel"
                onEdit={() => openEditModal(hotel, 'hotel')}
                onDelete={() => handleDelete(hotel.hotel_id, 'hotel')}
              />
            ))
          }
          
          {/* Cars */}
          {(filterType === 'all' || filterType === 'car') && 
            filteredCars.map((car) => (
              <ListingCard
                key={car.car_id}
                listing={car}
                type="car"
                onEdit={() => openEditModal(car, 'car')}
                onDelete={() => handleDelete(car.car_id, 'car')}
              />
            ))
          }
        </div>
      </AnimatePresence>

      {/* Empty State */}
      {filteredFlights.length === 0 && filteredHotels.length === 0 && filteredCars.length === 0 && (
        <div className="card p-12 text-center">
          <div className="text-6xl mb-4">📋</div>
          <h3 className="text-xl font-semibold text-white mb-2">No listings found</h3>
          <p className="text-gray-400 mb-6">
            {search ? 'Try adjusting your search.' : 'Start by adding some listings.'}
          </p>
          <button onClick={() => openCreateModal('flight')} className="btn-primary">
            <HiPlus className="w-5 h-5 mr-2" />
            Add Your First Listing
          </button>
        </div>
      )}

      {/* Modal */}
      <AnimatePresence>
        {showModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-dark-950/80 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="card w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6 m-4"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                    modalType === 'flight' ? 'bg-primary-500/20 text-primary-400' :
                    modalType === 'hotel' ? 'bg-secondary-500/20 text-secondary-400' :
                    'bg-accent-emerald/20 text-accent-emerald'
                  }`}>
                    {modalType === 'flight' && <FaPlane className="w-5 h-5" />}
                    {modalType === 'hotel' && <FaHotel className="w-5 h-5" />}
                    {modalType === 'car' && <FaCar className="w-5 h-5" />}
                  </div>
                  <h3 className="text-xl font-semibold text-white">
                    {editingListing ? `Edit ${modalType}` : `Add New ${modalType}`}
                  </h3>
                </div>
                <button onClick={closeModal} className="p-2 text-gray-400 hover:text-white rounded-lg">
                  <HiX className="w-5 h-5" />
                </button>
              </div>

              {modalType === 'flight' && (
                <FlightForm
                  initialData={editingListing}
                  onSubmit={handleSubmit}
                  onCancel={closeModal}
                  isLoading={isLoading}
                />
              )}
              {modalType === 'hotel' && (
                <HotelForm
                  initialData={editingListing}
                  onSubmit={handleSubmit}
                  onCancel={closeModal}
                  isLoading={isLoading}
                />
              )}
              {modalType === 'car' && (
                <CarForm
                  initialData={editingListing}
                  onSubmit={handleSubmit}
                  onCancel={closeModal}
                  isLoading={isLoading}
                />
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AdminListings;
