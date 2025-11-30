import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import {
  HiMail,
  HiLockClosed,
  HiUser,
  HiPhone,
  HiLocationMarker,
  HiIdentification,
  HiArrowRight,
} from 'react-icons/hi';
import { userService } from '../../services/api';
import { useAuthStore } from '../../store/authStore';

interface RegisterFormData {
  user_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  password: string;
  confirm_password: string;
}

const US_STATES = [
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
  'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
  'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
  'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
  'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
];

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { loginUser } = useAuthStore();
  const [isLoading, setIsLoading] = React.useState(false);
  const [step, setStep] = React.useState(1);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>();

  const password = watch('password');

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    try {
      const { confirm_password, ...userData } = data;
      await userService.register(userData);
      
      // Auto login after registration
      const loginResponse = await userService.login(data.email, data.password);
      loginUser(loginResponse.user, loginResponse.access_token);
      
      toast.success('Account created successfully!');
      navigate('/');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary-500/10 rounded-full blur-3xl"></div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="card w-full max-w-2xl p-8 relative"
      >
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-dark-950 font-bold text-2xl">K</span>
          </div>
          <h1 className="text-2xl font-display font-bold text-white mb-2">
            Create Your Account
          </h1>
          <p className="text-gray-400">Start planning your next adventure</p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-8">
          <div className="flex items-center space-x-4">
            {[1, 2].map((s) => (
              <React.Fragment key={s}>
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-medium ${
                    step >= s
                      ? 'bg-primary-500 text-dark-950'
                      : 'bg-dark-700 text-gray-400'
                  }`}
                >
                  {s}
                </div>
                {s < 2 && (
                  <div
                    className={`w-16 h-1 rounded ${
                      step > s ? 'bg-primary-500' : 'bg-dark-700'
                    }`}
                  ></div>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)}>
          {step === 1 && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-5"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label className="label">User ID (SSN Format)</label>
                  <div className="relative">
                    <HiIdentification className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                    <input
                      type="text"
                      placeholder="###-##-####"
                      className={`input pl-10 ${errors.user_id ? 'input-error' : ''}`}
                      {...register('user_id', {
                        required: 'User ID is required',
                        pattern: {
                          value: /^[0-9]{3}-[0-9]{2}-[0-9]{4}$/,
                          message: 'Invalid format. Use ###-##-####',
                        },
                      })}
                    />
                  </div>
                  {errors.user_id && (
                    <p className="mt-1 text-sm text-red-400">{errors.user_id.message}</p>
                  )}
                </div>
                <div>
                  <label className="label">Email</label>
                  <div className="relative">
                    <HiMail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                    <input
                      type="email"
                      placeholder="you@example.com"
                      className={`input pl-10 ${errors.email ? 'input-error' : ''}`}
                      {...register('email', {
                        required: 'Email is required',
                        pattern: {
                          value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                          message: 'Invalid email address',
                        },
                      })}
                    />
                  </div>
                  {errors.email && (
                    <p className="mt-1 text-sm text-red-400">{errors.email.message}</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label className="label">First Name</label>
                  <div className="relative">
                    <HiUser className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                    <input
                      type="text"
                      placeholder="John"
                      className={`input pl-10 ${errors.first_name ? 'input-error' : ''}`}
                      {...register('first_name', {
                        required: 'First name is required',
                      })}
                    />
                  </div>
                  {errors.first_name && (
                    <p className="mt-1 text-sm text-red-400">{errors.first_name.message}</p>
                  )}
                </div>
                <div>
                  <label className="label">Last Name</label>
                  <div className="relative">
                    <HiUser className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                    <input
                      type="text"
                      placeholder="Doe"
                      className={`input pl-10 ${errors.last_name ? 'input-error' : ''}`}
                      {...register('last_name', {
                        required: 'Last name is required',
                      })}
                    />
                  </div>
                  {errors.last_name && (
                    <p className="mt-1 text-sm text-red-400">{errors.last_name.message}</p>
                  )}
                </div>
              </div>

              <div>
                <label className="label">Phone Number</label>
                <div className="relative">
                  <HiPhone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="tel"
                    placeholder="(555) 123-4567"
                    className={`input pl-10 ${errors.phone_number ? 'input-error' : ''}`}
                    {...register('phone_number', {
                      required: 'Phone number is required',
                    })}
                  />
                </div>
                {errors.phone_number && (
                  <p className="mt-1 text-sm text-red-400">{errors.phone_number.message}</p>
                )}
              </div>

              <button
                type="button"
                onClick={() => setStep(2)}
                className="btn-primary w-full"
              >
                Continue
                <HiArrowRight className="w-5 h-5 ml-2" />
              </button>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-5"
            >
              <div>
                <label className="label">Address</label>
                <div className="relative">
                  <HiLocationMarker className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="text"
                    placeholder="123 Main Street"
                    className={`input pl-10 ${errors.address ? 'input-error' : ''}`}
                    {...register('address', {
                      required: 'Address is required',
                      minLength: { value: 5, message: 'Address too short' },
                    })}
                  />
                </div>
                {errors.address && (
                  <p className="mt-1 text-sm text-red-400">{errors.address.message}</p>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                <div>
                  <label className="label">City</label>
                  <input
                    type="text"
                    placeholder="San Jose"
                    className={`input ${errors.city ? 'input-error' : ''}`}
                    {...register('city', { required: 'City is required' })}
                  />
                  {errors.city && (
                    <p className="mt-1 text-sm text-red-400">{errors.city.message}</p>
                  )}
                </div>
                <div>
                  <label className="label">State</label>
                  <select
                    className={`input ${errors.state ? 'input-error' : ''}`}
                    {...register('state', { required: 'State is required' })}
                  >
                    <option value="">Select state</option>
                    {US_STATES.map((state) => (
                      <option key={state} value={state}>{state}</option>
                    ))}
                  </select>
                  {errors.state && (
                    <p className="mt-1 text-sm text-red-400">{errors.state.message}</p>
                  )}
                </div>
                <div>
                  <label className="label">ZIP Code</label>
                  <input
                    type="text"
                    placeholder="95112"
                    className={`input ${errors.zip_code ? 'input-error' : ''}`}
                    {...register('zip_code', {
                      required: 'ZIP code is required',
                      pattern: {
                        value: /^[0-9]{5}(-[0-9]{4})?$/,
                        message: 'Invalid ZIP format',
                      },
                    })}
                  />
                  {errors.zip_code && (
                    <p className="mt-1 text-sm text-red-400">{errors.zip_code.message}</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label className="label">Password</label>
                  <div className="relative">
                    <HiLockClosed className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                    <input
                      type="password"
                      placeholder="••••••••"
                      className={`input pl-10 ${errors.password ? 'input-error' : ''}`}
                      {...register('password', {
                        required: 'Password is required',
                        minLength: { value: 8, message: 'At least 8 characters' },
                      })}
                    />
                  </div>
                  {errors.password && (
                    <p className="mt-1 text-sm text-red-400">{errors.password.message}</p>
                  )}
                </div>
                <div>
                  <label className="label">Confirm Password</label>
                  <div className="relative">
                    <HiLockClosed className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                    <input
                      type="password"
                      placeholder="••••••••"
                      className={`input pl-10 ${errors.confirm_password ? 'input-error' : ''}`}
                      {...register('confirm_password', {
                        required: 'Please confirm password',
                        validate: (value) =>
                          value === password || 'Passwords do not match',
                      })}
                    />
                  </div>
                  {errors.confirm_password && (
                    <p className="mt-1 text-sm text-red-400">{errors.confirm_password.message}</p>
                  )}
                </div>
              </div>

              <div className="flex space-x-4">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="btn-secondary flex-1"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="btn-primary flex-1"
                >
                  {isLoading ? (
                    <div className="w-5 h-5 border-2 border-dark-950 border-t-transparent rounded-full animate-spin"></div>
                  ) : (
                    <>
                      Create Account
                      <HiArrowRight className="w-5 h-5 ml-2" />
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          )}
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-400">
            Already have an account?{' '}
            <Link to="/login" className="link">
              Sign in
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default RegisterPage;


