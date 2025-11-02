<template>
  <div class="table-wrapper">
    <table class="attendance-table" v-if="attendanceData.length > 0">
      <thead>
        <tr>
          <th>Event ID</th>
          <th>Check-In Time</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="record in attendanceData" :key="record._id">
          <td>
            <span class="event-id">{{ record.event_id }}</span>
          </td>
          <td>
            <span class="timestamp">{{ formatDateTime(record.timestamp) }}</span>
          </td>
          <td>
            <span :class="['status-badge', statusClass(record.status)]">
              <CheckCircleIcon v-if="record.status === 'Present'" class="status-icon" />
              <XCircleIcon v-else class="status-icon" />
              {{ record.status }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-else class="no-data">
      No attendance records found.
    </div>
  </div>
</template>

<script>
import { CheckCircleIcon, XCircleIcon } from '@heroicons/vue/24/solid';

export default {
  name: 'AttendanceTable',
  components: {
    CheckCircleIcon,
    XCircleIcon
  },
  props: ['attendanceData'],
  methods: {
    formatDateTime(dateString) {
      return new Date(dateString).toLocaleString();
    },
    statusClass(status) {
      return {
        'status-present': status === 'Present',
        'status-out-of-range': status === 'Out of Range'
      };
    }
  }
}
</script>

<style scoped>
.table-wrapper {
  width: 100%;
  overflow-x: auto;
}

.attendance-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

th, td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--gray-200);
}

th {
  background-color: var(--gray-50);
  color: var(--dark-green);
  font-weight: 600;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

tbody tr:hover {
  background-color: var(--gray-50);
}

.event-id {
  font-family: monospace;
  background: var(--gray-100);
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
}

.timestamp {
  color: var(--gray-600);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
}

.status-present {
  background-color: #D1E7DD;
  color: #0F5132;
}

.status-out-of-range {
  background-color: #F8D7DA;
  color: #842029;
}

.status-icon {
  width: 18px;
  height: 18px;
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: var(--gray-600);
}
</style>
