import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Hotel, Plus, Edit, Trash2, X, Save, ArrowLeft, Building2, DoorOpen } from 'lucide-react';
import {
  createHotel,
  updateHotel,
  deleteHotel,
  getAllHotels,
  getHotelRooms,
  createHotelRoom,
  updateHotelRoom,
  deleteHotelRoom,
  HotelResponse,
  HotelCreateData,
  HotelUpdateData,
  HotelRoomResponse,
  HotelRoomCreateData,
  HotelRoomUpdateData
} from '../api/adminHotels';

const AdminHotelManagement: React.FC = () => {
  const navigate = useNavigate();
  const [hotels, setHotels] = useState<HotelResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [authLoading, setAuthLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showRoomModal, setShowRoomModal] = useState(false);
  const [showCreateRoomModal, setShowCreateRoomModal] = useState(false);
  const [showEditRoomModal, setShowEditRoomModal] = useState(false);
  const [selectedHotel, setSelectedHotel] = useState<HotelResponse | null>(null);
  const [selectedHotelForRooms, setSelectedHotelForRooms] = useState<HotelResponse | null>(null);
  const [hotelRooms, setHotelRooms] = useState<HotelRoomResponse[]>([]);
  const [selectedRoom, setSelectedRoom] = useState<HotelRoomResponse | null>(null);
  const [roomFormData, setRoomFormData] = useState<HotelRoomCreateData>({
    room_id: '',
    room_type: 'single',
    room_number: '',
    price_per_night: 0,
    max_occupancy: 2,
    total_rooms: 1
  });
  const [roomEditData, setRoomEditData] = useState<HotelRoomUpdateData>({});
  const [formData, setFormData] = useState<HotelCreateData>({
    hotel_id: '',
    hotel_name: '',
    description: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
    star_rating: 3,
    amenities: '',
    phone_number: '',
    email: '',
    website: ''
  });
  const [editData, setEditData] = useState<HotelUpdateData>({});
  const [submitting, setSubmitting] = useState(false);
  const [createImageFile, setCreateImageFile] = useState<File | null>(null);
  const [editImageFile, setEditImageFile] = useState<File | null>(null);
  const [createImagePreview, setCreateImagePreview] = useState<string | null>(null);
  const [editImagePreview, setEditImagePreview] = useState<string | null>(null);

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
  }, [navigate]);

  useEffect(() => {
    if (!authLoading) {
    loadHotels();
    }
  }, [authLoading]);

  const loadHotels = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getAllHotels();
      setHotels(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load hotels');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      await createHotel(formData, createImageFile || undefined);
      setShowCreateModal(false);
      resetForm();
      setCreateImageFile(null);
      setCreateImagePreview(null);
      await loadHotels();
    } catch (err: any) {
      setError(err.message || 'Failed to create hotel');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (hotel: HotelResponse) => {
    setSelectedHotel(hotel);
    setEditData({
      hotel_name: hotel.hotel_name,
      description: hotel.description,
      address: hotel.address,
      city: hotel.city,
      state: hotel.state,
      zip_code: hotel.zip_code,
      star_rating: hotel.star_rating,
      amenities: hotel.amenities,
      phone_number: hotel.phone_number,
      email: hotel.email,
      website: hotel.website,
      is_active: hotel.is_active
    });
    setEditImagePreview(hotel.image_url || null);
    setEditImageFile(null);
    setShowEditModal(true);
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHotel) return;

    setSubmitting(true);
    setError('');

    try {
      await updateHotel(selectedHotel.hotel_id, editData, editImageFile || undefined);
      setShowEditModal(false);
      setSelectedHotel(null);
      setEditImageFile(null);
      setEditImagePreview(null);
      await loadHotels();
    } catch (err: any) {
      setError(err.message || 'Failed to update hotel');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (hotelId: string) => {
    if (!confirm(`Are you sure you want to delete hotel ${hotelId}?`)) {
      return;
    }

    try {
      await deleteHotel(hotelId);
      await loadHotels();
    } catch (err: any) {
      setError(err.message || 'Failed to delete hotel');
    }
  };

  const handleManageRooms = async (hotel: HotelResponse) => {
    setSelectedHotelForRooms(hotel);
    try {
      const rooms = await getHotelRooms(hotel.hotel_id);
      setHotelRooms(rooms);
      setShowRoomModal(true);
    } catch (err: any) {
      setError(err.message || 'Failed to load rooms');
    }
  };

  const handleCreateRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHotelForRooms) return;

    setSubmitting(true);
    setError('');

    try {
      await createHotelRoom(selectedHotelForRooms.hotel_id, roomFormData);
      setShowCreateRoomModal(false);
      resetRoomForm();
      // Reload rooms
      const rooms = await getHotelRooms(selectedHotelForRooms.hotel_id);
      setHotelRooms(rooms);
    } catch (err: any) {
      setError(err.message || 'Failed to create room');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEditRoom = (room: HotelRoomResponse) => {
    setSelectedRoom(room);
    setRoomEditData({
      price_per_night: parseFloat(room.price_per_night),
      max_occupancy: room.max_occupancy,
      total_rooms: room.total_rooms,
      available_rooms: room.available_rooms,
      is_active: room.is_active
    });
    setShowEditRoomModal(true);
  };

  const handleUpdateRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHotelForRooms || !selectedRoom) return;

    setSubmitting(true);
    setError('');

    try {
      await updateHotelRoom(selectedHotelForRooms.hotel_id, selectedRoom.room_id, roomEditData);
      setShowEditRoomModal(false);
      setSelectedRoom(null);
      // Reload rooms
      const rooms = await getHotelRooms(selectedHotelForRooms.hotel_id);
      setHotelRooms(rooms);
    } catch (err: any) {
      setError(err.message || 'Failed to update room');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteRoom = async (roomId: string) => {
    if (!selectedHotelForRooms) return;
    if (!confirm(`Are you sure you want to delete room ${roomId}?`)) {
      return;
    }

    try {
      await deleteHotelRoom(selectedHotelForRooms.hotel_id, roomId);
      // Reload rooms
      const rooms = await getHotelRooms(selectedHotelForRooms.hotel_id);
      setHotelRooms(rooms);
    } catch (err: any) {
      setError(err.message || 'Failed to delete room');
    }
  };

  const resetRoomForm = () => {
    setRoomFormData({
      room_id: '',
      room_type: 'single',
      room_number: '',
      price_per_night: 0,
      max_occupancy: 2,
      total_rooms: 1
    });
  };

  const resetForm = () => {
    setFormData({
      hotel_id: '',
      hotel_name: '',
      description: '',
      address: '',
      city: '',
      state: '',
      zip_code: '',
      star_rating: 3,
      amenities: '',
      phone_number: '',
      email: '',
      website: ''
    });
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-600 mx-auto"></div>
          <p className="mt-4 text-slate-600">{authLoading ? 'Checking authentication...' : 'Loading hotels...'}</p>
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
                <Hotel className="mr-3 text-slate-600" size={36} />
                Hotel Management
              </h1>
              <p className="mt-2 text-slate-600">
                Create, update, and delete hotels
              </p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-md flex items-center"
            >
              <Plus className="mr-2" size={20} />
              Create Hotel
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Hotels Table */}
        <div className="bg-white rounded-xl shadow-lg border-2 border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Hotel ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Location</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Stars</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {hotels.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-8 text-center text-slate-600">
                      No hotels found
                    </td>
                  </tr>
                ) : (
                  hotels.map((hotel) => (
                    <tr key={hotel.hotel_id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                        {hotel.hotel_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        {hotel.hotel_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        {hotel.city}, {hotel.state}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        {'⭐'.repeat(hotel.star_rating || 0)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          hotel.is_active
                            ? 'bg-green-100 text-green-700'
                            : 'bg-red-100 text-red-700'
                        }`}>
                          {hotel.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleManageRooms(hotel)}
                            className="text-green-500 hover:text-green-700 transition-colors"
                            title="Manage Rooms"
                          >
                            <DoorOpen size={18} />
                          </button>
                          <button
                            onClick={() => handleEdit(hotel)}
                            className="text-blue-500 hover:text-blue-700 transition-colors"
                            title="Edit"
                          >
                            <Edit size={18} />
                          </button>
                          <button
                            onClick={() => handleDelete(hotel.hotel_id)}
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
              <div className="sticky top-0 bg-white border-b border-slate-100 px-6 py-4 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-slate-700">Create New Hotel</h2>
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
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Hotel ID *</label>
                    <input
                      type="text"
                      required
                      value={formData.hotel_id}
                      onChange={(e) => setFormData({ ...formData, hotel_id: e.target.value.toUpperCase() })}
                      placeholder="HOTEL-001"
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Hotel Name *</label>
                    <input
                      type="text"
                      required
                      value={formData.hotel_name}
                      onChange={(e) => setFormData({ ...formData, hotel_name: e.target.value })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Description</label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      rows={2}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Address *</label>
                    <input
                      type="text"
                      required
                      value={formData.address}
                      onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">City *</label>
                    <input
                      type="text"
                      required
                      value={formData.city}
                      onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">State</label>
                    <input
                      type="text"
                      maxLength={2}
                      value={formData.state}
                      onChange={(e) => setFormData({ ...formData, state: e.target.value.toUpperCase() })}
                      placeholder="CA"
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 uppercase"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Zip Code</label>
                    <input
                      type="text"
                      value={formData.zip_code}
                      onChange={(e) => setFormData({ ...formData, zip_code: e.target.value })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Star Rating</label>
                    <select
                      value={formData.star_rating}
                      onChange={(e) => setFormData({ ...formData, star_rating: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value={1}>1 Star</option>
                      <option value={2}>2 Stars</option>
                      <option value={3}>3 Stars</option>
                      <option value={4}>4 Stars</option>
                      <option value={5}>5 Stars</option>
                    </select>
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Amenities (comma-separated)</label>
                    <input
                      type="text"
                      value={formData.amenities}
                      onChange={(e) => setFormData({ ...formData, amenities: e.target.value })}
                      placeholder="wifi,breakfast,parking,pool,gym"
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Phone</label>
                    <input
                      type="tel"
                      value={formData.phone_number}
                      onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Email</label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Website</label>
                    <input
                      type="url"
                      value={formData.website}
                      onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
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
                    {submitting ? 'Creating...' : 'Create Hotel'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Edit Modal - Similar to Create but with edit data */}
        {showEditModal && selectedHotel && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white border-b border-slate-100 px-6 py-4 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-slate-700">Edit Hotel {selectedHotel.hotel_id}</h2>
                <button
                  onClick={() => {
                    setShowEditModal(false);
                    setSelectedHotel(null);
                  }}
                  className="text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <X size={24} />
                </button>
              </div>
              <form onSubmit={handleUpdate} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Hotel Name</label>
                    <input
                      type="text"
                      value={editData.hotel_name || ''}
                      onChange={(e) => setEditData({ ...editData, hotel_name: e.target.value })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Description</label>
                    <textarea
                      value={editData.description || ''}
                      onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                      rows={2}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Star Rating</label>
                    <select
                      value={editData.star_rating || 3}
                      onChange={(e) => setEditData({ ...editData, star_rating: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value={1}>1 Star</option>
                      <option value={2}>2 Stars</option>
                      <option value={3}>3 Stars</option>
                      <option value={4}>4 Stars</option>
                      <option value={5}>5 Stars</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Status</label>
                    <select
                      value={editData.is_active !== undefined ? editData.is_active.toString() : selectedHotel.is_active.toString()}
                      onChange={(e) => setEditData({ ...editData, is_active: e.target.value === 'true' })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="true">Active</option>
                      <option value="false">Inactive</option>
                    </select>
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">Amenities</label>
                    <input
                      type="text"
                      value={editData.amenities || ''}
                      onChange={(e) => setEditData({ ...editData, amenities: e.target.value })}
                      placeholder="wifi,breakfast,parking,pool,gym"
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
                <div className="flex justify-end space-x-3 pt-4 border-t border-slate-100">
                  <button
                    type="button"
                    onClick={() => {
                      setShowEditModal(false);
                      setSelectedHotel(null);
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
                    {submitting ? 'Updating...' : 'Update Hotel'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Room Management Modal */}
        {showRoomModal && selectedHotelForRooms && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-slate-900">Manage Rooms - {selectedHotelForRooms.hotel_name}</h2>
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => setShowCreateRoomModal(true)}
                    className="px-3 py-1.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all text-sm flex items-center"
                  >
                    <Plus className="mr-1.5" size={16} />
                    Add Room
                  </button>
                <button
                  onClick={() => {
                    setShowRoomModal(false);
                    setSelectedHotelForRooms(null);
                      setHotelRooms([]);
                    }}
                    className="text-slate-400 hover:text-slate-600 transition-colors"
                  >
                    <X size={24} />
                  </button>
                </div>
              </div>
              <div className="p-6">
                {error && (
                  <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                    {error}
                  </div>
                )}

                {hotelRooms.length === 0 ? (
                  <div className="text-center py-12">
                    <Building2 className="mx-auto text-slate-400 mb-4" size={48} />
                    <p className="text-slate-600 mb-4">No rooms found for this hotel</p>
                    <button
                      onClick={() => setShowCreateRoomModal(true)}
                      className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all"
                    >
                      Create First Room
                    </button>
                  </div>
                ) : (
                  <div className="bg-white rounded-xl shadow-lg border-2 border-slate-200 overflow-hidden">
                    <table className="min-w-full divide-y divide-slate-200">
                      <thead className="bg-slate-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Room ID</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Type</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Room Number</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Price/Night</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Max Occupancy</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Total Rooms</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Available</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Status</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-slate-200">
                        {hotelRooms.map((room) => (
                          <tr key={room.room_id} className="hover:bg-slate-50">
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                              {room.room_id}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600 capitalize">
                              {room.room_type}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                              {room.room_number || '-'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                              ${parseFloat(room.price_per_night).toFixed(2)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                              {room.max_occupancy}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                              {room.total_rooms}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                              {room.available_rooms}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-2 py-1 text-xs rounded-full ${
                                room.is_active
                                  ? 'bg-green-100 text-green-700'
                                  : 'bg-red-100 text-red-700'
                              }`}>
                                {room.is_active ? 'Active' : 'Inactive'}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                              <div className="flex space-x-2">
                                <button
                                  onClick={() => handleEditRoom(room)}
                                  className="text-blue-600 hover:text-blue-700 transition-colors"
                                  title="Edit"
                                >
                                  <Edit size={18} />
                                </button>
                                <button
                                  onClick={() => handleDeleteRoom(room.room_id)}
                                  className="text-red-600 hover:text-red-700 transition-colors"
                                  title="Delete"
                                >
                                  <Trash2 size={18} />
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Create Room Modal */}
        {showCreateRoomModal && selectedHotelForRooms && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[60] p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-slate-900">Create New Room</h2>
                <button
                  onClick={() => {
                    setShowCreateRoomModal(false);
                    resetRoomForm();
                  }}
                  className="text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <X size={24} />
                </button>
              </div>
              <form onSubmit={handleCreateRoom} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Room ID *</label>
                    <input
                      type="text"
                      required
                      value={roomFormData.room_id}
                      onChange={(e) => setRoomFormData({ ...roomFormData, room_id: e.target.value.toUpperCase() })}
                      placeholder="ROOM-001"
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Room Type *</label>
                    <select
                      required
                      value={roomFormData.room_type}
                      onChange={(e) => setRoomFormData({ ...roomFormData, room_type: e.target.value as any })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="single">Single</option>
                      <option value="double">Double</option>
                      <option value="suite">Suite</option>
                      <option value="deluxe">Deluxe</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Room Number</label>
                    <input
                      type="text"
                      value={roomFormData.room_number}
                      onChange={(e) => setRoomFormData({ ...roomFormData, room_number: e.target.value })}
                      placeholder="101"
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Price Per Night *</label>
                    <input
                      type="number"
                      required
                      min="0"
                      step="0.01"
                      value={roomFormData.price_per_night}
                      onChange={(e) => setRoomFormData({ ...roomFormData, price_per_night: parseFloat(e.target.value) || 0 })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Max Occupancy *</label>
                    <input
                      type="number"
                      required
                      min="1"
                      max="10"
                      value={roomFormData.max_occupancy}
                      onChange={(e) => setRoomFormData({ ...roomFormData, max_occupancy: parseInt(e.target.value) || 2 })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Total Rooms *</label>
                    <input
                      type="number"
                      required
                      min="1"
                      value={roomFormData.total_rooms}
                      onChange={(e) => setRoomFormData({ ...roomFormData, total_rooms: parseInt(e.target.value) || 1 })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
                <div className="flex justify-end space-x-3 pt-4 border-t border-slate-200">
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateRoomModal(false);
                      resetRoomForm();
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
                    {submitting ? 'Creating...' : 'Create Room'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Edit Room Modal */}
        {showEditRoomModal && selectedRoom && selectedHotelForRooms && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[60] p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-slate-900">Edit Room {selectedRoom.room_id}</h2>
                <button
                  onClick={() => {
                    setShowEditRoomModal(false);
                    setSelectedRoom(null);
                  }}
                  className="text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <X size={24} />
                </button>
              </div>
              <form onSubmit={handleUpdateRoom} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Price Per Night</label>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={roomEditData.price_per_night || ''}
                      onChange={(e) => setRoomEditData({ ...roomEditData, price_per_night: parseFloat(e.target.value) || 0 })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Max Occupancy</label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={roomEditData.max_occupancy || ''}
                      onChange={(e) => setRoomEditData({ ...roomEditData, max_occupancy: parseInt(e.target.value) || 2 })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Total Rooms</label>
                    <input
                      type="number"
                      min="1"
                      value={roomEditData.total_rooms || ''}
                      onChange={(e) => setRoomEditData({ ...roomEditData, total_rooms: parseInt(e.target.value) || 1 })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Available Rooms</label>
                    <input
                      type="number"
                      min="0"
                      value={roomEditData.available_rooms || ''}
                      onChange={(e) => setRoomEditData({ ...roomEditData, available_rooms: parseInt(e.target.value) || 0 })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Status</label>
                    <select
                      value={roomEditData.is_active !== undefined ? roomEditData.is_active.toString() : selectedRoom.is_active.toString()}
                      onChange={(e) => setRoomEditData({ ...roomEditData, is_active: e.target.value === 'true' })}
                      className="w-full px-3 py-2 border-2 border-slate-300 rounded-xl text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="true">Active</option>
                      <option value="false">Inactive</option>
                    </select>
                  </div>
                </div>
                <div className="flex justify-end space-x-3 pt-4 border-t border-slate-200">
                  <button
                    type="button"
                    onClick={() => {
                      setShowEditRoomModal(false);
                      setSelectedRoom(null);
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
                    {submitting ? 'Updating...' : 'Update Room'}
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

export default AdminHotelManagement;
