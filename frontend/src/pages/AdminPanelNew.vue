<template>
  <div class="admin-panel-wrapper">
    <div class="admin-panel">
      <div class="page-header">
        <div class="header-content">
          <div class="title-group">
            <h2 class="page-title">Admin Dashboard</h2>
            <p class="page-subtitle">Manage departments, teachers, and generate system reports</p>
          </div>
          <div class="stats-badge">
            <div class="stats-number">{{ totalDepartments }}</div>
            <div class="stats-label">Departments</div>
          </div>
        </div>
      </div>

    <!-- Tab Navigation -->
    <div class="tabs-container">
      <button 
        @click="activeTab = 'departments'"
        :class="['tab-button', { active: activeTab === 'departments' }]"
      >
        <BuildingLibraryIcon class="tab-icon" />
        <span>Manage Departments</span>
      </button>
      <button 
        @click="activeTab = 'reports'"
        :class="['tab-button', { active: activeTab === 'reports' }]"
      >
        <DocumentArrowDownIcon class="tab-icon" />
        <span>Reports</span>
      </button>
    </div>

    <!-- Departments Tab -->
    <div v-if="activeTab === 'departments'" class="departments-section">
      <!-- Add Department Form -->
      <div class="admin-card featured-card">
        <div class="card-header">
          <div class="card-icon">
            <BuildingLibraryIcon />
          </div>
          <div>
            <h3>{{ editingDepartment ? 'Edit Department' : 'Create Department' }}</h3>
            <p class="card-subtitle">{{ editingDepartment ? 'Update department information' : 'Add a new department or society' }}</p>
          </div>
        </div>
        
        <form @submit.prevent="editingDepartment ? updateDepartment() : createDepartment()" class="form">
          <div class="input-group">
            <label for="dept-name">Department Name</label>
            <div class="input-wrapper">
              <input 
                type="text" 
                id="dept-name" 
                v-model="departmentName"
                placeholder="e.g., Computer Science Society"
                required
              >
            </div>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn-primary" :disabled="isLoading">
              <PlusCircleIcon v-if="!editingDepartment" class="btn-icon" />
              <svg v-else class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              <span>{{ isLoading ? 'Processing...' : (editingDepartment ? 'Update Department' : 'Create Department') }}</span>
            </button>
            <button v-if="editingDepartment" type="button" @click="cancelEdit" class="btn-secondary">
              Cancel
            </button>
          </div>
        </form>
        
        <div v-if="message" :class="['message', messageType]">
          {{ message }}
        </div>
      </div>

      <!-- Departments List -->
      <div class="admin-card">
        <div class="card-header">
          <div class="card-icon">
            <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
            </svg>
          </div>
          <div>
            <h3>All Departments</h3>
            <p class="card-subtitle">View and manage existing departments</p>
          </div>
        </div>

        <div v-if="loadingDepartments" class="loading-state">
          <div class="spinner"></div>
          <p>Loading departments...</p>
        </div>

        <div v-else-if="departments.length === 0" class="empty-state">
          <BuildingLibraryIcon class="empty-icon" />
          <p>No departments created yet</p>
        </div>

        <div v-else class="departments-list">
          <div v-for="dept in departments" :key="dept._id" class="department-item">
            <div class="dept-info">
              <div class="dept-icon">
                <BuildingLibraryIcon />
              </div>
              <div class="dept-details">
                <h4 class="dept-name">{{ dept.name }}</h4>
                <p class="dept-id">ID: {{ dept._id }}</p>
              </div>
            </div>
            <div class="dept-actions">
              <button @click="editDepartment(dept)" class="btn-edit" title="Edit">
                <svg class="icon-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                </svg>
              </button>
              <button @click="confirmDelete(dept)" class="btn-delete" title="Delete">
                <svg class="icon-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Reports Tab -->
    <div v-if="activeTab === 'reports'" class="admin-grid">
      <!-- Export Attendance Card -->
      <div class="admin-card export-card">
        <div class="card-header">
          <div class="card-icon export-icon">
            <DocumentArrowDownIcon />
          </div>
          <div>
            <h3>Export Attendance</h3>
            <p class="card-subtitle">Download attendance records as Excel</p>
          </div>
        </div>
        
        <div class="export-options">
          <div class="input-group">
            <label for="department-select">Filter by Department</label>
            <select id="department-select" v-model="selectedDepartment" class="select-input">
              <option value="">All Departments</option>
              <option v-for="dept in departments" :key="dept._id" :value="dept._id">
                {{ dept.name }}
              </option>
            </select>
          </div>
          
          <button @click="exportAttendance" class="btn-export" :disabled="isExporting">
            <ArrowDownTrayIcon class="btn-icon" />
            <span>{{ isExporting ? 'Generating...' : 'Export to Excel' }}</span>
          </button>
        </div>
        
        <div v-if="exportMessage" :class="['message', exportMessageType]">
          {{ exportMessage }}
        </div>
      </div>

      <!-- Statistics Card -->
      <div class="admin-card stats-card">
        <div class="card-header">
          <div class="card-icon stats-icon">
            <ChartBarIcon />
          </div>
          <div>
            <h3>System Statistics</h3>
            <p class="card-subtitle">Overview of system data</p>
          </div>
        </div>
        
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">{{ totalUsers }}</div>
            <div class="stat-text">Total Users</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ totalEvents }}</div>
            <div class="stat-text">Total Events</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ totalAttendance }}</div>
            <div class="stat-text">Attendance Records</div>
          </div>
        </div>
      </div>

      <!-- Quick Actions Card -->
      <div class="admin-card actions-card">
        <div class="card-header">
          <div class="card-icon settings-icon">
            <Cog6ToothIcon />
          </div>
          <div>
            <h3>Quick Actions</h3>
            <p class="card-subtitle">Manage system settings</p>
          </div>
        </div>
        
        <div class="action-buttons">
          <button class="action-btn" @click="viewDepartments">
            <BuildingLibraryIcon class="action-icon" />
            <span>View All Departments</span>
          </button>
          <button class="action-btn" @click="viewUsers">
            <UserGroupIcon class="action-icon" />
            <span>Manage Users</span>
          </button>
          <button class="action-btn" @click="viewReports">
            <DocumentChartBarIcon class="action-icon" />
            <span>View Reports</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="showDeleteModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <svg class="modal-icon warning-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
          </svg>
          <h3>Delete Department</h3>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete <strong>{{ departmentToDelete?.name }}</strong>?</p>
          <p class="warning-text">This action cannot be undone. All associated data may be affected.</p>
        </div>
        <div class="modal-actions">
          <button @click="showDeleteModal = false" class="btn-cancel">Cancel</button>
          <button @click="deleteDepartment" class="btn-confirm-delete" :disabled="isDeleting">
            {{ isDeleting ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
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
  UserGroupIcon,
  PlusCircleIcon,
  DocumentArrowDownIcon,
  ArrowDownTrayIcon,
  DocumentChartBarIcon
} from '@heroicons/vue/24/solid';

export default {
  name: 'AdminPanel',
  components: {
    BuildingLibraryIcon,
    Cog6ToothIcon,
    ChartBarIcon,
    UserGroupIcon,
    PlusCircleIcon,
    DocumentArrowDownIcon,
    ArrowDownTrayIcon,
    DocumentChartBarIcon
  },
  data() {
    return {
      activeTab: 'departments',
      departmentName: '',
      message: '',
      messageType: '',
      isLoading: false,
      loadingDepartments: false,
      departments: [],
      selectedDepartment: '',
      isExporting: false,
      exportMessage: '',
      exportMessageType: '',
      totalDepartments: 0,
      totalUsers: 0,
      totalEvents: 0,
      totalAttendance: 0,
      editingDepartment: null,
      showDeleteModal: false,
      departmentToDelete: null,
      isDeleting: false
    };
  },
  async created() {
    await this.fetchDepartments();
    await this.fetchStatistics();
  },
  methods: {
    async fetchDepartments() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/admin/departments`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.departments = response.data || [];
        this.totalDepartments = this.departments.length;
      } catch (error) {
        console.error('Failed to fetch departments:', error);
      }
    },
    async fetchStatistics() {
      try {
        const token = localStorage.getItem('token');
        // Fetch statistics from various endpoints
        // Note: You may need to add these endpoints in the backend
        this.totalUsers = 0; // Placeholder
        this.totalEvents = 0; // Placeholder
        this.totalAttendance = 0; // Placeholder
      } catch (error) {
        console.error('Failed to fetch statistics:', error);
      }
    },
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
        await this.fetchDepartments();
        setTimeout(() => {
          this.message = '';
        }, 3000);
      } catch (error) {
        console.error('Failed to create department:', error);
        this.message = error.response?.data?.detail || 'Failed to create department. Please try again.';
        this.messageType = 'error';
      } finally {
        this.isLoading = false;
      }
    },
    editDepartment(dept) {
      this.editingDepartment = dept;
      this.departmentName = dept.name;
      this.message = '';
      // Scroll to form
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    cancelEdit() {
      this.editingDepartment = null;
      this.departmentName = '';
      this.message = '';
    },
    async updateDepartment() {
      this.isLoading = true;
      try {
        const token = localStorage.getItem('token');
        await axios.put(`${API_BASE_URL}/admin/departments/${this.editingDepartment._id}`, {
          name: this.departmentName
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.message = `Department updated successfully!`;
        this.messageType = 'success';
        this.departmentName = '';
        this.editingDepartment = null;
        await this.fetchDepartments();
        setTimeout(() => {
          this.message = '';
        }, 3000);
      } catch (error) {
        console.error('Failed to update department:', error);
        this.message = error.response?.data?.detail || 'Failed to update department. Please try again.';
        this.messageType = 'error';
      } finally {
        this.isLoading = false;
      }
    },
    confirmDelete(dept) {
      this.departmentToDelete = dept;
      this.showDeleteModal = true;
    },
    async deleteDepartment() {
      this.isDeleting = true;
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`${API_BASE_URL}/admin/departments/${this.departmentToDelete._id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.message = `Department "${this.departmentToDelete.name}" deleted successfully!`;
        this.messageType = 'success';
        this.showDeleteModal = false;
        this.departmentToDelete = null;
        await this.fetchDepartments();
        setTimeout(() => {
          this.message = '';
        }, 3000);
      } catch (error) {
        console.error('Failed to delete department:', error);
        this.message = error.response?.data?.detail || 'Failed to delete department. Please try again.';
        this.messageType = 'error';
        this.showDeleteModal = false;
      } finally {
        this.isDeleting = false;
      }
    },
    async exportAttendance() {
      this.isExporting = true;
      this.exportMessage = '';
      try {
        const token = localStorage.getItem('token');
        const params = this.selectedDepartment ? `?department_id=${this.selectedDepartment}` : '';
        
        const response = await axios.get(`${API_BASE_URL}/admin/export/attendance${params}`, {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        });
        
        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `attendance_report_${new Date().getTime()}.xlsx`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        
        this.exportMessage = 'Attendance report downloaded successfully!';
        this.exportMessageType = 'success';
        
        setTimeout(() => {
          this.exportMessage = '';
        }, 3000);
      } catch (error) {
        console.error('Failed to export attendance:', error);
        this.exportMessage = 'Failed to export attendance. Please try again.';
        this.exportMessageType = 'error';
      } finally {
        this.isExporting = false;
      }
    },
    viewDepartments() {
      alert('View Departments feature - Coming soon!');
    },
    viewUsers() {
      alert('Manage Users feature - Coming soon!');
    },
    viewReports() {
      alert('View Reports feature - Coming soon!');
    }
  }
}
</script>

<style scoped>
.admin-panel-wrapper {
  min-height: 100vh;
  background: linear-gradient(to bottom right, #F0FDF4, #FFFFFF, #ECFDF5);
  padding: 2rem;
}

.admin-panel {
  max-width: 1600px;
  margin: 0 auto;
}

/* Header Section */
.page-header {
  margin-bottom: 2.5rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.title-group {
  flex: 1;
  min-width: 300px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(to right, #198754, #0F5132);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
  line-height: 1.2;
}

.page-subtitle {
  color: #6B7280;
  font-size: 1rem;
  margin: 0;
}

.stats-badge {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  padding: 1.5rem 2rem;
  border: 2px solid #D1FAE5;
  text-align: center;
  min-width: 150px;
  transition: all 0.3s ease;
}

.stats-badge:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.stats-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: #198754;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stats-label {
  font-size: 0.875rem;
  color: #6B7280;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.admin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 2rem;
}

.admin-card {
  background: white;
  border-radius: 1.25rem;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #F3F4F6;
  transition: all 0.3s ease;
}

.admin-card:hover {
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.featured-card {
  background: linear-gradient(to bottom, rgba(25, 135, 84, 0.02), white);
  border: 2px solid #D1FAE5;
}

.export-card {
  background: linear-gradient(to bottom, rgba(13, 110, 253, 0.02), white);
  border: 2px solid #CCE5FF;
}

.stats-card {
  background: linear-gradient(to bottom, rgba(111, 66, 193, 0.02), white);
  border: 2px solid #E9D5FF;
}

.actions-card {
  background: linear-gradient(to bottom, rgba(253, 126, 20, 0.02), white);
  border: 2px solid #FFEDD5;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.card-header h3 {
  font-size: 1.375rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.card-subtitle {
  font-size: 0.938rem;
  color: #6B7280;
  margin: 0.25rem 0 0 0;
}

.card-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #198754, #0F5132);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 15px rgba(25, 135, 84, 0.3);
}

.export-icon {
  background: linear-gradient(135deg, #0d6efd, #0a58ca);
  box-shadow: 0 4px 15px rgba(13, 110, 253, 0.3);
}

.stats-icon {
  background: linear-gradient(135deg, #6f42c1, #5a32a3);
  box-shadow: 0 4px 15px rgba(111, 66, 193, 0.3);
}

.settings-icon {
  background: linear-gradient(135deg, #fd7e14, #dc6502);
  box-shadow: 0 4px 15px rgba(253, 126, 20, 0.3);
}

.card-icon svg {
  width: 34px;
  height: 34px;
}

.card-header h3 {
  color: var(--dark-green);
  margin: 0;
  font-size: 1.35rem;
  font-weight: 700;
}

.card-subtitle {
  color: var(--gray-600);
  font-size: 0.9rem;
  margin: 0.25rem 0 0 0;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-group label {
  font-weight: 600;
  color: var(--gray-800);
  margin-bottom: 0.75rem;
  font-size: 0.95rem;
}

.input-wrapper input,
.select-input {
  padding: 1rem 1.25rem;
  border: 2px solid #E5E7EB;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #F9FAFB;
}

.input-wrapper input:focus,
.select-input:focus {
  outline: none;
  border-color: #198754;
  background: white;
  box-shadow: 0 0 0 4px rgba(25, 135, 84, 0.1);
  transform: translateY(-1px);
}

.select-input {
  cursor: pointer;
  width: 100%;
}

.btn-primary,
.btn-export,
.btn-secondary {
  color: white;
  border: none;
  padding: 1rem 1.75rem;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.btn-primary {
  background: linear-gradient(135deg, #198754, #0F5132);
  box-shadow: 0 4px 15px rgba(25, 135, 84, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(25, 135, 84, 0.4);
  background: linear-gradient(135deg, #0F5132, #0A3622);
}

.btn-secondary {
  background: linear-gradient(135deg, #6B7280, #4B5563);
  box-shadow: 0 4px 15px rgba(107, 114, 128, 0.3);
}

.btn-secondary:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(107, 114, 128, 0.4);
  background: linear-gradient(135deg, #4B5563, #374151);
}

.btn-export {
  background: linear-gradient(135deg, #0d6efd, #0a58ca);
  box-shadow: 0 4px 15px rgba(13, 110, 253, 0.3);
}

.btn-export:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(13, 110, 253, 0.4);
  background: linear-gradient(135deg, #0a58ca, #084298);
}

.btn-export:hover:not(:disabled) {
  box-shadow: 0 6px 20px rgba(13, 110, 253, 0.4);
}

.btn-primary:disabled,
.btn-export:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  width: 22px;
  height: 22px;
}

.export-options {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.stat-item {
  text-align: center;
  padding: 1.25rem;
  background: var(--gray-50);
  border-radius: 12px;
  border: 2px solid var(--gray-200);
  transition: var(--transition);
}

.stat-item:hover {
  border-color: var(--medium-green);
  background: white;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--medium-green);
  margin-bottom: 0.5rem;
}

.stat-text {
  font-size: 0.9rem;
  color: var(--gray-600);
  font-weight: 500;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--gray-50);
  border: 2px solid var(--gray-200);
  border-radius: 10px;
  cursor: pointer;
  transition: var(--transition);
  font-weight: 500;
  color: var(--gray-800);
}

.action-btn:hover {
  background: white;
  border-color: var(--medium-green);
  color: var(--medium-green);
  transform: translateX(5px);
}

.action-icon {
  width: 22px;
  height: 22px;
  color: var(--medium-green);
}

.message {
  padding: 1rem;
  border-radius: 10px;
  margin-top: 1rem;
  font-weight: 500;
  animation: slideIn 0.3s ease-out;
}

.message.success {
  background: #D1E7DD;
  color: #0F5132;
  border: 2px solid #198754;
}

.message.error {
  background: #F8D7DA;
  color: #842029;
  border: 2px solid #F5C2C7;
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

@media (max-width: 1200px) {
  .admin-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Tab Navigation */
.tabs-container {
  display: flex;
  gap: 0.5rem;
  background: white;
  border-radius: 12px;
  padding: 0.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.tab-button {
  padding: 0.875rem 1.75rem;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  color: #6B7280;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  justify-content: center;
}

.tab-icon {
  width: 20px;
  height: 20px;
}

.tab-button:hover {
  color: #198754;
  background: rgba(25, 135, 84, 0.08);
}

.tab-button.active {
  color: white;
  background: linear-gradient(135deg, #198754, #0F5132);
  box-shadow: 0 4px 12px rgba(25, 135, 84, 0.3);
}

/* Departments Section */
.departments-section {
  margin-top: 2rem;
}

.departments-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.department-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.75rem;
  background: linear-gradient(to right, rgba(25, 135, 84, 0.02), white);
  border-radius: 14px;
  border: 2px solid #E5E7EB;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.department-item:hover {
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border-color: #198754;
  transform: translateY(-3px);
  background: white;
}

.dept-info {
  display: flex;
  gap: 1.25rem;
  align-items: center;
  flex: 1;
}

.dept-icon {
  width: 56px;
  height: 56px;
  min-width: 56px;
  border-radius: 14px;
  background: linear-gradient(135deg, #198754, #0F5132);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 15px rgba(25, 135, 84, 0.3);
}

.dept-icon svg {
  width: 28px;
  height: 28px;
}

.dept-details {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.dept-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
}

.dept-id {
  font-size: 0.875rem;
  color: #9CA3AF;
  font-family: 'Courier New', monospace;
  background: #F3F4F6;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  display: inline-block;
  width: fit-content;
}

.dept-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-edit,
.btn-delete {
  padding: 0.75rem;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.btn-edit {
  background: linear-gradient(135deg, #3B82F6, #2563EB);
  color: white;
}

.btn-edit:hover {
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
  transform: translateY(-3px) scale(1.05);
  background: linear-gradient(135deg, #2563EB, #1D4ED8);
}

.btn-delete {
  background: linear-gradient(135deg, #EF4444, #DC2626);
  color: white;
}

.btn-delete:hover {
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.5);
  transform: translateY(-3px) scale(1.05);
  background: linear-gradient(135deg, #DC2626, #B91C1C);
}

.btn-edit svg,
.btn-delete svg {
  width: 22px;
  height: 22px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 2.5rem;
  max-width: 540px;
  width: 90%;
  box-shadow: 0 25px 70px rgba(0, 0, 0, 0.35);
  animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.modal-header h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.modal-icon {
  width: 56px;
  height: 56px;
  min-width: 56px;
  border-radius: 14px;
  background: linear-gradient(135deg, #EF4444, #DC2626);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
}

.warning-icon {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
  }
  50% {
    box-shadow: 0 4px 25px rgba(239, 68, 68, 0.6);
  }
}

.modal-icon svg {
  width: 24px;
  height: 24px;
}

.modal-header h3 {
  color: var(--dark-green);
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
}

.modal-body {
  color: #6B7280;
  font-size: 1.0625rem;
  line-height: 1.7;
  margin-bottom: 2rem;
  background: #F9FAFB;
  padding: 1.25rem;
  border-radius: 12px;
  border-left: 4px solid #EF4444;
}

.modal-body p {
  margin: 0 0 0.75rem 0;
}

.modal-body p:last-child {
  margin-bottom: 0;
}

.modal-body strong {
  color: #111827;
  font-weight: 700;
}

.warning-text {
  color: #DC2626;
  font-weight: 600;
  font-size: 0.9375rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-cancel,
.btn-confirm-delete {
  padding: 0.875rem 1.75rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn-cancel {
  background: #F3F4F6;
  color: #4B5563;
}

.btn-cancel:hover {
  background: #E5E7EB;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-confirm-delete {
  background: linear-gradient(135deg, #EF4444, #DC2626);
  color: white;
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
}

.btn-confirm-delete:hover:not(:disabled) {
  box-shadow: 0 6px 25px rgba(239, 68, 68, 0.5);
  transform: translateY(-2px);
  background: linear-gradient(135deg, #DC2626, #B91C1C);
}

.btn-confirm-delete:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Form Actions */
.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.form-actions .btn-cancel {
  background: #E5E7EB;
  color: var(--gray-700);
  padding: 0.875rem 1.5rem;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #E5E7EB;
  border-top-color: var(--medium-green);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-state p {
  color: var(--gray-600);
  font-size: 1rem;
  font-weight: 500;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
  text-align: center;
}

.empty-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(25, 135, 84, 0.1), rgba(15, 81, 50, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--medium-green);
}

.empty-icon svg {
  width: 32px;
  height: 32px;
}

.empty-state p {
  color: var(--gray-600);
  font-size: 1rem;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1rem;
  }

  .header-stats {
    width: 100%;
  }

  .stat-card {
    flex: 1;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .tabs-container {
    overflow-x: auto;
  }

  .department-item {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .dept-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .modal-content {
    padding: 1.5rem;
  }

  .modal-actions {
    flex-direction: column-reverse;
  }

  .btn-cancel,
  .btn-confirm-delete {
    width: 100%;
    justify-content: center;
  }
}
</style>
