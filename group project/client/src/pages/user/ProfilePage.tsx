import React from 'react';
import { useForm } from 'react-hook-form';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import {
  HiUser,
  HiMail,
  HiPhone,
  HiLocationMarker,
  HiPencil,
  HiCamera,
  HiShieldCheck,
} from 'react-icons/hi';
import { useAuthStore } from '../../store/authStore';
import { userService } from '../../services/api';

const ProfilePage: React.FC = () => {
  const { user, updateUser } = useAuthStore();
  const [isEditing, setIsEditing] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm({
    defaultValues: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      email: user?.email || '',
      phone_number: user?.phone_number || '',
      address: user?.address || '',
      city: user?.city || '',
      state: user?.state || '',
      zip_code: user?.zip_code || '',
    },
  });

  const onSubmit = async (data: any) => {
    setIsLoading(true);
    try {
      const response = await userService.updateProfile(data);
      updateUser(response);
      toast.success('Profile updated successfully!');
      setIsEditing(false);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update profile');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    reset();
    setIsEditing(false);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl font-display font-bold text-white mb-2">
            My Profile
          </h1>
          <p className="text-gray-400">Manage your account settings</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Card */}
          <div className="lg:col-span-1">
            <div className="card p-6 text-center">
              <div className="relative inline-block mb-4">
                <div className="w-24 h-24 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center text-3xl font-bold text-white">
                  {user?.first_name?.charAt(0)}{user?.last_name?.charAt(0)}
                </div>
                <button className="absolute bottom-0 right-0 w-8 h-8 bg-dark-700 rounded-full flex items-center justify-center text-gray-400 hover:text-white hover:bg-dark-600 transition-colors">
                  <HiCamera className="w-4 h-4" />
                </button>
              </div>
              <h2 className="text-xl font-semibold text-white mb-1">
                {user?.first_name} {user?.last_name}
              </h2>
              <p className="text-gray-400 text-sm mb-4">{user?.email}</p>
              
              <div className="flex items-center justify-center space-x-2 mb-6">
                {user?.is_verified ? (
                  <span className="badge-success">
                    <HiShieldCheck className="w-4 h-4 mr-1" />
                    Verified
                  </span>
                ) : (
                  <span className="badge-warning">Pending Verification</span>
                )}
              </div>

              <div className="border-t border-dark-700 pt-4">
                <p className="text-sm text-gray-500 mb-1">Member since</p>
                <p className="text-white">January 2025</p>
              </div>
            </div>
          </div>

          {/* Profile Form */}
          <div className="lg:col-span-2">
            <div className="card p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-white">
                  Personal Information
                </h3>
                {!isEditing && (
                  <button
                    onClick={() => setIsEditing(true)}
                    className="flex items-center space-x-2 text-primary-400 hover:text-primary-300"
                  >
                    <HiPencil className="w-4 h-4" />
                    <span>Edit</span>
                  </button>
                )}
              </div>

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div>
                    <label className="label">First Name</label>
                    <div className="relative">
                      <HiUser className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                      <input
                        type="text"
                        disabled={!isEditing}
                        className={`input pl-10 ${!isEditing ? 'opacity-60' : ''}`}
                        {...register('first_name', { required: true })}
                      />
                    </div>
                  </div>
                  <div>
                    <label className="label">Last Name</label>
                    <div className="relative">
                      <HiUser className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                      <input
                        type="text"
                        disabled={!isEditing}
                        className={`input pl-10 ${!isEditing ? 'opacity-60' : ''}`}
                        {...register('last_name', { required: true })}
                      />
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div>
                    <label className="label">Email</label>
                    <div className="relative">
                      <HiMail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                      <input
                        type="email"
                        disabled={!isEditing}
                        className={`input pl-10 ${!isEditing ? 'opacity-60' : ''}`}
                        {...register('email', { required: true })}
                      />
                    </div>
                  </div>
                  <div>
                    <label className="label">Phone Number</label>
                    <div className="relative">
                      <HiPhone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                      <input
                        type="tel"
                        disabled={!isEditing}
                        className={`input pl-10 ${!isEditing ? 'opacity-60' : ''}`}
                        {...register('phone_number', { required: true })}
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <label className="label">Address</label>
                  <div className="relative">
                    <HiLocationMarker className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                    <input
                      type="text"
                      disabled={!isEditing}
                      className={`input pl-10 ${!isEditing ? 'opacity-60' : ''}`}
                      {...register('address', { required: true })}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                  <div>
                    <label className="label">City</label>
                    <input
                      type="text"
                      disabled={!isEditing}
                      className={`input ${!isEditing ? 'opacity-60' : ''}`}
                      {...register('city', { required: true })}
                    />
                  </div>
                  <div>
                    <label className="label">State</label>
                    <input
                      type="text"
                      disabled={!isEditing}
                      className={`input ${!isEditing ? 'opacity-60' : ''}`}
                      {...register('state', { required: true })}
                    />
                  </div>
                  <div>
                    <label className="label">ZIP Code</label>
                    <input
                      type="text"
                      disabled={!isEditing}
                      className={`input ${!isEditing ? 'opacity-60' : ''}`}
                      {...register('zip_code', { required: true })}
                    />
                  </div>
                </div>

                {isEditing && (
                  <div className="flex space-x-4 pt-4">
                    <button
                      type="button"
                      onClick={handleCancel}
                      className="btn-secondary flex-1"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={isLoading}
                      className="btn-primary flex-1"
                    >
                      {isLoading ? (
                        <div className="w-5 h-5 border-2 border-dark-950 border-t-transparent rounded-full animate-spin"></div>
                      ) : (
                        'Save Changes'
                      )}
                    </button>
                  </div>
                )}
              </form>
            </div>

            {/* Security Section */}
            <div className="card p-6 mt-6">
              <h3 className="text-lg font-semibold text-white mb-4">Security</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-dark-800 rounded-xl">
                  <div>
                    <p className="text-white font-medium">Password</p>
                    <p className="text-gray-400 text-sm">Last changed 30 days ago</p>
                  </div>
                  <button className="btn-secondary text-sm">
                    Change Password
                  </button>
                </div>
                <div className="flex items-center justify-between p-4 bg-dark-800 rounded-xl">
                  <div>
                    <p className="text-white font-medium">Two-Factor Authentication</p>
                    <p className="text-gray-400 text-sm">Add extra security to your account</p>
                  </div>
                  <button className="btn-secondary text-sm">
                    Enable
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default ProfilePage;


