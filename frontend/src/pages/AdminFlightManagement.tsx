import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plane, Plus, Edit, Trash2, X, Save, ArrowLeft } from 'lucide-react';
import { createFlight, updateFlight, deleteFlight, getAllFlights, FlightResponse, FlightCreateData, FlightUpdateData } from '../api/adminFlights';

const AdminFlightManagement: React.FC = () => {
  const navigate = useNavigate();
  const [flights, setFlights] = useState<FlightResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [authLoading, setAuthLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedFlight, setSelectedFlight] = useState<FlightResponse | null>(null);
  const [formData, setFormData] = useState<FlightCreateData>({
    flight_id: '',
    airline_name: '',
    operator_name: '',
    departure_airport: '',
    arrival_airport: '',
    departure_datetime: '',
    arrival_datetime: '',
    flight_class: 'economy',
    base_price: 0,
    total_seats: 0,
    available_seats: 0
  });
  const [editData, setEditData] = useState<FlightUpdateData>({});
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
      loadFlights();

      // Set up auto-refresh every 10 seconds for real-time updates
      const refreshInterval = setInterval(() => {
        loadFlights();
      }, 10000);

      // Cleanup interval on unmount
      return () => clearInterval(refreshInterval);
    }
  }, [authLoading]);

  const loadFlights = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getAllFlights();
      setFlights(data);
    } catch (err: any) {
      const errorMessage = err?.message || err?.toString() || 'Failed to load flights';
      console.error('Load flights error:', err);
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
      await createFlight(formData);
      setShowCreateModal(false);
      resetForm();
      await loadFlights();
    } catch (err: any) {
      setError(err.message || 'Failed to create flight');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (flight: FlightResponse) => {
    setSelectedFlight(flight);
    setEditData({
      airline_name: flight.airline_name,
      operator_name: flight.operator_name,
      departure_datetime: flight.departure_datetime.split('T')[0] + 'T' + flight.departure_datetime.split('T')[1].split('.')[0],
      arrival_datetime: flight.arrival_datetime.split('T')[0] + 'T' + flight.arrival_datetime.split('T')[1].split('.')[0],
      base_price: parseFloat(flight.base_price),
      available_seats: flight.available_seats,
      is_active: flight.is_active
    });
    setShowEditModal(true);
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFlight) return;

    setSubmitting(true);
    setError('');

    try {
      await updateFlight(selectedFlight.flight_id, editData);
      setShowEditModal(false);
      setSelectedFlight(null);
      await loadFlights();
    } catch (err: any) {
      setError(err.message || 'Failed to update flight');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (flightId: string) => {
    if (!confirm(`Are you sure you want to delete flight ${flightId}?`)) {
      return;
    }

    try {
      await deleteFlight(flightId);
      await loadFlights();
    } catch (err: any) {
      setError(err.message || 'Failed to delete flight');
    }
  };

  const resetForm = () => {
    setFormData({
      flight_id: '',
      airline_name: '',
      operator_name: '',
      departure_airport: '',
      arrival_airport: '',
      departure_datetime: '',
      arrival_datetime: '',
      flight_class: 'economy',
      base_price: 0,
      total_seats: 0,
      available_seats: 0
    });
  };

  const formatDateTime = (dateTime: string) => {
    const date = new Date(dateTime);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-600 mx-auto"></div>
          <p className="mt-4 text-slate-600">{authLoading ? 'Checking authentication...' : 'Loading flights...'}</p>
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
                <Plane className="mr-3 text-slate-600" size={36} />
                Flight Management
              </h1>
              <p className="mt-2 text-slate-600">
                Create, update, and delete flights
              </p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-md flex items-center"
            >
              <Plus className="mr-2" size={20} />
              Create Flight
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Flights Table */}
        <div className="bg-white rounded-xl shadow-lg border-2 border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Flight ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Airline</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Route</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Departure</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Price</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Seats</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {flights.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-6 py-8 text-center text-slate-600">
                      No flights found
                    </td>
                  </tr>
                ) : (
                  flights.map((flight) => (
                    <tr key={flight.flight_id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                        {flight.flight_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        {flight.airline_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        {flight.departure_airport} → {flight.arrival_airport}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        {formatDateTime(flight.departure_datetime)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        ${parseFloat(flight.base_price).toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        {flight.available_seats}/{flight.total_seats}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          flight.is_active 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-red-100 text-red-700'
                        }`}>
                          {flight.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleEdit(flight)}
                            className="text-blue-600 hover:text-blue-700 transition-colors"
                            title="Edit"
                          >
                            <Edit size={18} />
                          </button>
                          <button
                            onClick={() => handleDelete(flight.flight_id)}
                            className="text-red-600 hover:text-red-700 transition-colors"
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
              <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-slate-900">Create New Flight</h2>
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
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Flight ID *</label>
                    <input
                      type="text"
                      required
                      value={formData.flight_id}
                      onChange={(e) => setFormData({ ...formData, flight_id: e.target.value.toUpperCase() })}
                      placeholder="AA123"
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Airline Name *</label>
                    <input
                      type="text"
                      required
                      value={formData.airline_name}
                      onChange={(e) => setFormData({ ...formData, airline_name: e.target.value })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Operator Name</label>
                    <input
                      type="text"
                      value={formData.operator_name}
                      onChange={(e) => setFormData({ ...formData, operator_name: e.target.value })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Flight Class *</label>
                    <select
                      required
                      value={formData.flight_class}
                      onChange={(e) => setFormData({ ...formData, flight_class: e.target.value as 'economy' | 'business' | 'first' })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="economy">Economy</option>
                      <option value="business">Business</option>
                      <option value="first">First</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Departure Airport *</label>
                    <input
                      type="text"
                      required
                      maxLength={3}
                      value={formData.departure_airport}
                      onChange={(e) => setFormData({ ...formData, departure_airport: e.target.value.toUpperCase() })}
                      placeholder="SFO"
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 uppercase"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Arrival Airport *</label>
                    <input
                      type="text"
                      required
                      maxLength={3}
                      value={formData.arrival_airport}
                      onChange={(e) => setFormData({ ...formData, arrival_airport: e.target.value.toUpperCase() })}
                      placeholder="JFK"
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 uppercase"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Departure Date & Time *</label>
                    <input
                      type="datetime-local"
                      required
                      value={formData.departure_datetime}
                      onChange={(e) => setFormData({ ...formData, departure_datetime: e.target.value })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Arrival Date & Time *</label>
                    <input
                      type="datetime-local"
                      required
                      value={formData.arrival_datetime}
                      onChange={(e) => setFormData({ ...formData, arrival_datetime: e.target.value })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Base Price *</label>
                    <input
                      type="number"
                      required
                      min="0"
                      step="0.01"
                      value={formData.base_price}
                      onChange={(e) => setFormData({ ...formData, base_price: parseFloat(e.target.value) || 0 })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Total Seats *</label>
                    <input
                      type="number"
                      required
                      min="1"
                      value={formData.total_seats}
                      onChange={(e) => setFormData({ ...formData, total_seats: parseInt(e.target.value) || 0, available_seats: parseInt(e.target.value) || 0 })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
                <div className="flex justify-end space-x-3 pt-4 border-t border-slate-200">
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateModal(false);
                      resetForm();
                    }}
                    className="px-4 py-2 border-2 border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    <Save className="mr-2" size={18} />
                    {submitting ? 'Creating...' : 'Create Flight'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Edit Modal */}
        {showEditModal && selectedFlight && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white border-b border-purple-100 px-6 py-4 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-purple-700">Edit Flight {selectedFlight.flight_id}</h2>
                <button
                  onClick={() => {
                    setShowEditModal(false);
                    setSelectedFlight(null);
                  }}
                  className="text-purple-400 hover:text-purple-600 transition-colors"
                >
                  <X size={24} />
                </button>
              </div>
              <form onSubmit={handleUpdate} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-purple-600 mb-1.5">Airline Name</label>
                    <input
                      type="text"
                      value={editData.airline_name || ''}
                      onChange={(e) => setEditData({ ...editData, airline_name: e.target.value })}
                      className="w-full px-3 py-2 border border-purple-200 rounded-lg text-purple-800 bg-purple-50/50 focus:outline-none focus:ring-2 focus:ring-purple-300"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-purple-600 mb-1.5">Operator Name</label>
                    <input
                      type="text"
                      value={editData.operator_name || ''}
                      onChange={(e) => setEditData({ ...editData, operator_name: e.target.value })}
                      className="w-full px-3 py-2 border border-purple-200 rounded-lg text-purple-800 bg-purple-50/50 focus:outline-none focus:ring-2 focus:ring-purple-300"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-purple-600 mb-1.5">Departure Date & Time</label>
                    <input
                      type="datetime-local"
                      value={editData.departure_datetime || ''}
                      onChange={(e) => setEditData({ ...editData, departure_datetime: e.target.value })}
                      className="w-full px-3 py-2 border border-purple-200 rounded-lg text-purple-800 bg-purple-50/50 focus:outline-none focus:ring-2 focus:ring-purple-300"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-purple-600 mb-1.5">Arrival Date & Time</label>
                    <input
                      type="datetime-local"
                      value={editData.arrival_datetime || ''}
                      onChange={(e) => setEditData({ ...editData, arrival_datetime: e.target.value })}
                      className="w-full px-3 py-2 border border-purple-200 rounded-lg text-purple-800 bg-purple-50/50 focus:outline-none focus:ring-2 focus:ring-purple-300"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-purple-600 mb-1.5">Base Price</label>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={editData.base_price || ''}
                      onChange={(e) => setEditData({ ...editData, base_price: parseFloat(e.target.value) || 0 })}
                      className="w-full px-3 py-2 border border-purple-200 rounded-lg text-purple-800 bg-purple-50/50 focus:outline-none focus:ring-2 focus:ring-purple-300"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-purple-600 mb-1.5">Available Seats</label>
                    <input
                      type="number"
                      min="0"
                      value={editData.available_seats || ''}
                      onChange={(e) => setEditData({ ...editData, available_seats: parseInt(e.target.value) || 0 })}
                      className="w-full px-3 py-2 border border-purple-200 rounded-lg text-purple-800 bg-purple-50/50 focus:outline-none focus:ring-2 focus:ring-purple-300"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-purple-600 mb-1.5">Status</label>
                    <select
                      value={editData.is_active !== undefined ? editData.is_active.toString() : selectedFlight.is_active.toString()}
                      onChange={(e) => setEditData({ ...editData, is_active: e.target.value === 'true' })}
                      className="w-full px-3 py-2 border border-purple-200 rounded-lg text-purple-800 bg-purple-50/50 focus:outline-none focus:ring-2 focus:ring-purple-300"
                    >
                      <option value="true">Active</option>
                      <option value="false">Inactive</option>
                    </select>
                  </div>
                </div>
                <div className="flex justify-end space-x-3 pt-4 border-t border-purple-100">
                  <button
                    type="button"
                    onClick={() => {
                      setShowEditModal(false);
                      setSelectedFlight(null);
                    }}
                    className="px-4 py-2 border border-purple-300 text-purple-600 rounded-lg hover:bg-purple-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="px-4 py-2 bg-gradient-to-r from-purple-400 to-pink-400 text-white rounded-lg hover:from-purple-500 hover:to-pink-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    <Save className="mr-2" size={18} />
                    {submitting ? 'Updating...' : 'Update Flight'}
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

export default AdminFlightManagement;

