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

      <!-- Filter by Society -->
      <div v-if="teacherDepartments.length > 1" class="controls-section" style="margin-bottom: 2rem;">
        <div class="control-group">
          <label for="pendingSocietyFilter" class="control-label">
            <svg class="label-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
            </svg>
            Filter by Society
          </label>
          <select 
            id="pendingSocietyFilter"
            v-model="selectedPendingDepartmentId" 
            @change="onPendingDepartmentChange"
            class="society-select"
          >
            <option value="">All Societies</option>
            <option 
              v-for="dept in teacherDepartments" 
              :key="dept.department_id" 
              :value="dept.department_id"
            >
              {{ dept.department_name }}
            </option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <p>Loading enrollment requests...</p>
      </div>

      <div v-else-if="filteredPendingEnrollments.length === 0" class="empty-state">
        <ClipboardDocumentCheckIcon class="empty-icon" />
        <h3>No Pending Requests</h3>
        <p>{{ selectedPendingDepartmentId ? 'No pending requests for this society' : 'All enrollment requests have been reviewed' }}</p>
      </div>

    <div v-else class="enrollments-list">
      <div v-for="enrollment in filteredPendingEnrollments" :key="enrollment._id" class="enrollment-card">
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
              <!-- Use the registration field `user_id_number` when provided, otherwise show N/A -->
                <span :class="['info-value', 'student-id', { 'not-set': !enrollment.user_id_number || enrollment.user_id_number === 'N/A' }]">
                  {{ enrollment.user_id_number && enrollment.user_id_number !== 'N/A' ? enrollment.user_id_number : 'N/A' }}
              </span>
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
          <p>Students currently enrolled in your department(s)</p>
        </div>
      </div>

      <!-- Society Selector and Controls -->
      <div class="controls-section">
        <div class="control-group">
          <label for="departmentSelect" class="control-label">
            <BuildingLibraryIcon class="label-icon" />
            Select Society
          </label>
          <select 
            id="departmentSelect" 
            v-model="selectedDepartmentId" 
            @change="onDepartmentChange"
            class="department-select"
          >
            <option value="">All Societies</option>
            <option 
              v-for="dept in teacherDepartments" 
              :key="dept.department_id" 
              :value="dept.department_id"
            >
              {{ dept.department_name }}
            </option>
          </select>
        </div>

        <div class="control-group">
          <label for="searchInput" class="control-label">
            <svg class="label-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Search Students
          </label>
          <input
            id="searchInput"
            v-model="searchQuery"
            type="text"
            placeholder="Search by name, ID, or email..."
            class="search-input"
          />
        </div>

        <button @click="exportToExcel" class="btn-export-students">
          <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Export to Excel
        </button>
      </div>

      <div v-if="loadingApproved" class="loading-state">
        <p>Loading enrolled students...</p>
      </div>

      <div v-else-if="filteredApprovedEnrollments.length === 0" class="empty-state">
        <UserCircleIcon class="empty-icon" />
        <h3>{{ searchQuery ? 'No Students Found' : 'No Enrolled Students' }}</h3>
        <p>{{ searchQuery ? 'Try adjusting your search criteria' : 'No students have been approved yet' }}</p>
      </div>

      <div v-else>
        <div class="results-count">
          Showing {{ filteredApprovedEnrollments.length }} of {{ approvedEnrollments.length }} students
        </div>
        <div class="enrollments-list">
          <div v-for="enrollment in filteredApprovedEnrollments" :key="enrollment.enrollment_id" class="enrollment-card approved-card">
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
                  <span class="info-label">Student ID Number</span>
                  <span class="info-value student-id-number">{{ enrollment.user_id_number || 'N/A' }}</span>
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
                  <span class="info-label">Email</span>
                  <span class="info-value">{{ enrollment.user_email }}</span>
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
      teacherDepartments: [],
      selectedDepartmentId: '',
      selectedPendingDepartmentId: '',
      searchQuery: '',
      loading: true,
      loadingApproved: false,
      reviewing: null,
      message: '',
      messageType: ''
    };
  },
  computed: {
    filteredPendingEnrollments() {
      if (!this.selectedPendingDepartmentId) {
        return this.pendingEnrollments;
      }
      return this.pendingEnrollments.filter(enrollment => 
        enrollment.department_id === this.selectedPendingDepartmentId
      );
    },
    filteredApprovedEnrollments() {
      console.log('Search Query:', this.searchQuery);
      console.log('Total Enrollments:', this.approvedEnrollments.length);
      
      if (!this.searchQuery) {
        return this.approvedEnrollments;
      }
      
      const query = this.searchQuery.toLowerCase().trim();
      const filtered = this.approvedEnrollments.filter(enrollment => {
        const userName = (enrollment.user_name || '').toLowerCase();
        const userEmail = (enrollment.user_email || '').toLowerCase();
        const userIdNumber = (enrollment.user_id_number || '').toLowerCase();
        const departmentName = (enrollment.department_name || '').toLowerCase();
        
        console.log('Checking:', userName, 'against', query);
        
        return userName.includes(query) ||
               userEmail.includes(query) ||
               userIdNumber.includes(query) ||
               departmentName.includes(query);
      });
      
      console.log('Filtered Results:', filtered.length);
      return filtered;
    }
  },
  watch: {
    activeTab(newTab) {
      if (newTab === 'approved') {
        if (this.teacherDepartments.length === 0) {
          this.fetchTeacherDepartments();
        }
        if (this.approvedEnrollments.length === 0) {
          this.fetchApprovedEnrollments();
        }
      }
    }
  },
  async created() {
    await this.fetchTeacherDepartments();
    await this.fetchPendingEnrollments();
  },
  methods: {
    async fetchTeacherDepartments() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/enrollments/teacher/departments`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.teacherDepartments = response.data;
      } catch (error) {
        console.error('Error fetching teacher departments:', error);
      }
    },
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
        const params = this.selectedDepartmentId ? { department_id: this.selectedDepartmentId } : {};
        const response = await axios.get(`${API_BASE_URL}/enrollments/approved`, {
          headers: { Authorization: `Bearer ${token}` },
          params: params
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
    async fetchTeacherDepartments() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/enrollments/teacher/departments`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.teacherDepartments = response.data;
      } catch (error) {
        console.error('Failed to fetch teacher departments:', error);
      }
    },
    onDepartmentChange() {
      this.searchQuery = '';
      this.fetchApprovedEnrollments();
    },
    onPendingDepartmentChange() {
      // Just filter the existing pending enrollments
      // No need to fetch again since we filter on frontend
    },
    async exportToExcel() {
      try {
        const token = localStorage.getItem('token');
        const params = this.selectedDepartmentId ? { department_id: this.selectedDepartmentId } : {};
        const response = await axios.get(`${API_BASE_URL}/enrollments/approved/export`, {
          headers: { Authorization: `Bearer ${token}` },
          params: params,
          responseType: 'blob'
        });
        
        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        const deptName = this.selectedDepartmentId ? 
          this.teacherDepartments.find(d => d.department_id === this.selectedDepartmentId)?.department_name || 'Society' :
          'All_Societies';
        link.setAttribute('download', `enrolled_students_${deptName.replace(/ /g, '_')}.xlsx`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        
        this.message = 'Students list exported successfully!';
        this.messageType = 'success';
        setTimeout(() => { this.message = ''; }, 3000);
      } catch (error) {
        console.error('Error exporting students:', error);
        this.message = 'Failed to export students list';
        this.messageType = 'error';
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

.controls-section {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.control-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--dark-green);
}

.label-icon {
  width: 18px;
  height: 18px;
  color: var(--medium-green);
}

.department-select,
.search-input {
  padding: 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  background: white;
}

.department-select:focus,
.search-input:focus {
  outline: none;
  border-color: var(--medium-green);
  box-shadow: 0 0 0 3px rgba(25, 135, 84, 0.1);
}

.department-select {
  cursor: pointer;
}

.btn-export-students {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  align-self: flex-end;
  white-space: nowrap;
}

.btn-export-students:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.results-count {
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-weight: 600;
  color: var(--dark-green);
  text-align: center;
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
  display: inline-block;
  min-width: 36px;
  text-align: center;
}

.student-id.not-set {
  /* N/A / not provided styling */
  background: transparent;
  color: var(--gray-600);
  border-color: var(--gray-200);
  font-style: italic;
  opacity: 0.9;
}

.student-id-number {
  font-family: 'Courier New', monospace;
  font-weight: 700;
  font-size: 1rem;
  color: var(--dark-green);
  background: linear-gradient(135deg, #D1FAE5, #A7F3D0);
  padding: 0.35rem 0.85rem;
  border-radius: 8px;
  border: 2px solid #10B981;
  display: inline-block;
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
