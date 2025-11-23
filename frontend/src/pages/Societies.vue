<template>
  <div class="societies-page">
    <div class="page-header">
      <div>
        <h2>{{ userRole === 'teacher' ? 'Manage Societies' : 'Available Societies' }}</h2>
        <p v-if="userRole === 'teacher'">Request to manage a society and create events</p>
        <p v-else>Browse and enroll in societies to access their events</p>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <p>Loading societies...</p>
    </div>

    <div v-else class="societies-grid">
      <div v-for="society in societies" :key="society._id" class="society-card">
        <div class="society-header">
          <div class="society-icon">
            <BuildingLibraryIcon />
          </div>
          <h3>{{ society.name }}</h3>
        </div>

        <div class="society-body">
          <div class="society-detail">
            <UsersIcon class="detail-icon" />
            <span>Department ID: {{ society._id.slice(0, 8) }}...</span>
          </div>
        </div>

        <div class="society-footer">
          <!-- Student View -->
          <template v-if="userRole === 'student'">
            <button 
              v-if="society.enrollment_status === 'not_enrolled'" 
              @click="requestEnrollment(society._id)"
              class="btn-enroll"
              :disabled="enrolling === society._id"
            >
              <PlusCircleIcon class="btn-icon" />
              <span>{{ enrolling === society._id ? 'Requesting...' : 'Request to Join' }}</span>
            </button>

            <div v-else-if="society.enrollment_status === 'pending'" class="status-badge pending">
              <ClockIcon class="status-icon" />
              <span>Pending Approval</span>
            </div>

            <div v-else-if="society.enrollment_status === 'approved'" class="action-buttons-group">
              <div class="status-badge approved">
                <CheckCircleIcon class="status-icon" />
                <span>Enrolled</span>
              </div>
              <button 
                @click="cancelEnrollment(society.enrollment_id)"
                class="btn-leave-society"
                :disabled="enrolling === society._id"
                title="Leave society"
              >
                <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
                </svg>
                <span>Leave</span>
              </button>
            </div>

            <div v-else-if="society.enrollment_status === 'declined'" class="status-badge declined">
              <XCircleIcon class="status-icon" />
              <span>Request Declined</span>
            </div>
          </template>

          <!-- Teacher View -->
          <template v-else-if="userRole === 'teacher'">
            <button 
              v-if="society.enrollment_status === 'not_enrolled'" 
              @click="requestEnrollment(society._id)"
              class="btn-enroll"
              :disabled="enrolling === society._id"
            >
              <PlusCircleIcon class="btn-icon" />
              <span>{{ enrolling === society._id ? 'Requesting...' : 'Request to Manage' }}</span>
            </button>

            <div v-else-if="society.enrollment_status === 'pending'" class="status-badge-container">
              <div class="status-badge pending">
                <ClockIcon class="status-icon" />
                <span>Pending Admin Approval</span>
              </div>
              <button 
                @click="cancelEnrollment(society.enrollment_id)"
                class="btn-cancel-enrollment"
                :disabled="enrolling === society._id"
                title="Cancel request"
              >
                <XCircleIcon class="btn-icon" />
                <span>Cancel</span>
              </button>
            </div>

            <div v-else-if="society.enrollment_status === 'approved'" class="action-buttons-group">
              <button 
                @click="createEvent(society._id, society.name)"
                class="btn-create-event"
              >
                <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                <span>Create Event</span>
              </button>
              <button 
                @click="cancelEnrollment(society.enrollment_id)"
                class="btn-leave-society"
                :disabled="enrolling === society._id"
                title="Leave society"
              >
                <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
                </svg>
                <span>Leave</span>
              </button>
            </div>

            <div v-else-if="society.enrollment_status === 'declined'" class="status-badge declined">
              <XCircleIcon class="status-icon" />
              <span>Request Declined</span>
            </div>
          </template>
        </div>
      </div>
    </div>

    <div v-if="!loading && societies.length === 0" class="empty-state">
      <BuildingLibraryIcon class="empty-icon" />
      <p>No societies available at the moment</p>
    </div>

    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../config.js';
import { jwtDecode } from 'jwt-decode';
import { 
  BuildingLibraryIcon, 
  UsersIcon, 
  PlusCircleIcon, 
  ClockIcon, 
  CheckCircleIcon,
  XCircleIcon 
} from '@heroicons/vue/24/solid';

export default {
  name: 'Societies',
  components: {
    BuildingLibraryIcon,
    UsersIcon,
    PlusCircleIcon,
    ClockIcon,
    CheckCircleIcon,
    XCircleIcon
  },
  data() {
    return {
      societies: [],
      loading: true,
      enrolling: null,
      message: '',
      messageType: '',
      userRole: ''
    };
  },
  async created() {
    const token = localStorage.getItem('token');
    if (token) {
      const decoded = jwtDecode(token);
      this.userRole = decoded.role;
    }
    await this.fetchSocieties();
  },
  methods: {
    async fetchSocieties() {
      try {
        this.loading = true;
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/enrollments/societies`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.societies = response.data;
      } catch (error) {
        console.error('Failed to fetch societies:', error);
        this.message = 'Failed to load societies';
        this.messageType = 'error';
      } finally {
        this.loading = false;
      }
    },
    async requestEnrollment(societyId) {
      try {
        this.enrolling = societyId;
        const token = localStorage.getItem('token');
        const decoded = jwtDecode(token);
        const userRole = decoded.role;
        
        await axios.post(`${API_BASE_URL}/enrollments/request`, {
          department_id: societyId
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (userRole === 'teacher') {
          this.message = 'Enrollment request submitted! Wait for admin approval.';
        } else {
          this.message = 'Enrollment request submitted! Wait for teacher approval.';
        }
        this.messageType = 'success';
        
        // Refresh societies to update status
        await this.fetchSocieties();
        
        setTimeout(() => {
          this.message = '';
        }, 3000);
      } catch (error) {
        console.error('Failed to request enrollment:', error);
        this.message = error.response?.data?.detail || 'Failed to submit enrollment request';
        this.messageType = 'error';
      } finally {
        this.enrolling = null;
      }
    },
    async cancelEnrollment(enrollmentId) {
      if (!confirm('Are you sure you want to cancel this enrollment?')) {
        return;
      }
      
      try {
        this.enrolling = enrollmentId;
        const token = localStorage.getItem('token');
        
        await axios.delete(`${API_BASE_URL}/enrollments/${enrollmentId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        this.message = 'Successfully left the society';
        this.messageType = 'success';
        
        // Refresh societies to update status
        await this.fetchSocieties();
        
        setTimeout(() => {
          this.message = '';
        }, 3000);
      } catch (error) {
        console.error('Failed to cancel enrollment:', error);
        this.message = error.response?.data?.detail || 'Failed to cancel enrollment';
        this.messageType = 'error';
      } finally {
        this.enrolling = null;
      }
    },
    createEvent(departmentId, departmentName) {
      // Navigate to create event page with department info as query params
      this.$router.push({
        name: 'CreateEvent',
        query: { departmentId, departmentName }
      });
    }
  }
}
</script>

<style scoped>
.societies-page {
  max-width: 1400px;
}

.page-header {
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

.loading-state {
  text-align: center;
  padding: 3rem;
  color: var(--gray-600);
}

.societies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.society-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--gray-200);
  transition: var(--transition);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.society-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
}

.society-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.society-icon {
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

.society-icon svg {
  width: 30px;
  height: 30px;
}

.society-header h3 {
  color: var(--dark-green);
  font-size: 1.25rem;
  margin: 0;
  font-weight: 700;
}

.society-body {
  flex: 1;
}

.society-detail {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--gray-600);
  font-size: 0.95rem;
}

.detail-icon {
  width: 18px;
  height: 18px;
  color: var(--medium-green);
  flex-shrink: 0;
}

.society-footer {
  margin-top: auto;
}

.btn-enroll {
  width: 100%;
  padding: 0.875rem;
  background: linear-gradient(135deg, #198754, #0F5132);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  box-shadow: 0 4px 15px rgba(25, 135, 84, 0.3);
}

.btn-enroll:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(25, 135, 84, 0.4);
}

.btn-enroll:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.action-buttons-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.btn-create-event {
  width: 100%;
  padding: 0.875rem;
  background: linear-gradient(135deg, #4F46E5, #7C3AED);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
  font-size: 0.95rem;
}

.btn-create-event:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4);
  background: linear-gradient(135deg, #4338CA, #6D28D9);
}

.btn-leave-society {
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(135deg, #EF4444, #DC2626);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
  font-size: 0.875rem;
}

.btn-leave-society:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
  background: linear-gradient(135deg, #DC2626, #B91C1C);
}

.btn-leave-society:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.status-badge-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.btn-cancel-enrollment {
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(135deg, #6B7280, #4B5563);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(107, 114, 128, 0.3);
  font-size: 0.875rem;
}

.btn-cancel-enrollment:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(107, 114, 128, 0.4);
  background: linear-gradient(135deg, #4B5563, #374151);
}

.btn-cancel-enrollment:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  width: 20px;
  height: 20px;
}

.status-badge {
  width: 100%;
  padding: 0.875rem;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 0.95rem;
}

.status-badge.pending {
  background: #FFF3CD;
  color: #856404;
  border: 2px solid #FFE69C;
}

.status-badge.approved {
  background: #D1E7DD;
  color: #0F5132;
  border: 2px solid #198754;
}

.status-badge.declined {
  background: #F8D7DA;
  color: #842029;
  border: 2px solid #F5C2C7;
}

.status-icon {
  width: 20px;
  height: 20px;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--gray-600);
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1rem;
  color: var(--gray-400);
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

@media (max-width: 768px) {
  .societies-grid {
    grid-template-columns: 1fr;
  }
}
</style>
