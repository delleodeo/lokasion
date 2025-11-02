<template>
  <div class="events-page">
    <div class="page-header">
      <h2>Available Events</h2>
      <p v-if="events.length === 0" class="empty-state">
        {{ userRole === 'teacher' ? 'No events available. Make sure you are enrolled in a society to see events.' : 'No events available at this time.' }}
      </p>
    </div>

    <div class="event-list">
      <EventCard 
        v-for="event in events" 
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
      userRole: ''
    };
  },
  created() {
    const token = localStorage.getItem('token');
    if (token) {
      const decodedToken = jwtDecode(token);
      this.userRole = decodedToken.role;
    }
  },
  async mounted() {
    await this.fetchEvents();
  },
  async created() {
    await this.fetchEvents();
  },
  methods: {
    async fetchEvents() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/events/`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.events = response.data;
      } catch (error) {
        console.error('Failed to fetch events:', error);
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
