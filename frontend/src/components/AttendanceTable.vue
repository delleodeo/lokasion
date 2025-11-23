<template>
  <div class="table-wrapper">
    <table class="attendance-table" v-if="attendanceData.length > 0">
      <thead>
        <tr>
          <th>Event Name</th>
          <th>Society</th>
          <th>Check-In Time</th>
          <th>Check-Out Time</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="record in attendanceData" :key="record._id">
          <td data-label="Event Name">
            <span class="event-name">{{ record.event_name || 'Unknown Event' }}</span>
          </td>
          <td data-label="Society">
            <span class="society-name">{{ record.department_name || 'Unknown Society' }}</span>
          </td>
          <td data-label="Check-In Time">
            <span class="timestamp">{{ formatDateTime(record.check_in_time || record.timestamp) }}</span>
          </td>
          <td data-label="Check-Out Time">
            <span v-if="record.check_out_time" class="timestamp">{{ formatDateTime(record.check_out_time) }}</span>
            <span v-else class="not-checked-out">Not checked out</span>
          </td>
          <td data-label="Status">
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

.event-name {
  font-weight: 600;
  color: var(--dark-green);
  font-size: 0.95rem;
}

.society-name {
  font-weight: 500;
  color: var(--medium-green);
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.timestamp {
  color: var(--gray-600);
}

.not-checked-out {
  color: var(--gray-500);
  font-style: italic;
  font-size: 0.9rem;
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
