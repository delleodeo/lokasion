<template>
  <div class="attendance-page">
    <div class="page-header">
      <h2>Attendance History</h2>
      <p v-if="attendanceHistory.length === 0" class="empty-state">No attendance records yet.</p>
    </div>

    <div class="attendance-container">
      <AttendanceTable :attendanceData="attendanceHistory" />
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../config.js';
import AttendanceTable from '../components/AttendanceTable.vue';
import { jwtDecode } from 'jwt-decode';

export default {
  name: 'Attendance',
  components: {
    AttendanceTable
  },
  data() {
    return {
      attendanceHistory: []
    };
  },
  async created() {
    try {
      const token = localStorage.getItem('token');
      const decodedToken = jwtDecode(token);
      const response = await axios.get(`${API_BASE_URL}/attendance/history/${decodedToken.user_id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      this.attendanceHistory = response.data;
    } catch (error) {
      console.error('Failed to fetch attendance history:', error);
    }
  }
}
</script>

<style scoped>
.attendance-page {
  max-width: 1200px;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h2 {
  color: var(--dark-green);
  margin-bottom: 0.5rem;
  font-size: 2rem;
}

.empty-state {
  color: var(--gray-600);
  font-size: 1rem;
  margin-top: 1rem;
}

.attendance-container {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
</style>
