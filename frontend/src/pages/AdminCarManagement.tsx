import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Car, Plus, Edit, Trash2, X, Save, ArrowLeft } from 'lucide-react';
import { createCar, updateCar, deleteCar, getAllCars, CarResponse, CarCreateData, CarUpdateData } from '../api/adminCars';

const AdminCarManagement: React.FC = () => {
  const navigate = useNavigate();
  const [cars, setCars] = useState<CarResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [authLoading, setAuthLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedCar, setSelectedCar] = useState<CarResponse | null>(null);
  const [formData, setFormData] = useState<CarCreateData>({
    car_id: '',
    car_type: 'sedan',
    make: '',
    model: '',
    year: new Date().getFullYear(),
    provider_name: '',
    transmission_type: 'automatic',
    seats: 5,
    doors: 4,
    daily_rental_price: 0,
    pickup_location: '',
    city: '',
    state: ''
  });
  const [editData, setEditData] = useState<CarUpdateData>({});
  const [submitting, setSubmitting] = useState(false);

  // Check admin authentication
  useEffect(() => {
    const adminToken = localStorage.getItem('admin_token');
    const adminData = localStorage.getItem('admin');
    const isAdmin = localStorage.getItem('is_admin');

    // Only allow access if user is authenticated as admin
    if (!adminToken || !adminData || isAdmin !== 'true') {
      // Clear any regular user session if present
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // Redirect to admin login if not authenticated as admin
      navigate('/admin/login');
      return;
    }

    setAuthLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // navigate is stable, don't include it

  useEffect(() => {
    if (!authLoading) {
      loadCars();

      // Set up auto-refresh every 10 seconds for real-time updates
      const refreshInterval = setInterval(() => {
        loadCars();
      }, 10000);

      // Cleanup interval on unmount
      return () => clearInterval(refreshInterval);
    }
  }, [authLoading]);

  const loadCars = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getAllCars();
      setCars(data);
    } catch (err: any) {
      const errorMessage = err?.message || err?.toString() || 'Failed to load cars';
      console.error('Load cars error:', err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      await createCar(formData);
      setShowCreateModal(false);
      resetForm();
      await loadCars();
    } catch (err: any) {
      setError(err.message || 'Failed to create car');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (car: CarResponse) => {
    setSelectedCar(car);
    setEditData({
      car_type: car.car_type as any,
      make: car.make,
      model: car.model,
      year: car.year,
      provider_name: car.provider_name,
      transmission_type: car.transmission_type as any,
      seats: car.seats,
      doors: car.doors,
      daily_rental_price: parseFloat(car.daily_rental_price),
      pickup_location: car.pickup_location,
      city: car.city,
      state: car.state,
      is_available: car.is_available,
      is_active: car.is_active
    });
    setShowEditModal(true);
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCar) return;

    setSubmitting(true);
    setError('');

    try {
      await updateCar(selectedCar.car_id, editData);
      setShowEditModal(false);
      setSelectedCar(null);
      await loadCars();
    } catch (err: any) {
      setError(err.message || 'Failed to update car');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (carId: string) => {
    if (!confirm(`Are you sure you want to delete car ${carId}?`)) {
      return;
    }

    try {
      await deleteCar(carId);
      await loadCars();
    } catch (err: any) {
      setError(err.message || 'Failed to delete car');
    }
  };

  const resetForm = () => {
    setFormData({
      car_id: '',
      car_type: 'sedan',
      make: '',
      model: '',
      year: new Date().getFullYear(),
      provider_name: '',
      transmission_type: 'automatic',
      seats: 5,
      doors: 4,
      daily_rental_price: 0,
      pickup_location: '',
      city: '',
      state: ''
    });
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-600 mx-auto"></div>
          <p className="mt-4 text-slate-600">{authLoading ? 'Checking authentication...' : 'Loading cars...'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/admin')}
            className="mb-4 flex items-center text-slate-600 hover:text-slate-700 transition-colors"
          >
            <ArrowLeft className="mr-2" size={20} />
            Back to Dashboard
          </button>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-slate-900 flex items-center">
                <Car className="mr-3 text-slate-600" size={36} />
                Car Management
              </h1>
              <p className="mt-2 text-slate-600">
                Create, update, and delete car listings
              </p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-md flex items-center"
            >
              <Plus className="mr-2" size={20} />
              Create Car
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Cars Table */}
        <div className="bg-white rounded-xl shadow-lg border-2 border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Car ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Vehicle</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Location</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Price/Day</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Specs</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {cars.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-6 py-8 text-center text-slate-600">
                      No cars found
                    </td>
                  </tr>
                ) : (
                  cars.map((car) => (
                    <tr key={car.car_id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                        {car.car_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        {car.make} {car.model} ({car.year})
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        <span className="capitalize">{car.car_type}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        {car.city ? `${car.city}, ${car.state}` : car.pickup_location}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        ${parseFloat(car.daily_rental_price).toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        {car.seats} seats, {car.doors} doors, {car.transmission_type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          car.is_active && car.is_available
                            ? 'bg-green-100 text-green-700'
                            : 'bg-red-100 text-red-700'
                        }`}>
                          {car.is_active && car.is_available ? 'Available' : 'Unavailable'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleEdit(car)}
                            className="text-blue-600 hover:text-blue-700 transition-colors"
                            title="Edit"
                          >
                            <Edit size={18} />
                          </button>
                          <button
                            onClick={() => handleDelete(car.car_id)}
                            className="text-red-500 hover:text-red-700 transition-colors"
                            title="Delete"
                          >
                            <Trash2 size={18} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Create Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white border-b border-slate-100 px-6 py-4 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-slate-700">Create New Car</h2>
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    resetForm();
                  }}
                  className="text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <X size={24} />
                </button>
              </div>
              <form onSubmit={handleCreate} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Car ID *</label>
                    <input
                      type="text"
                      required
                      value={formData.car_id}
                      onChange={(e) => setFormData({ ...formData, car_id: e.target.value.toUpperCase() })}
                      placeholder="CAR001"
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Car Type *</label>
                    <select
                      required
                      value={formData.car_type}
                      onChange={(e) => setFormData({ ...formData, car_type: e.target.value as any })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="sedan">Sedan</option>
                      <option value="suv">SUV</option>
                      <option value="compact">Compact</option>
                      <option value="luxury">Luxury</option>
                      <option value="van">Van</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Make *</label>
                    <input
                      type="text"
                      required
                      value={formData.make}
                      onChange={(e) => setFormData({ ...formData, make: e.target.value })}
                      placeholder="Toyota"
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Model *</label>
                    <input
                      type="text"
                      required
                      value={formData.model}
                      onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                      placeholder="Camry"
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Year *</label>
                    <input
                      type="number"
                      required
                      min="2000"
                      max="2030"
                      value={formData.year}
                      onChange={(e) => setFormData({ ...formData, year: parseInt(e.target.value) || 2024 })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Provider Name *</label>
                    <input
                      type="text"
                      required
                      value={formData.provider_name}
                      onChange={(e) => setFormData({ ...formData, provider_name: e.target.value })}
                      placeholder="Enterprise"
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Transmission *</label>
                    <select
                      required
                      value={formData.transmission_type}
                      onChange={(e) => setFormData({ ...formData, transmission_type: e.target.value as any })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="automatic">Automatic</option>
                      <option value="manual">Manual</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Seats *</label>
                    <input
                      type="number"
                      required
                      min="2"
                      max="12"
                      value={formData.seats}
                      onChange={(e) => setFormData({ ...formData, seats: parseInt(e.target.value) || 5 })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Doors *</label>
                    <input
                      type="number"
                      required
                      min="2"
                      max="5"
                      value={formData.doors}
                      onChange={(e) => setFormData({ ...formData, doors: parseInt(e.target.value) || 4 })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Daily Price *</label>
                    <input
                      type="number"
                      required
                      min="0"
                      step="0.01"
                      value={formData.daily_rental_price}
                      onChange={(e) => setFormData({ ...formData, daily_rental_price: parseFloat(e.target.value) || 0 })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Pickup Location *</label>
                    <input
                      type="text"
                      required
                      value={formData.pickup_location}
                      onChange={(e) => setFormData({ ...formData, pickup_location: e.target.value })}
                      placeholder="SFO Airport"
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">City</label>
                    <input
                      type="text"
                      value={formData.city}
                      onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                      placeholder="San Francisco"
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">State</label>
                    <input
                      type="text"
                      value={formData.state}
                      onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                      placeholder="CA"
                      maxLength={2}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 uppercase"
                    />
                  </div>
                </div>
                <div className="flex justify-end space-x-3 pt-4 border-t border-slate-100">
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateModal(false);
                      resetForm();
                    }}
                    className="px-4 py-2 border border-slate-300 text-slate-600 rounded-lg hover:bg-slate-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    <Save className="mr-2" size={18} />
                    {submitting ? 'Creating...' : 'Create Car'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Edit Modal */}
        {showEditModal && selectedCar && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white border-b border-slate-100 px-6 py-4 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-slate-700">Edit Car {selectedCar.car_id}</h2>
                <button
                  onClick={() => {
                    setShowEditModal(false);
                    setSelectedCar(null);
                  }}
                  className="text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <X size={24} />
                </button>
              </div>
              <form onSubmit={handleUpdate} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Daily Price</label>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={editData.daily_rental_price || ''}
                      onChange={(e) => setEditData({ ...editData, daily_rental_price: parseFloat(e.target.value) || 0 })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Status</label>
                    <select
                      value={editData.is_active !== undefined ? editData.is_active.toString() : selectedCar.is_active.toString()}
                      onChange={(e) => setEditData({ ...editData, is_active: e.target.value === 'true' })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="true">Active</option>
                      <option value="false">Inactive</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Availability</label>
                    <select
                      value={editData.is_available !== undefined ? editData.is_available.toString() : selectedCar.is_available.toString()}
                      onChange={(e) => setEditData({ ...editData, is_available: e.target.value === 'true' })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="true">Available</option>
                      <option value="false">Not Available</option>
                    </select>
                  </div>
                </div>
                <div className="flex justify-end space-x-3 pt-4 border-t border-slate-100">
                  <button
                    type="button"
                    onClick={() => {
                      setShowEditModal(false);
                      setSelectedCar(null);
                    }}
                    className="px-4 py-2 border border-slate-300 text-slate-600 rounded-lg hover:bg-slate-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    <Save className="mr-2" size={18} />
                    {submitting ? 'Updating...' : 'Update Car'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminCarManagement;
