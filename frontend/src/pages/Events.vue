<template>
  <div class="events-page">
    <div class="page-header">
      <h2>Available Events</h2>
      <p v-if="filteredEvents.length === 0 && !loading" class="empty-state">
        {{ userRole === 'teacher' ? 'No events available. Make sure you are enrolled in a society to see events.' : 'No events available at this time.' }}
      </p>
    </div>

    <!-- Society Filter for Students -->
    <div v-if="userRole === 'student' && studentSocieties.length > 0" class="filter-section">
      <label for="societyFilter" class="filter-label">
        <svg class="filter-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
        </svg>
        Filter by Society
      </label>
      <select 
        id="societyFilter" 
        v-model="selectedSocietyId" 
        class="society-filter"
      >
        <option value="">All Societies</option>
        <option 
          v-for="society in studentSocieties" 
          :key="society.department_id" 
          :value="society.department_id"
        >
          {{ society.department_name }}
        </option>
      </select>
    </div>

    <div v-if="loading" class="loading-state">
      <p>Loading events...</p>
    </div>

    <div v-else class="event-list">
      <EventCard 
        v-for="event in filteredEvents" 
        :key="event._id" 
        :event="event" 
        @checkin="handleCheckIn"
      />
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../config.js';
import EventCard from '../components/EventCard.vue';
import { jwtDecode } from 'jwt-decode';

export default {
  name: 'Events',
  components: {
    EventCard
  },
  data() {
    return {
      events: [],
      studentSocieties: [],
      selectedSocietyId: '',
      userRole: '',
      loading: true
    };
  },
  computed: {
    filteredEvents() {
      if (!this.selectedSocietyId || this.userRole !== 'student') {
        return this.events;
      }
      return this.events.filter(event => event.department_id === this.selectedSocietyId);
    }
  },
  async created() {
    const token = localStorage.getItem('token');
    if (token) {
      const decodedToken = jwtDecode(token);
      this.userRole = decodedToken.role;
    }
    await this.fetchEvents();
    if (this.userRole === 'student') {
      await this.fetchStudentSocieties();
    }
  },
  methods: {
    async fetchEvents() {
      try {
        this.loading = true;
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/events/`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.events = response.data;
        console.log('Fetched events:', this.events);
      } catch (error) {
        console.error('Failed to fetch events:', error);
      } finally {
        this.loading = false;
      }
    },
    async fetchStudentSocieties() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/enrollments/my-enrollments`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        // Get approved enrollments
        const approvedEnrollments = response.data.filter(e => e.status === 'approved');
        
        // Fetch department details for each enrollment
        this.studentSocieties = await Promise.all(
          approvedEnrollments.map(async (enrollment) => {
            try {
              const deptResponse = await axios.get(`${API_BASE_URL}/enrollments/societies`, {
                headers: { Authorization: `Bearer ${token}` }
              });
              const dept = deptResponse.data.find(d => d._id === enrollment.department_id);
              return {
                department_id: enrollment.department_id,
                department_name: dept ? dept.name : 'Unknown'
              };
            } catch (error) {
              return {
                department_id: enrollment.department_id,
                department_name: 'Unknown'
              };
            }
          })
        );
      } catch (error) {
        console.error('Failed to fetch student societies:', error);
      }
    },
    handleCheckIn() {
      // Optionally refresh events after check-in
      this.fetchEvents();
    }
  }
}
</script>

<style scoped>
.events-page {
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

.empty-state {
  color: var(--gray-600);
  font-size: 1rem;
  margin-top: 1rem;
}

.filter-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
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
  color: #10b981;
}

.society-filter {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.society-filter:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.loading-state {
  text-align: center;
  padding: 3rem;
  color: var(--gray-600);
}

.event-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .event-list {
    grid-template-columns: 1fr;
  }
}
</style>
