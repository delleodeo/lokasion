<template>
  <div class="teacher-events-wrapper">
    <div class="container">
      <!-- Header -->
      <div class="header-section">
        <div class="header-content">
          <div class="title-group">
            <h1 class="page-title">My Events</h1>
            <p class="page-subtitle">Manage your events and track attendance</p>
          </div>
          <div class="stats-badges">
            <div class="stats-badge">
              <div class="stats-number">{{ filteredEvents.length }}</div>
              <div class="stats-label">{{ selectedDepartmentId ? 'Society Events' : 'Total Events' }}</div>
            </div>
            <div class="stats-badge">
              <div class="stats-number">{{ totalAttendees }}</div>
              <div class="stats-label">Total Check-ins</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Society Filter -->
      <div v-if="teacherDepartments.length > 1" class="filter-section">
        <label for="eventDepartmentFilter" class="filter-label">
          <svg class="filter-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
          </svg>
          Filter by Society
        </label>
        <select 
          id="eventDepartmentFilter" 
          v-model="selectedDepartmentId" 
          class="department-filter"
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

      <!-- Loading State -->
      <div v-if="loading" class="loading-container">
        <div class="spinner"></div>
        <p class="loading-text">Loading your events...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredEvents.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <h3 class="empty-title">No Events Yet</h3>
        <p class="empty-description">
          Make sure you are enrolled and approved in a society to create and view events. 
          Visit the Societies page to enroll.
        </p>
      </div>

      <!-- Events Grid -->
      <div v-else class="events-grid">
        <div
          v-for="event in filteredEvents"
          :key="event._id"
          class="event-card"
        >
          <!-- Event Header -->
          <div class="event-header">
            <div class="event-icon-wrapper">
              <svg class="event-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="event-title-group">
              <h3 class="event-title">{{ event.name }}</h3>
              <div class="event-badge">
                <svg class="badge-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                <span>{{ event.attendanceCount || 0 }} attendees</span>
              </div>
            </div>
          </div>

          <!-- Event Details -->
          <div class="event-details">
            <div class="detail-item">
              <svg class="detail-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="detail-content">
                <span class="detail-label">Start Time</span>
                <span class="detail-value">{{ formatDateTime(event.start_time) }}</span>
              </div>
            </div>

            <div class="detail-item" v-if="event.location_name">
              <svg class="detail-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <div class="detail-content">
                <span class="detail-label">Venue</span>
                <span class="detail-value location-name">{{ event.location_name }}</span>
              </div>
            </div>

            <div class="detail-item">
              <svg class="detail-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <div class="detail-content">
                <span class="detail-label">GPS Coordinates</span>
                <span class="detail-value">{{ event.latitude.toFixed(4) }}, {{ event.longitude.toFixed(4) }}</span>
              </div>
            </div>

            <div class="detail-item">
              <svg class="detail-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
              <div class="detail-content">
                <span class="detail-label">Check-in Radius</span>
                <span class="detail-value">{{ event.radius }} meters</span>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="action-buttons">
            <button
              @click="viewAttendance(event)"
              class="btn btn-view"
            >
              <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <span>View Attendance</span>
            </button>

            <button
              @click="editEvent(event)"
              class="btn btn-edit"
            >
              <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <span>Edit</span>
            </button>

            <button
              @click="deleteEvent(event)"
              class="btn btn-delete"
            >
              <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              <span>Delete</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Attendance Modal -->
      <transition name="modal">
        <div v-if="showAttendanceModal" class="modal-overlay" @click.self="closeAttendanceModal">
          <div class="modal-container">
            <div class="modal-header">
              <div>
                <h2 class="modal-title">Attendance Details</h2>
                <p class="modal-subtitle">{{ selectedEvent?.name }}</p>
              </div>
              <button @click="closeAttendanceModal" class="btn-close">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div class="modal-body">
              <!-- Attendance Stats -->
              <div class="attendance-stats">
                <div class="stat-card stat-total">
                  <div class="stat-icon">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                  <div class="stat-content">
                    <div class="stat-number">{{ attendanceData.length }}</div>
                    <div class="stat-label">Total Check-ins</div>
                  </div>
                </div>

                <div class="stat-card stat-present">
                  <div class="stat-icon">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div class="stat-content">
                    <div class="stat-number">{{ presentCount }}</div>
                    <div class="stat-label">Present</div>
                  </div>
                </div>

                <div class="stat-card stat-absent">
                  <div class="stat-icon">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div class="stat-content">
                    <div class="stat-number">{{ absentCount }}</div>
                    <div class="stat-label">Absent</div>
                  </div>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="export-section">
                <button @click="finalizeAttendance" class="btn btn-finalize">
                  <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Finalize Attendance</span>
                </button>
                <button @click="exportToExcel" class="btn btn-export">
                  <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span>Export to Excel</span>
                </button>
              </div>

              <!-- Attendance Table -->
              <div v-if="loadingAttendance" class="loading-container">
                <div class="spinner"></div>
                <p class="loading-text">Loading attendance data...</p>
              </div>

              <div v-else-if="attendanceData.length === 0" class="empty-attendance">
                <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
                <p class="empty-text">No check-ins yet for this event</p>
              </div>

              <div v-else class="attendance-table-wrapper">
                <table class="attendance-table">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>ID Number</th>
                      <th>Student Name</th>
                      <th>Email</th>
                      <th>Check-In Time</th>
                      <th>Check-Out Time</th>
                      <th>Duration</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(record, index) in attendanceData" :key="record._id">
                      <td>{{ index + 1 }}</td>
                      <td class="student-id">{{ record.student_id_number || 'N/A' }}</td>
                      <td class="student-name">{{ record.student_name }}</td>
                      <td class="student-email">{{ record.student_email }}</td>
                      <td>{{ formatDateTime(record.check_in_time || record.timestamp) }}</td>
                      <td>
                        <span v-if="record.check_out_time">{{ formatDateTime(record.check_out_time) }}</span>
                        <span v-else class="text-muted">Not checked out</span>
                      </td>
                      <td>
                        <span v-if="record.check_in_time && record.check_out_time">{{ calculateDuration(record.check_in_time, record.check_out_time) }}</span>
                        <span v-else class="text-muted">—</span>
                      </td>
                      <td>
                        <span :class="['status-badge', record.status === 'Present' ? 'status-present' : 'status-absent']">
                          {{ record.status }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </transition>

      <!-- Success/Error Notifications -->
      <transition name="notification">
        <div v-if="notification.show" class="notification-container">
          <div :class="['notification', notification.type]">
            <div class="notification-icon">
              <svg v-if="notification.type === 'success'" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              <svg v-else fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <p class="notification-message">{{ notification.message }}</p>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { API_BASE_URL } from '../config.js';

const events = ref([]);
const teacherDepartments = ref([]);
const selectedDepartmentId = ref('');
const loading = ref(true);
const showAttendanceModal = ref(false);
const selectedEvent = ref(null);
const attendanceData = ref([]);
const loadingAttendance = ref(false);
const notification = ref({
  show: false,
  message: '',
  type: 'success'
});

const filteredEvents = computed(() => {
  if (!selectedDepartmentId.value) {
    return events.value;
  }
  return events.value.filter(event => event.department_id === selectedDepartmentId.value);
});

const totalAttendees = computed(() => {
  return filteredEvents.value.reduce((sum, event) => sum + (event.attendanceCount || 0), 0);
});

const presentCount = computed(() => {
  return attendanceData.value.filter(record => record.status === 'Present').length;
});

const absentCount = computed(() => {
  return attendanceData.value.filter(record => record.status === 'Absent').length;
});

const fetchEvents = async () => {
  try {
    loading.value = true;
    const token = localStorage.getItem('token');
    const response = await axios.get(`${API_BASE_URL}/events/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    // Fetch attendance count for each event
    events.value = await Promise.all(
      response.data.map(async (event) => {
        try {
          const attendanceRes = await axios.get(`${API_BASE_URL}/attendance/event/${event._id}`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          return {
            ...event,
            attendanceCount: attendanceRes.data.total_checkins
          };
        } catch (error) {
          return { ...event, attendanceCount: 0 };
        }
      })
    );
  } catch (error) {
    console.error('Error fetching events:', error);
    showNotification('Failed to load events', 'error');
  } finally {
    loading.value = false;
  }
};

const viewAttendance = async (event) => {
  selectedEvent.value = event;
  showAttendanceModal.value = true;
  loadingAttendance.value = true;
  
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${API_BASE_URL}/attendance/event/${event._id}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    attendanceData.value = response.data.attendance;
  } catch (error) {
    console.error('Error fetching attendance:', error);
    showNotification('Failed to load attendance data', 'error');
  } finally {
    loadingAttendance.value = false;
  }
};

const closeAttendanceModal = () => {
  showAttendanceModal.value = false;
  selectedEvent.value = null;
  attendanceData.value = [];
};

const finalizeAttendance = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.post(
      `${API_BASE_URL}/attendance/event/${selectedEvent.value._id}/finalize`,
      {},
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    
    showNotification(`Attendance finalized: ${response.data.absent_count} students marked absent`, 'success');
    
    // Refresh attendance data
    await viewAttendance(selectedEvent.value);
  } catch (error) {
    console.error('Error finalizing attendance:', error);
    showNotification(error.response?.data?.detail || 'Failed to finalize attendance', 'error');
  }
};

const exportToExcel = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(
      `${API_BASE_URL}/attendance/event/${selectedEvent.value._id}/export`,
      {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      }
    );
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${selectedEvent.value.name}_attendance.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    showNotification('Attendance exported successfully!', 'success');
  } catch (error) {
    console.error('Error exporting attendance:', error);
    showNotification('Failed to export attendance', 'error');
  }
};

const editEvent = (event) => {
  router.push(`/edit-event/${event._id}`);
};

const deleteEvent = async (event) => {
  if (!confirm(`Are you sure you want to delete "${event.name}"?`)) return;
  
  try {
    const token = localStorage.getItem('token');
    await axios.delete(`${API_BASE_URL}/events/${event._id}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    showNotification('Event deleted successfully', 'success');
    await fetchEvents();
  } catch (error) {
    console.error('Error deleting event:', error);
    showNotification('Failed to delete event', 'error');
  }
};

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  // NO TIMEZONE CONVERSION - Display in user's local time
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  });
};

const calculateDuration = (checkInTime, checkOutTime) => {
  if (!checkInTime || !checkOutTime) return '—';
  
  const checkIn = new Date(checkInTime);
  const checkOut = new Date(checkOutTime);
  const diffMs = checkOut - checkIn;
  
  if (diffMs < 0) return 'Invalid';
  
  const hours = Math.floor(diffMs / (1000 * 60 * 60));
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  } else {
    return `${minutes}m`;
  }
};

const showNotification = (message, type) => {
  notification.value = { show: true, message, type };
  setTimeout(() => {
    notification.value.show = false;
  }, 3000);
};

const fetchTeacherDepartments = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${API_BASE_URL}/enrollments/teacher/departments`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    teacherDepartments.value = response.data;
  } catch (error) {
    console.error('Error fetching teacher departments:', error);
  }
};

onMounted(() => {
  fetchEvents();
  fetchTeacherDepartments();
});
</script>

<style scoped>
/* Main Wrapper */
.teacher-events-wrapper {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.header-section {
  margin-bottom: 2.5rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  flex-wrap: wrap;
}

.title-group {
  flex: 1;
  min-width: 300px;
}

.page-title {
  font-size: 3rem;
  font-weight: 800;
  color: white;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.page-subtitle {
  font-size: 1.125rem;
  color: rgba(255, 255, 255, 0.9);
}

.stats-badges {
  display: flex;
  gap: 1rem;
}

.stats-badge {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 1.25rem 1.75rem;
  text-align: center;
  min-width: 140px;
}

.stats-number {
  font-size: 2.25rem;
  font-weight: 800;
  color: white;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stats-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

/* Filter Section */
.filter-section {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.filter-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #1F2937;
  white-space: nowrap;
}

.filter-icon {
  width: 20px;
  height: 20px;
  color: #667eea;
}

.department-filter {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.department-filter:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 1rem;
  color: white;
  font-size: 1rem;
}

/* Empty State */
.empty-state {
  background: white;
  border-radius: 20px;
  padding: 4rem 2rem;
  text-align: center;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.5rem;
  color: #9CA3AF;
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 0.5rem;
}

.empty-description {
  font-size: 1rem;
  color: #6B7280;
}

/* Events Grid */
.events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.event-card {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
}

.event-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

/* Event Header */
.event-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  align-items: flex-start;
}

.event-icon-wrapper {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 14px rgba(102, 126, 234, 0.4);
}

.event-icon {
  width: 28px;
  height: 28px;
  color: white;
}

.event-title-group {
  flex: 1;
}

.event-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 0.5rem;
  line-height: 1.3;
}

.event-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #F0F4FF 0%, #E8ECFF 100%);
  padding: 0.375rem 0.875rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  color: #667eea;
}

.badge-icon {
  width: 16px;
  height: 16px;
}

/* Event Details */
.event-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.detail-item {
  display: flex;
  gap: 0.875rem;
  align-items: flex-start;
}

.detail-icon {
  width: 20px;
  height: 20px;
  color: #9CA3AF;
  flex-shrink: 0;
  margin-top: 2px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.detail-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #9CA3AF;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  font-size: 0.9375rem;
  font-weight: 500;
  color: #374151;
}

.location-name {
  color: #2E7D32;
  font-weight: 700;
  font-size: 1rem;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 2px solid #F3F4F6;
}

.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  flex: 1;
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.btn-view {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-view:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.btn-edit {
  background: linear-gradient(135deg, #F59E0B 0%, #F97316 100%);
  color: white;
}

.btn-edit:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(245, 158, 11, 0.4);
}

.btn-delete {
  background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
  color: white;
}

.btn-delete:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(239, 68, 68, 0.4);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  z-index: 1000;
}

.modal-container {
  background: white;
  border-radius: 24px;
  max-width: 1000px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 2rem;
  border-bottom: 2px solid #F3F4F6;
}

.modal-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #1F2937;
  margin-bottom: 0.25rem;
}

.modal-subtitle {
  font-size: 1rem;
  color: #6B7280;
}

.btn-close {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #F3F4F6;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-close:hover {
  background: #E5E7EB;
  transform: rotate(90deg);
}

.btn-close svg {
  width: 20px;
  height: 20px;
  color: #6B7280;
}

.modal-body {
  padding: 2rem;
  overflow-y: auto;
}

/* Attendance Stats */
.attendance-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 16px;
  border: 2px solid;
}

.stat-total {
  background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
  border-color: #667eea;
}

.stat-present {
  background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
  border-color: #10B981;
}

.stat-absent {
  background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
  border-color: #EF4444;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-total .stat-icon {
  background: #667eea;
  color: white;
}

.stat-present .stat-icon {
  background: #10B981;
  color: white;
}

.stat-absent .stat-icon {
  background: #EF4444;
  color: white;
}

.stat-icon svg {
  width: 24px;
  height: 24px;
}

.stat-content {
  flex: 1;
}

.stat-card .stat-number {
  font-size: 2rem;
  font-weight: 800;
  color: #1F2937;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stat-card .stat-label {
  font-size: 0.875rem;
  color: #6B7280;
  font-weight: 600;
}

/* Export Section */
.export-section {
  margin-bottom: 2rem;
  display: flex;
  gap: 1rem;
}

.btn-finalize {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  color: white;
  flex: 1;
}

.btn-finalize:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
}

.btn-export {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: white;
  flex: 1;
}

.btn-export:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4);
}

/* Attendance Table */
.empty-attendance {
  text-align: center;
  padding: 3rem 1rem;
}

.empty-attendance .empty-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem;
  color: #D1D5DB;
}

.empty-text {
  font-size: 1rem;
  color: #9CA3AF;
}

.attendance-table-wrapper {
  overflow-x: auto;
  border-radius: 12px;
  border: 2px solid #F3F4F6;
}

.attendance-table {
  width: 100%;
  border-collapse: collapse;
}

.attendance-table thead {
  background: linear-gradient(135deg, #F9FAFB 0%, #F3F4F6 100%);
}

.attendance-table th {
  padding: 1rem;
  text-align: left;
  font-size: 0.875rem;
  font-weight: 700;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #E5E7EB;
}

.attendance-table td {
  padding: 1rem;
  font-size: 0.9375rem;
  color: #6B7280;
  border-bottom: 1px solid #F3F4F6;
}

.attendance-table tbody tr:hover {
  background: #F9FAFB;
}

.student-name {
  font-weight: 600;
  color: #1F2937;
}

.student-email {
  color: #9CA3AF;
}

.text-muted {
  color: #9CA3AF;
  font-style: italic;
  font-size: 0.875rem;
}

.status-badge {
  display: inline-block;
  padding: 0.375rem 0.875rem;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
}

.status-present {
  background: #D1FAE5;
  color: #065F46;
}

.status-absent {
  background: #FEE2E2;
  color: #991B1B;
}

/* Notifications */
.notification-container {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 2000;
}

.notification {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  min-width: 320px;
  border: 2px solid;
}

.notification.success {
  background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
  border-color: #10B981;
  color: #065F46;
}

.notification.error {
  background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
  border-color: #EF4444;
  color: #991B1B;
}

.notification-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.notification-message {
  font-size: 0.9375rem;
  font-weight: 600;
}

/* Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9);
}

.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.notification-enter-from,
.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

/* Responsive */
@media (max-width: 768px) {
  .teacher-events-wrapper {
    padding: 1rem;
  }

  .page-title {
    font-size: 2rem;
  }

  .stats-badges {
    width: 100%;
    justify-content: center;
  }

  .events-grid {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-direction: column;
  }

  .attendance-stats {
    grid-template-columns: 1fr;
  }

  .modal-container {
    margin: 1rem;
  }

  .modal-header,
  .modal-body {
    padding: 1.5rem;
  }

  .notification-container {
    left: 1rem;
    right: 1rem;
  }

  .notification {
    min-width: auto;
  }
}
</style>
