import React from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {
  HiSearch,
  HiDotsVertical,
  HiPencil,
  HiTrash,
  HiMail,
  HiPhone,
  HiLocationMarker,
} from 'react-icons/hi';
import { adminService } from '../../services/api';

const AdminUsers: React.FC = () => {
  const [search, setSearch] = React.useState('');
  const [page, setPage] = React.useState(1);
  const [selectedUser, setSelectedUser] = React.useState<any>(null);

  const { data: usersData, isLoading, refetch } = useQuery({
    queryKey: ['admin-users', page, search],
    queryFn: () => adminService.getUsers({ page, page_size: 10, search }),
  });

  // Mock data for development
  const mockUsers = [
    { user_id: '123-45-6789', first_name: 'John', last_name: 'Doe', email: 'john@example.com', city: 'San Jose', state: 'CA', is_active: true },
    { user_id: '234-56-7890', first_name: 'Jane', last_name: 'Smith', email: 'jane@example.com', city: 'Los Angeles', state: 'CA', is_active: true },
    { user_id: '345-67-8901', first_name: 'Mike', last_name: 'Johnson', email: 'mike@example.com', city: 'New York', state: 'NY', is_active: false },
    { user_id: '456-78-9012', first_name: 'Sarah', last_name: 'Williams', email: 'sarah@example.com', city: 'Miami', state: 'FL', is_active: true },
    { user_id: '567-89-0123', first_name: 'David', last_name: 'Brown', email: 'david@example.com', city: 'Seattle', state: 'WA', is_active: true },
  ];

  const users = usersData?.users || mockUsers;

  const handleDelete = async (userId: string) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await adminService.deleteUser(userId);
        toast.success('User deleted successfully');
        refetch();
      } catch (error) {
        toast.error('Failed to delete user');
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">User Management</h2>
          <p className="text-gray-400 text-sm">Manage and view all users</p>
        </div>
        <div className="relative w-72">
          <HiSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input
            type="text"
            placeholder="Search users..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input pl-10"
          />
        </div>
      </div>

      {/* Users Table */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="card overflow-hidden"
      >
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-dark-800">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Contact
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-4 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-700">
              {users.map((user: any) => (
                <tr key={user.user_id} className="hover:bg-dark-800/50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center text-white font-medium">
                        {user.first_name?.charAt(0)}{user.last_name?.charAt(0)}
                      </div>
                      <div>
                        <p className="text-white font-medium">
                          {user.first_name} {user.last_name}
                        </p>
                        <p className="text-gray-500 text-sm">{user.user_id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center text-gray-400 text-sm">
                      <HiMail className="w-4 h-4 mr-2" />
                      {user.email}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center text-gray-400 text-sm">
                      <HiLocationMarker className="w-4 h-4 mr-2" />
                      {user.city}, {user.state}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`badge ${user.is_active ? 'badge-success' : 'badge-error'}`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={() => setSelectedUser(user)}
                        className="p-2 text-gray-400 hover:text-white hover:bg-dark-700 rounded-lg transition-colors"
                      >
                        <HiPencil className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(user.user_id)}
                        className="p-2 text-gray-400 hover:text-red-400 hover:bg-dark-700 rounded-lg transition-colors"
                      >
                        <HiTrash className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-6 py-4 bg-dark-800">
          <p className="text-gray-400 text-sm">
            Showing {users.length} of {usersData?.total || users.length} users
          </p>
          <div className="flex space-x-2">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="btn-secondary text-sm disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={users.length < 10}
              className="btn-secondary text-sm disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default AdminUsers;


