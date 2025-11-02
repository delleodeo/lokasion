<template>
  <div class="enrollment-management-page">
    <!-- Tab Navigation -->
    <div class="tabs-container">
      <button 
        @click="activeTab = 'pending'"
        :class="['tab-button', { active: activeTab === 'pending' }]"
      >
        <ClockIcon class="tab-icon" />
        <span>Pending Requests</span>
        <span v-if="pendingEnrollments.length > 0" class="tab-badge">{{ pendingEnrollments.length }}</span>
      </button>
      <button 
        @click="activeTab = 'approved'"
        :class="['tab-button', { active: activeTab === 'approved' }]"
      >
        <CheckCircleIcon class="tab-icon" />
        <span>Enrolled Students</span>
        <span v-if="approvedEnrollments.length > 0" class="tab-badge">{{ approvedEnrollments.length }}</span>
      </button>
    </div>

    <!-- Pending Tab -->
    <div v-if="activeTab === 'pending'">
      <div class="page-header">
        <div>
          <h2>Pending Enrollment Requests</h2>
          <p>Review and approve student enrollment requests</p>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <p>Loading enrollment requests...</p>
      </div>

      <div v-else-if="pendingEnrollments.length === 0" class="empty-state">
        <ClipboardDocumentCheckIcon class="empty-icon" />
        <h3>No Pending Requests</h3>
        <p>All enrollment requests have been reviewed</p>
      </div>

    <div v-else class="enrollments-list">
      <div v-for="enrollment in pendingEnrollments" :key="enrollment._id" class="enrollment-card">
        <div class="enrollment-header">
          <div class="user-avatar">
            {{ getInitials(enrollment.user_name) }}
          </div>
          <div class="user-info">
            <h3>{{ enrollment.user_name }}</h3>
            <p class="user-email">{{ enrollment.user_email }}</p>
          </div>
        </div>

        <div class="enrollment-body">
          <div class="info-row">
            <UserCircleIcon class="info-icon" />
            <div>
              <span class="info-label">Student ID</span>
              <span class="info-value student-id">{{ enrollment.user_id }}</span>
            </div>
          </div>

          <div class="info-row">
            <BuildingLibraryIcon class="info-icon" />
            <div>
              <span class="info-label">Society</span>
              <span class="info-value">{{ enrollment.department_name }}</span>
            </div>
          </div>

          <div class="info-row">
            <ClockIcon class="info-icon" />
            <div>
              <span class="info-label">Requested</span>
              <span class="info-value">{{ formatDate(enrollment.requested_at) }}</span>
            </div>
          </div>
        </div>

        <div class="enrollment-actions">
          <button 
            @click="reviewEnrollment(enrollment._id, 'approved')"
            class="btn-approve"
            :disabled="reviewing === enrollment._id"
          >
            <CheckCircleIcon class="btn-icon" />
            <span>Approve</span>
          </button>
          <button 
            @click="reviewEnrollment(enrollment._id, 'declined')"
            class="btn-decline"
            :disabled="reviewing === enrollment._id"
          >
            <XCircleIcon class="btn-icon" />
            <span>Decline</span>
          </button>
        </div>
      </div>
      </div>
    </div>

    <!-- Approved Tab -->
    <div v-if="activeTab === 'approved'">
      <div class="page-header">
        <div>
          <h2>Enrolled Students</h2>
          <p>Students currently enrolled in your department</p>
        </div>
      </div>

      <div v-if="loadingApproved" class="loading-state">
        <p>Loading enrolled students...</p>
      </div>

      <div v-else-if="approvedEnrollments.length === 0" class="empty-state">
        <UserCircleIcon class="empty-icon" />
        <h3>No Enrolled Students</h3>
        <p>No students have been approved yet</p>
      </div>

      <div v-else class="enrollments-list">
        <div v-for="enrollment in approvedEnrollments" :key="enrollment.enrollment_id" class="enrollment-card approved-card">
          <div class="enrollment-header">
            <div class="user-avatar approved">
              {{ getInitials(enrollment.user_name) }}
            </div>
            <div class="user-info">
              <h3>{{ enrollment.user_name }}</h3>
              <p class="user-email">{{ enrollment.user_email }}</p>
            </div>
          </div>

          <div class="enrollment-body">
            <div class="info-row">
              <UserCircleIcon class="info-icon" />
              <div>
                <span class="info-label">Student ID</span>
                <span class="info-value student-id">{{ enrollment.user_id }}</span>
              </div>
            </div>

            <div class="info-row">
              <BuildingLibraryIcon class="info-icon" />
              <div>
                <span class="info-label">Society</span>
                <span class="info-value">{{ enrollment.department_name }}</span>
              </div>
            </div>

            <div class="info-row">
              <CheckCircleIcon class="info-icon" />
              <div>
                <span class="info-label">Approved</span>
                <span class="info-value">{{ formatDate(enrollment.approved_at) }}</span>
              </div>
            </div>
          </div>

          <div class="enrollment-status">
            <div class="status-badge-approved">
              <CheckCircleIcon class="status-icon" />
              <span>Enrolled</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../config.js';
import { 
  ClipboardDocumentCheckIcon,
  BuildingLibraryIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  UserCircleIcon
} from '@heroicons/vue/24/solid';

export default {
  name: 'EnrollmentManagement',
  components: {
    ClipboardDocumentCheckIcon,
    BuildingLibraryIcon,
    ClockIcon,
    CheckCircleIcon,
    XCircleIcon,
    UserCircleIcon
  },
  data() {
    return {
      activeTab: 'pending',
      pendingEnrollments: [],
      approvedEnrollments: [],
      loading: true,
      loadingApproved: false,
      reviewing: null,
      message: '',
      messageType: ''
    };
  },
  watch: {
    activeTab(newTab) {
      if (newTab === 'approved' && this.approvedEnrollments.length === 0) {
        this.fetchApprovedEnrollments();
      }
    }
  },
  async created() {
    await this.fetchPendingEnrollments();
  },
  methods: {
    async fetchPendingEnrollments() {
      try {
        this.loading = true;
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/enrollments/pending`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.pendingEnrollments = response.data;
      } catch (error) {
        console.error('Failed to fetch pending enrollments:', error);
        this.message = 'Failed to load enrollment requests';
        this.messageType = 'error';
      } finally {
        this.loading = false;
      }
    },
    async fetchApprovedEnrollments() {
      try {
        this.loadingApproved = true;
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/enrollments/approved`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.approvedEnrollments = response.data;
      } catch (error) {
        console.error('Failed to fetch approved enrollments:', error);
        this.message = 'Failed to load enrolled students';
        this.messageType = 'error';
      } finally {
        this.loadingApproved = false;
      }
    },
    async reviewEnrollment(enrollmentId, action) {
      try {
        this.reviewing = enrollmentId;
        const token = localStorage.getItem('token');
        await axios.post(`${API_BASE_URL}/enrollments/review/${enrollmentId}`, {
          action: action
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        this.message = `Enrollment ${action === 'approved' ? 'approved' : 'declined'} successfully!`;
        this.messageType = 'success';
        
        // Refresh the lists
        await this.fetchPendingEnrollments();
        if (action === 'approved' && this.approvedEnrollments.length > 0) {
          await this.fetchApprovedEnrollments();
        }
        
        setTimeout(() => {
          this.message = '';
        }, 3000);
      } catch (error) {
        console.error('Failed to review enrollment:', error);
        this.message = error.response?.data?.detail || 'Failed to review enrollment';
        this.messageType = 'error';
      } finally {
        this.reviewing = null;
      }
    },
    getInitials(name) {
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleString();
    }
  }
}
</script>

<style scoped>
.enrollment-management-page {
  max-width: 1200px;
}

.tabs-container {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid var(--gray-200);
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  color: var(--gray-600);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  margin-bottom: -2px;
}

.tab-button:hover {
  color: var(--medium-green);
  background: var(--light-green);
}

.tab-button.active {
  color: var(--dark-green);
  border-bottom-color: var(--medium-green);
  background: linear-gradient(to bottom, var(--light-green), transparent);
}

.tab-icon {
  width: 20px;
  height: 20px;
}

.tab-badge {
  background: var(--medium-green);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
  min-width: 24px;
  text-align: center;
}

.tab-button.active .tab-badge {
  background: var(--dark-green);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.page-header h2 {
  color: var(--dark-green);
  margin-bottom: 0.5rem;
  font-size: 2rem;
  font-weight: 700;
}

.page-header p {
  color: var(--gray-600);
  font-size: 1rem;
}

.header-badge {
  background: linear-gradient(135deg, #198754, #0F5132);
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  color: white;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 4px 15px rgba(25, 135, 84, 0.3);
}

.badge-count {
  font-size: 1.75rem;
  font-weight: 700;
}

.badge-text {
  font-size: 0.9rem;
  opacity: 0.9;
}

.loading-state {
  text-align: center;
  padding: 3rem;
  color: var(--gray-600);
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 16px;
  border: 2px dashed var(--gray-300);
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1rem;
  color: var(--gray-400);
}

.empty-state h3 {
  color: var(--dark-green);
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: var(--gray-600);
}

.enrollments-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.enrollment-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--gray-200);
  transition: var(--transition);
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 2rem;
  align-items: center;
}

.enrollment-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.enrollment-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-avatar {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #198754, #0F5132);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.user-info h3 {
  color: var(--dark-green);
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.user-email {
  color: var(--gray-600);
  font-size: 0.9rem;
  margin: 0;
}

.enrollment-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.info-icon {
  width: 20px;
  height: 20px;
  color: var(--medium-green);
  flex-shrink: 0;
}

.info-label {
  display: block;
  font-size: 0.85rem;
  color: var(--gray-600);
}

.info-value {
  display: block;
  font-weight: 600;
  color: var(--gray-800);
  font-size: 0.95rem;
}

.student-id {
  font-family: 'Courier New', monospace;
  background: var(--light-green);
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-size: 0.85rem;
  color: var(--dark-green);
  border: 1px solid var(--medium-green);
}

.enrollment-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 140px;
}

.btn-approve,
.btn-decline {
  padding: 0.75rem 1.25rem;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-approve {
  background: linear-gradient(135deg, #198754, #0F5132);
  color: white;
  box-shadow: 0 4px 12px rgba(25, 135, 84, 0.3);
}

.btn-approve:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(25, 135, 84, 0.4);
}

.btn-decline {
  background: white;
  color: #dc3545;
  border: 2px solid #dc3545;
}

.btn-decline:hover:not(:disabled) {
  background: #dc3545;
  color: white;
  transform: translateY(-2px);
}

.btn-approve:disabled,
.btn-decline:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.message {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  border-radius: 10px;
  font-weight: 500;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease-out;
  z-index: 1000;
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

.approved-card {
  border: 2px solid var(--light-green);
  background: linear-gradient(135deg, #ffffff 0%, #f0fff4 100%);
}

.user-avatar.approved {
  background: linear-gradient(135deg, #10b981, #059669);
}

.enrollment-status {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 140px;
}

.status-badge-approved {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, #D1FAE5, #A7F3D0);
  color: #065F46;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.9rem;
  border: 2px solid #10B981;
}

.status-icon {
  width: 20px;
  height: 20px;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(100px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@media (max-width: 1024px) {
  .enrollment-card {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .enrollment-actions {
    flex-direction: row;
    width: 100%;
  }

  .enrollment-actions button {
    flex: 1;
  }
}
</style>
