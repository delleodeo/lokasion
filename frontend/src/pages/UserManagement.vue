<template>
  <div class="user-management">
    <div class="page-header">
      <h1>User Management</h1>
      <p>View and edit user details</p>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading users...</p>
    </div>

    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-else class="users-container">
      <!-- Filter Section -->
      <div class="filters">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Search by name, email, or ID number..."
          class="search-input"
        />
        <select v-model="roleFilter" class="role-filter">
          <option value="">All Roles</option>
          <option value="student">Students</option>
          <option value="teacher">Teachers</option>
          <option value="admin">Admins</option>
        </select>
      </div>

      <!-- Users Table -->
      <div class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>ID Number</th>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Department</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user._id">
              <td>{{ user.id_number }}</td>
              <td>{{ user.first_name }} {{ user.last_name }}</td>
              <td>{{ user.email }}</td>
              <td>
                <span :class="['role-badge', user.role]">
                  {{ user.role }}
                </span>
              </td>
              <td>{{ getDepartmentName(user.department_id) }}</td>
              <td>
                <button @click="editUser(user)" class="btn-edit">
                  <PencilIcon class="icon" />
                  Edit
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="filteredUsers.length === 0" class="no-results">
          No users found matching your search
        </div>
      </div>
    </div>

    <!-- Edit User Modal -->
    <Transition name="modal-fade">
      <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Edit User</h2>
            <button @click="closeEditModal" class="close-button">✕</button>
          </div>

          <form @submit.prevent="saveUser" class="edit-form">
            <div class="form-grid">
              <div class="form-group">
                <label>First Name *</label>
                <input 
                  v-model="editFormData.first_name" 
                  type="text" 
                  required
                />
              </div>

              <div class="form-group">
                <label>Middle Name</label>
                <input 
                  v-model="editFormData.middle_name" 
                  type="text" 
                />
              </div>

              <div class="form-group">
                <label>Last Name *</label>
                <input 
                  v-model="editFormData.last_name" 
                  type="text" 
                  required
                />
              </div>

              <div class="form-group">
                <label>ID Number *</label>
                <input 
                  v-model="editFormData.id_number" 
                  type="text" 
                  required
                />
              </div>

              <div class="form-group">
                <label>Email *</label>
                <input 
                  v-model="editFormData.email" 
                  type="email" 
                  required
                />
              </div>

              <div class="form-group">
                <label>Role *</label>
                <select v-model="editFormData.role" required>
                  <option value="student">Student</option>
                  <option value="teacher">Teacher</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              <div class="form-group">
                <label>Department</label>
                <select v-model="editFormData.department_id">
                  <option value="">No Department</option>
                  <option 
                    v-for="dept in departments" 
                    :key="dept._id" 
                    :value="dept._id"
                  >
                    {{ dept.name }}
                  </option>
                </select>
              </div>

              <div class="form-group full-width">
                <label>New Password (leave blank to keep current)</label>
                <input 
                  v-model="editFormData.password" 
                  type="password" 
                  placeholder="Enter new password"
                />
              </div>
            </div>

            <div v-if="saveError" class="error-message">
              {{ saveError }}
            </div>

            <div class="modal-actions">
              <button type="button" @click="closeEditModal" class="btn-secondary">
                Cancel
              </button>
              <button type="submit" class="btn-primary" :disabled="saving">
                <span v-if="saving">Saving...</span>
                <span v-else>Save Changes</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- Success Message -->
    <Transition name="fade">
      <div v-if="successMessage" class="success-toast">
        <CheckCircleIcon class="icon" />
        {{ successMessage }}
      </div>
    </Transition>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { PencilIcon, CheckCircleIcon } from '@heroicons/vue/24/outline';

export default {
  name: 'UserManagement',
  components: {
    PencilIcon,
    CheckCircleIcon
  },
  data() {
    return {
      users: [],
      departments: [],
      loading: true,
      error: null,
      searchQuery: '',
      roleFilter: '',
      showEditModal: false,
      editingUser: null,
      editFormData: {
        first_name: '',
        middle_name: '',
        last_name: '',
        id_number: '',
        email: '',
        role: '',
        department_id: '',
        password: ''
      },
      saving: false,
      saveError: null,
      successMessage: ''
    };
  },
  computed: {
    filteredUsers() {
      let filtered = this.users;

      // Filter by role
      if (this.roleFilter) {
        filtered = filtered.filter(u => u.role === this.roleFilter);
      }

      // Filter by search query
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(u => {
          const fullName = `${u.first_name} ${u.last_name}`.toLowerCase();
          return fullName.includes(query) ||
                 u.email.toLowerCase().includes(query) ||
                 u.id_number.toLowerCase().includes(query);
        });
      }

      return filtered;
    }
  },
  async mounted() {
    await this.loadUsers();
    await this.loadDepartments();
  },
  methods: {
    async loadUsers() {
      this.loading = true;
      this.error = null;

      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/admin/users`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.users = response.data;
      } catch (error) {
        console.error('Failed to load users:', error);
        this.error = error.response?.data?.detail || 'Failed to load users';
      } finally {
        this.loading = false;
      }
    },

    async loadDepartments() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/admin/departments`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.departments = response.data;
      } catch (error) {
        console.error('Failed to load departments:', error);
      }
    },

    getDepartmentName(departmentId) {
      if (!departmentId) return 'N/A';
      const dept = this.departments.find(d => d._id === departmentId);
      return dept?.name || 'Unknown';
    },

    editUser(user) {
      this.editingUser = user;
      this.editFormData = {
        first_name: user.first_name || '',
        middle_name: user.middle_name || '',
        last_name: user.last_name || '',
        id_number: user.id_number || '',
        email: user.email || '',
        role: user.role || '',
        department_id: user.department_id || '',
        password: ''
      };
      this.showEditModal = true;
      this.saveError = null;
    },

    closeEditModal() {
      this.showEditModal = false;
      this.editingUser = null;
      this.saveError = null;
    },

    async saveUser() {
      this.saving = true;
      this.saveError = null;

      try {
        const token = localStorage.getItem('token');
        const updateData = {
          first_name: this.editFormData.first_name,
          middle_name: this.editFormData.middle_name,
          last_name: this.editFormData.last_name,
          id_number: this.editFormData.id_number,
          email: this.editFormData.email,
          role: this.editFormData.role,
          department_id: this.editFormData.department_id || null
        };

        // Only include password if it's been set
        if (this.editFormData.password) {
          updateData.password = this.editFormData.password;
        }

        await axios.put(
          `${API_BASE_URL}/admin/users/${this.editingUser._id}`,
          updateData,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        // Reload users
        await this.loadUsers();

        // Show success message
        this.successMessage = 'User updated successfully!';
        setTimeout(() => {
          this.successMessage = '';
        }, 3000);

        this.closeEditModal();

      } catch (error) {
        console.error('Failed to update user:', error);
        this.saveError = error.response?.data?.detail || 'Failed to update user';
      } finally {
        this.saving = false;
      }
    }
  }
};
</script>

<style scoped>
.user-management {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  color: var(--dark-green);
  margin: 0 0 0.5rem 0;
}

.page-header p {
  color: var(--gray-600);
  margin: 0;
}

.loading {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid var(--light-green);
  border-top-color: var(--medium-green);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 8px;
  padding: 1rem;
  color: #c00;
  margin-bottom: 1rem;
}

.users-container {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.search-input,
.role-filter {
  padding: 0.75rem;
  border: 2px solid var(--gray-300);
  border-radius: 8px;
  font-size: 1rem;
}

.search-input {
  flex: 1;
}

.search-input:focus,
.role-filter:focus {
  outline: none;
  border-color: var(--medium-green);
}

.table-container {
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table thead {
  background: var(--light-green);
}

.users-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--dark-green);
  border-bottom: 2px solid var(--medium-green);
}

.users-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--gray-200);
}

.users-table tbody tr:hover {
  background: var(--light-green);
}

.role-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: capitalize;
}

.role-badge.student {
  background: #dbeafe;
  color: #1e40af;
}

.role-badge.teacher {
  background: #fef3c7;
  color: #92400e;
}

.role-badge.admin {
  background: #fce7f3;
  color: #831843;
}

.btn-edit {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--medium-green);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-edit:hover {
  background: var(--dark-green);
  transform: translateY(-2px);
}

.btn-edit .icon {
  width: 16px;
  height: 16px;
}

.no-results {
  text-align: center;
  padding: 3rem;
  color: var(--gray-600);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--light-green);
}

.modal-header h2 {
  margin: 0;
  color: var(--dark-green);
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--gray-600);
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.close-button:hover {
  background: var(--gray-200);
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-weight: 600;
  color: var(--dark-green);
  margin-bottom: 0.5rem;
}

.form-group input,
.form-group select {
  padding: 0.75rem;
  border: 2px solid var(--gray-300);
  border-radius: 6px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--medium-green);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
}

.btn-primary {
  background: var(--medium-green);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--dark-green);
  transform: translateY(-2px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--gray-200);
  color: var(--gray-700);
}

.btn-secondary:hover {
  background: var(--gray-300);
}

.success-toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: var(--medium-green);
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  z-index: 1001;
}

.success-toast .icon {
  width: 24px;
  height: 24px;
}

/* Transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

@media (max-width: 768px) {
  .user-management {
    padding: 1rem;
  }

  .filters {
    flex-direction: column;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .modal-actions {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style>
