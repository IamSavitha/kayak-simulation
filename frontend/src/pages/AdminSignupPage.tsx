import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { User, Lock, Mail, Phone, MapPin, Upload, X } from 'lucide-react';
import { adminSignup } from '../api/admin';

const AdminSignupPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    adminId: '',
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
    role: 'admin' as 'admin' | 'super_admin' | 'moderator'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [profileImage, setProfileImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    // Validate admin ID format
    if (!formData.adminId.startsWith('ADMIN-')) {
      setError('Admin ID must start with "ADMIN-" (e.g., ADMIN-001)');
      return;
    }

    setLoading(true);

    try {
      await adminSignup({
        admin_id: formData.adminId.toUpperCase(),
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        phone_number: formData.phone || undefined,
        password: formData.password,
        address: formData.address || undefined,
        city: formData.city || undefined,
        state: formData.state || undefined,
        zip_code: formData.zipCode || undefined,
        role: formData.role // Already lowercase: 'admin', 'super_admin', 'moderator'
      }, profileImage || undefined);

      alert('Admin account created successfully! Please sign in.');
      navigate('/admin/login');
    } catch (err: any) {
      setError(err.message || 'Failed to create admin account');
    } finally {
      setLoading(false);
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        setError('Image file size must be less than 5MB');
        return;
      }
      if (!file.type.startsWith('image/')) {
        setError('Please select a valid image file');
        return;
      }
      setProfileImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
      setError('');
    }
  };

  const removeImage = () => {
    setProfileImage(null);
    setImagePreview(null);
  };

  return (
    <div className="min-h-[calc(100vh-16rem)] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-slate-50 via-white to-slate-100/30">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-semibold text-slate-700 tracking-tight">Create Admin Account</h1>
          <p className="mt-2 text-sm text-slate-500">
            Sign up to create a new admin account
          </p>
        </div>

        <form className="mt-8 space-y-6 bg-white/80 backdrop-blur-sm p-8 rounded-2xl shadow-lg border border-slate-100" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="adminId" className="block text-sm font-medium text-slate-600 mb-1.5">
                Admin ID <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-slate-300" />
                </div>
                <input
                  type="text"
                  name="adminId"
                  required
                  value={formData.adminId}
                  onChange={handleChange}
                  placeholder="ADMIN-001"
                  className="block w-full pl-10 pr-3 py-2.5 border-2 border-slate-300 rounded-xl text-slate-900 placeholder-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-400"
                />
              </div>
              <p className="mt-1 text-xs text-slate-400">Must start with "ADMIN-"</p>
            </div>

            <div>
              <label htmlFor="adminId" className="block text-sm font-medium text-slate-600 mb-1.5">
                Role <span className="text-red-500">*</span>
              </label>
              <select
                name="role"
                required
                value={formData.role}
                onChange={handleChange}
                className="block w-full px-3 py-2.5 border-2 border-slate-300 rounded-xl text-slate-900 placeholder-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-400"
              >
                <option value="admin">Admin</option>
                <option value="moderator">Moderator</option>
                <option value="super_admin">Super Admin</option>
              </select>
            </div>

            <div>
              <label htmlFor="adminId" className="block text-sm font-medium text-slate-600 mb-1.5">
                First Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="firstName"
                required
                value={formData.firstName}
                onChange={handleChange}
                  className="block w-full px-3 py-2.5 border-2 border-slate-300 rounded-xl text-slate-900 placeholder-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-400"
              />
            </div>

            <div>
              <label htmlFor="adminId" className="block text-sm font-medium text-slate-600 mb-1.5">
                Last Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="lastName"
                required
                value={formData.lastName}
                onChange={handleChange}
                  className="block w-full px-3 py-2.5 border-2 border-slate-300 rounded-xl text-slate-900 placeholder-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-400"
              />
            </div>

            <div>
              <label htmlFor="adminId" className="block text-sm font-medium text-slate-600 mb-1.5">
                Email <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-slate-300" />
                </div>
                <input
                  type="email"
                  name="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="block w-full pl-10 pr-3 py-2.5 border-2 border-slate-300 rounded-xl text-slate-900 placeholder-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-400"
                />
              </div>
            </div>

            <div>
              <label htmlFor="adminId" className="block text-sm font-medium text-slate-600 mb-1.5">
                Phone
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Phone className="h-5 w-5 text-slate-300" />
                </div>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  className="block w-full pl-10 pr-3 py-2.5 border-2 border-slate-300 rounded-xl text-slate-900 placeholder-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-400"
                />
              </div>
            </div>

            <div>
              <label htmlFor="adminId" className="block text-sm font-medium text-slate-600 mb-1.5">
                Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MapPin className="h-5 w-5 text-slate-300" />
                </div>
                <input
                  type="text"
                  name="address"
                  value={formData.address}
                  onChange={handleChange}
                  className="block w-full pl-10 pr-3 py-2.5 border-2 border-slate-300 rounded-xl text-slate-900 placeholder-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-400"
                />
              </div>
            </div>

            <div>
              <label htmlFor="adminId" className="block text-sm font-medium text-slate-600 mb-1.5">
                City
              </label>
              <input
                type="text"
                name="city"
                value={formData.city}
                onChange={handleChange}
                  className="block w-full px-3 py-2.5 border-2 border-slate-300 rounded-xl text-slate-900 placeholder-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-400"
              />
            </div>

            <div>
              <label htmlFor="adminId" className="block text-sm font-medium text-slate-600 mb-1.5">
                State
              </label>
              <input
                type="text"
                name="state"
                maxLength={2}
                value={formData.state}
                onChange={handleChange}
                placeholder="CA"
                className="block w-full px-3 py-2.5 border-2 border-slate-300 rounded-xl text-slate-900 placeholder-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-400 uppercase"
              />
            </div>

            <div>
              <label htmlFor="adminId" className="block text-sm font-medium text-slate-600 mb-1.5">
                ZIP Code
              </label>
              <input
                type="text"
                name="zipCode"
                value={formData.zipCode}
                onChange={handleChange}
                  className="block w-full px-3 py-2.5 border-2 border-slate-300 rounded-xl text-slate-900 placeholder-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-400"
              />
            </div>

            <div>
              <label htmlFor="adminId" className="block text-sm font-medium text-slate-600 mb-1.5">
                Password <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-slate-300" />
                </div>
                <input
                  type="password"
                  name="password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  minLength={8}
                  className="block w-full pl-10 pr-3 py-2.5 border-2 border-slate-300 rounded-xl text-slate-900 placeholder-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-400"
                />
              </div>
            </div>

            <div>
              <label htmlFor="adminId" className="block text-sm font-medium text-slate-600 mb-1.5">
                Confirm Password <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-slate-300" />
                </div>
                <input
                  type="password"
                  name="confirmPassword"
                  required
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  minLength={8}
                  className="block w-full pl-10 pr-3 py-2.5 border-2 border-slate-300 rounded-xl text-slate-900 placeholder-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-400"
                />
              </div>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-slate-600 mb-1.5">
                Profile Image (Optional)
              </label>
              {imagePreview ? (
                <div className="relative inline-block">
                  <img
                    src={imagePreview}
                    alt="Profile preview"
                    className="w-32 h-32 object-cover rounded-lg border-2 border-slate-300"
                  />
                  <button
                    type="button"
                    onClick={removeImage}
                    className="absolute top-0 right-0 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
                  >
                    <X size={16} />
                  </button>
                </div>
              ) : (
                <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-slate-300 border-dashed rounded-lg cursor-pointer bg-slate-50 hover:bg-slate-100 transition-colors">
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <Upload className="w-8 h-8 mb-2 text-slate-400" />
                    <p className="mb-2 text-sm text-slate-500">
                      <span className="font-semibold">Click to upload</span> or drag and drop
                    </p>
                    <p className="text-xs text-slate-400">PNG, JPG, GIF up to 5MB</p>
                  </div>
                  <input
                    type="file"
                    className="hidden"
                    accept="image/*"
                    onChange={handleImageChange}
                  />
                </label>
              )}
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-300 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating Account...' : 'Create Admin Account'}
            </button>
          </div>

          <div className="text-center">
              <p className="text-sm text-slate-500">
              Already have an admin account?{' '}
              <Link to="/admin/login" className="font-medium text-slate-600 hover:text-slate-700">
                Sign in
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AdminSignupPage;

