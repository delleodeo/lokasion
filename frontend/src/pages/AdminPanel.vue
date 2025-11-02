<template>
  <div class="admin-panel">
    <div class="page-header">
      <h2>Admin Panel</h2>
      <p>Manage system configuration and departments</p>
    </div>

    <div class="admin-grid">
      <div class="admin-card">
        <div class="card-icon">
          <BuildingLibraryIcon />
        </div>
        <h3>Create Department</h3>
        <form @submit.prevent="createDepartment" class="form">
          <div class="input-group">
            <label for="dept-name">Department Name</label>
            <div class="input-wrapper">
              <input 
                type="text" 
                id="dept-name" 
                v-model="departmentName"
                placeholder="e.g., Computer Science"
                required
              >
            </div>
          </div>
          <button type="submit" class="btn-primary" :disabled="isLoading">
            {{ isLoading ? 'Creating...' : 'Create Department' }}
          </button>
        </form>
        <div v-if="message" :class="['message', messageType]">
          {{ message }}
        </div>
      </div>

      <div class="admin-card">
        <div class="card-icon">
          <Cog6ToothIcon />
        </div>
        <h3>System Settings</h3>
        <div class="settings-info">
          <p>Configure system parameters and policies</p>
          <button class="btn-secondary">View Settings</button>
        </div>
      </div>

      <div class="admin-card">
        <div class="card-icon">
          <ChartBarIcon />
        </div>
        <h3>Analytics</h3>
        <div class="settings-info">
          <p>View system statistics and reports</p>
          <button class="btn-secondary">View Analytics</button>
        </div>
      </div>

      <div class="admin-card">
        <div class="card-icon">
          <UserGroupIcon />
        </div>
        <h3>User Management</h3>
        <div class="settings-info">
          <p>Manage users and permissions</p>
          <button class="btn-secondary">Manage Users</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../config.js';
import { 
  BuildingLibraryIcon, 
  Cog6ToothIcon, 
  ChartBarIcon, 
  UserGroupIcon 
} from '@heroicons/vue/24/solid';

export default {
  name: 'AdminPanel',
  components: {
    BuildingLibraryIcon,
    Cog6ToothIcon,
    ChartBarIcon,
    UserGroupIcon
  },
  data() {
    return {
      departmentName: '',
      message: '',
      messageType: '',
      isLoading: false
    };
  },
  methods: {
    async createDepartment() {
      this.isLoading = true;
      try {
        const token = localStorage.getItem('token');
        await axios.post(`${API_BASE_URL}/admin/departments`, {
          name: this.departmentName
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.message = `Department "${this.departmentName}" created successfully!`;
        this.messageType = 'success';
        this.departmentName = '';
        setTimeout(() => {
          this.message = '';
        }, 3000);
      } catch (error) {
        console.error('Failed to create department:', error);
        this.message = 'Failed to create department. Please try again.';
        this.messageType = 'error';
      } finally {
        this.isLoading = false;
      }
    }
  }
}
</script>

<style scoped>
.admin-panel {
  max-width: 1400px;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h2 {
  color: var(--dark-green);
  margin-bottom: 0.5rem;
  font-size: 2rem;
}

.page-header p {
  color: var(--gray-600);
}

.admin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.admin-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--gray-200);
  transition: var(--transition);
}

.admin-card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
}

.card-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #198754, #0F5132);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 1rem;
}

.card-icon svg {
  width: 32px;
  height: 32px;
}

.admin-card h3 {
  color: var(--dark-green);
  margin-bottom: 1rem;
  font-size: 1.25rem;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-group label {
  font-weight: 600;
  color: var(--gray-800);
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.input-wrapper input {
  padding: 0.75rem;
  border: 1px solid var(--gray-300);
  border-radius: 8px;
  font-size: 0.95rem;
  transition: var(--transition);
}

.input-wrapper input:focus {
  outline: none;
  border-color: var(--medium-green);
  box-shadow: 0 0 0 3px rgba(25, 135, 84, 0.1);
}

.btn-primary {
  background: linear-gradient(135deg, #198754, #0F5132);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: var(--transition);
  box-shadow: 0 4px 12px rgba(25, 135, 84, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(25, 135, 84, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--gray-100);
  color: var(--dark-green);
  border: 1px solid var(--gray-300);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: var(--transition);
}

.btn-secondary:hover {
  background: var(--gray-200);
}

.message {
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
  animation: slideIn 0.3s ease-out;
}

.message.success {
  background: #D1E7DD;
  color: #0F5132;
  border: 1px solid #198754;
}

.message.error {
  background: #F8D7DA;
  color: #842029;
  border: 1px solid #F5C2C7;
}

.settings-info {
  color: var(--gray-600);
}

.settings-info p {
  margin-bottom: 1rem;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .admin-grid {
    grid-template-columns: 1fr;
  }
}
</style>
