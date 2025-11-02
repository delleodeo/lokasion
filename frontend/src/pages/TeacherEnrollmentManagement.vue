<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-6">
    <div class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="header-section">
        <div class="header-content">
          <div class="title-group">
            <h1 class="page-title">Teacher Enrollment Requests</h1>
            <p class="page-subtitle">Review and approve teacher enrollment requests</p>
          </div>
          <div class="stats-badge">
            <div class="stats-number">{{ pendingEnrollments.length }}</div>
            <div class="stats-label">Pending Requests</div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>

      <!-- Empty State -->
      <div v-else-if="pendingEnrollments.length === 0" class="empty-state-card">
        <div class="empty-icon-wrapper">
          <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <h3 class="empty-title">All Caught Up!</h3>
        <p class="empty-description">No pending teacher enrollment requests at the moment.</p>
      </div>

      <!-- Enrollment List -->
      <div v-else class="enrollment-list">
        <div
          v-for="enrollment in pendingEnrollments"
          :key="enrollment._id"
          class="enrollment-card"
        >
          <div class="card-content">
            <!-- User Info Section -->
            <div class="user-section">
              <div class="avatar-wrapper">
                <div class="user-avatar">
                  {{ getInitials(enrollment.user_name) }}
                </div>
              </div>

              <div class="user-details">
                <div class="user-header">
                  <h3 class="user-name">{{ enrollment.user_name }}</h3>
                  <span class="role-badge">Teacher</span>
                </div>
                <p class="user-email">{{ enrollment.user_email }}</p>
                
                <div class="info-grid">
                  <div class="info-item">
                    <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                    </svg>
                    <div>
                      <span class="info-label">Department</span>
                      <span class="info-value">{{ enrollment.department_name }}</span>
                    </div>
                  </div>
                  
                  <div class="info-item">
                    <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <div>
                      <span class="info-label">Requested</span>
                      <span class="info-value">{{ formatDate(enrollment.requested_at) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Action Buttons Section -->
            <div class="action-section">
              <button
                @click="reviewEnrollment(enrollment._id, 'approved')"
                :disabled="processingId === enrollment._id"
                class="btn-approve"
              >
                <svg v-if="processingId === enrollment._id" class="btn-spinner" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <svg v-else class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <span>Approve</span>
              </button>

              <button
                @click="reviewEnrollment(enrollment._id, 'declined')"
                :disabled="processingId === enrollment._id"
                class="btn-decline"
              >
                <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
                <span>Decline</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Success/Error Notifications -->
      <transition name="fade">
        <div v-if="notification.show" class="fixed bottom-4 right-4 z-50">
          <div
            :class="[
              'rounded-lg shadow-2xl p-4 max-w-sm',
              notification.type === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
            ]"
          >
            <div class="flex items-center">
              <div :class="[
                'flex-shrink-0',
                notification.type === 'success' ? 'text-green-400' : 'text-red-400'
              ]">
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path v-if="notification.type === 'success'" fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  <path v-else fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <p :class="[
                  'text-sm font-medium',
                  notification.type === 'success' ? 'text-green-800' : 'text-red-800'
                ]">
                  {{ notification.message }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const pendingEnrollments = ref([]);
const loading = ref(true);
const processingId = ref(null);
const notification = ref({
  show: false,
  message: '',
  type: 'success'
});

const fetchPendingEnrollments = async () => {
  try {
    loading.value = true;
    const token = localStorage.getItem('token');
    const response = await axios.get('http://localhost:8001/enrollments/pending', {
      headers: { Authorization: `Bearer ${token}` }
    });
    pendingEnrollments.value = response.data;
  } catch (error) {
    console.error('Error fetching pending enrollments:', error);
    showNotification('Failed to load enrollment requests', 'error');
  } finally {
    loading.value = false;
  }
};

const reviewEnrollment = async (enrollmentId, action) => {
  try {
    processingId.value = enrollmentId;
    const token = localStorage.getItem('token');
    await axios.post(
      `http://localhost:8001/enrollments/review/${enrollmentId}`,
      { action },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    
    showNotification(
      `Teacher enrollment ${action === 'approved' ? 'approved' : 'declined'} successfully`,
      'success'
    );
    
    // Refresh the list
    await fetchPendingEnrollments();
  } catch (error) {
    console.error('Error reviewing enrollment:', error);
    showNotification(
      error.response?.data?.detail || 'Failed to process enrollment',
      'error'
    );
  } finally {
    processingId.value = null;
  }
};

const getInitials = (name) => {
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const showNotification = (message, type) => {
  notification.value = { show: true, message, type };
  setTimeout(() => {
    notification.value.show = false;
  }, 3000);
};

onMounted(() => {
  fetchPendingEnrollments();
});
</script>

<style scoped>
/* Main Container */
.min-h-screen {
  min-height: 100vh;
}

.bg-gradient-to-br {
  background: linear-gradient(to bottom right, #EEF2FF, #FFFFFF, #FAF5FF);
}

.from-indigo-50 {
  --tw-gradient-from: #EEF2FF;
}

.via-white {
  --tw-gradient-via: #FFFFFF;
}

.to-purple-50 {
  --tw-gradient-to: #FAF5FF;
}

.p-6 {
  padding: 1.5rem;
}

.max-w-6xl {
  max-width: 72rem;
}

.mx-auto {
  margin-left: auto;
  margin-right: auto;
}

/* Header Section */
.header-section {
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
  background: linear-gradient(to right, #4F46E5, #7C3AED);
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
  border: 2px solid #E0E7FF;
  text-align: center;
  min-width: 150px;
}

.stats-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: #4F46E5;
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

/* Loading State */
.flex {
  display: flex;
}

.justify-center {
  justify-content: center;
}

.items-center {
  align-items: center;
}

.py-12 {
  padding-top: 3rem;
  padding-bottom: 3rem;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.rounded-full {
  border-radius: 9999px;
}

.h-12 {
  height: 3rem;
}

.w-12 {
  width: 3rem;
}

.border-b-2 {
  border-bottom-width: 2px;
}

.border-indigo-600 {
  border-color: #4F46E5;
}

/* Empty State */
.empty-state-card {
  background: white;
  border-radius: 1.5rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  padding: 4rem 2rem;
  text-align: center;
}

.empty-icon-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.empty-icon {
  width: 5rem;
  height: 5rem;
  color: #D1D5DB;
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.5rem 0;
}

.empty-description {
  color: #6B7280;
  font-size: 1rem;
  margin: 0;
}

/* Enrollment List */
.enrollment-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.enrollment-card {
  background: white;
  border-radius: 1.25rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #F3F4F6;
  transition: all 0.3s ease;
  overflow: hidden;
}

.enrollment-card:hover {
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.card-content {
  padding: 2rem;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 2rem;
  align-items: center;
}

/* User Section */
.user-section {
  display: flex;
  gap: 1.5rem;
  align-items: start;
  flex: 1;
}

.avatar-wrapper {
  flex-shrink: 0;
}

.user-avatar {
  width: 4.5rem;
  height: 4.5rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #A855F7, #4F46E5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 1.5rem;
  box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.user-name {
  font-size: 1.375rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.role-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  background: #F3E8FF;
  color: #7C3AED;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.user-email {
  font-size: 0.938rem;
  color: #6B7280;
  margin: 0 0 1rem 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.info-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: #6366F1;
  flex-shrink: 0;
}

.info-item > div {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.info-label {
  font-size: 0.75rem;
  color: #9CA3AF;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  font-size: 0.938rem;
  color: #1F2937;
  font-weight: 600;
}

/* Action Section */
.action-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 140px;
}

.btn-approve,
.btn-decline {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border: none;
  border-radius: 0.75rem;
  font-size: 0.938rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  white-space: nowrap;
}

.btn-approve {
  background: linear-gradient(135deg, #10B981, #059669);
  color: white;
}

.btn-approve:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669, #047857);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
  transform: translateY(-1px);
}

.btn-decline {
  background: linear-gradient(135deg, #EF4444, #DC2626);
  color: white;
}

.btn-decline:hover:not(:disabled) {
  background: linear-gradient(135deg, #DC2626, #B91C1C);
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
  transform: translateY(-1px);
}

.btn-approve:disabled,
.btn-decline:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-icon,
.btn-spinner {
  width: 1.25rem;
  height: 1.25rem;
}

.btn-spinner {
  animation: spin 1s linear infinite;
}

/* Notification */
.fixed {
  position: fixed;
}

.bottom-4 {
  bottom: 1rem;
}

.right-4 {
  right: 1rem;
}

.z-50 {
  z-index: 50;
}

.rounded-lg {
  border-radius: 0.75rem;
}

.shadow-2xl {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.p-4 {
  padding: 1rem;
}

.max-w-sm {
  max-width: 24rem;
}

.bg-green-50 {
  background-color: #F0FDF4;
}

.border {
  border-width: 1px;
}

.border-green-200 {
  border-color: #BBF7D0;
}

.bg-red-50 {
  background-color: #FEF2F2;
}

.border-red-200 {
  border-color: #FECACA;
}

.flex-shrink-0 {
  flex-shrink: 0;
}

.text-green-400 {
  color: #4ADE80;
}

.text-red-400 {
  color: #F87171;
}

.h-5 {
  height: 1.25rem;
}

.w-5 {
  width: 1.25rem;
}

.ml-3 {
  margin-left: 0.75rem;
}

.text-sm {
  font-size: 0.875rem;
}

.font-medium {
  font-weight: 500;
}

.text-green-800 {
  color: #166534;
}

.text-red-800 {
  color: #991B1B;
}

/* Transitions */
.fade-enter-active, 
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, 
.fade-leave-to {
  opacity: 0;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .card-content {
    grid-template-columns: 1fr;
  }

  .action-section {
    flex-direction: row;
    width: 100%;
  }

  .btn-approve,
  .btn-decline {
    flex: 1;
  }
}

@media (max-width: 640px) {
  .page-title {
    font-size: 2rem;
  }

  .stats-badge {
    width: 100%;
  }

  .user-section {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .action-section {
    flex-direction: column;
  }
}
</style>
