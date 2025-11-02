<template>
  <div class="event-card">
    <div class="event-header">
      <div class="event-icon">
        <CalendarDaysIcon />
      </div>
      <h3>{{ event.name }}</h3>
    </div>

    <div class="event-body">
      <div class="event-detail">
        <ClockIcon class="detail-icon" />
        <div>
          <p class="detail-label">Start Time</p>
          <p class="detail-value">{{ formatDateTime(event.start_time) }}</p>
        </div>
      </div>

      <div class="event-detail">
        <MapPinIcon class="detail-icon" />
        <div>
          <p class="detail-label">Location</p>
          <p class="detail-value">{{ event.latitude }}, {{ event.longitude }}</p>
        </div>
      </div>

      <div class="event-detail">
        <ArrowsPointingOutIcon class="detail-icon" />
        <div>
          <p class="detail-label">Radius</p>
          <p class="detail-value">{{ event.radius }} meters</p>
        </div>
      </div>
    </div>

    <button @click="checkIn" class="check-in-button">
      <CheckCircleIcon class="button-icon" />
      <span>Check In</span>
    </button>

    <div v-if="status" :class="['status-message', statusClass]">
      <CheckIcon v-if="status === 'Present'" class="status-icon" />
      <XMarkIcon v-else class="status-icon" />
      {{ statusMessage }}
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../config.js';
import { 
  CalendarDaysIcon, 
  ClockIcon, 
  MapPinIcon, 
  ArrowsPointingOutIcon, 
  CheckCircleIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/vue/24/solid';

export default {
  name: 'EventCard',
  components: {
    CalendarDaysIcon,
    ClockIcon,
    MapPinIcon,
    ArrowsPointingOutIcon,
    CheckCircleIcon,
    CheckIcon,
    XMarkIcon
  },
  props: ['event'],
  data() {
    return {
      status: null,
      statusMessage: '',
      isLoading: false
    };
  },
  computed: {
    statusClass() {
      return {
        'status-success': this.status === 'Present',
        'status-error': this.status === 'Out of Range',
        'status-loading': this.isLoading
      };
    }
  },
  methods: {
    formatDateTime(dateString) {
      return new Date(dateString).toLocaleString();
    },
    checkIn() {
      this.isLoading = true;
      this.statusMessage = 'Getting your location...';
      
      navigator.geolocation.getCurrentPosition(async position => {
        const { latitude, longitude, accuracy } = position.coords;
        
        console.log('📍 Student location:', { latitude, longitude, accuracy });
        console.log('📍 Event location:', { 
          latitude: this.event.latitude, 
          longitude: this.event.longitude,
          radius: this.event.radius 
        });
        
        try {
          const token = localStorage.getItem('token');
          const response = await axios.post(`${API_BASE_URL}/attendance/checkin`, {
            event_id: this.event._id,
            latitude,
            longitude
          }, {
            headers: { Authorization: `Bearer ${token}` }
          });
          
          this.status = response.data.status;
          
          if (response.data.status === 'Present') {
            this.statusMessage = '✓ Successfully checked in!';
          } else {
            this.statusMessage = `✗ Out of range (Accuracy: ±${Math.round(accuracy)}m)`;
          }
          
          this.$emit('checkin', this.status);
        } catch (error) {
          console.error('Check-in failed:', error);
          this.status = 'Error';
          this.statusMessage = error.response?.data?.detail || 'Check-in failed. Please try again.';
        } finally {
          this.isLoading = false;
        }
      }, error => {
        console.error('Geolocation error:', error);
        this.status = 'Error';
        
        if (error.code === 1) {
          this.statusMessage = 'Location access denied. Please enable location services.';
        } else if (error.code === 2) {
          this.statusMessage = 'Location unavailable. Please try again.';
        } else if (error.code === 3) {
          this.statusMessage = 'Location request timeout. Please try again.';
        } else {
          this.statusMessage = 'Unable to access your location.';
        }
        
        this.isLoading = false;
      }, {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      });
    }
  }
}
</script>

<style scoped>
.event-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--gray-200);
  transition: var(--transition);
}

.event-card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
}

.event-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.event-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #198754, #0F5132);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.event-icon svg {
  width: 28px;
  height: 28px;
}

.event-header h3 {
  margin: 0;
  color: var(--dark-green);
  font-size: 1.25rem;
}

.event-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.event-detail {
  display: flex;
  gap: 1rem;
}

.detail-icon {
  width: 20px;
  height: 20px;
  color: var(--medium-green);
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.detail-label {
  font-size: 0.85rem;
  color: var(--gray-600);
  margin: 0 0 0.25rem 0;
}

.detail-value {
  font-size: 0.95rem;
  color: var(--gray-800);
  margin: 0;
  font-weight: 500;
}

.check-in-button {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #198754, #0F5132);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  box-shadow: 0 4px 12px rgba(25, 135, 84, 0.3);
}

.check-in-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(25, 135, 84, 0.4);
}

.check-in-button:active {
  transform: translateY(0);
}

.button-icon {
  width: 22px;
  height: 22px;
}

.status-message {
  margin-top: 1rem;
  padding: 0.875rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
  font-size: 0.95rem;
  animation: slideIn 0.3s ease-out;
}

.status-success {
  background: #D1E7DD;
  color: #0F5132;
  border: 1px solid #198754;
}

.status-error {
  background: #F8D7DA;
  color: #842029;
  border: 1px solid #F5C2C7;
}

.status-icon {
  width: 20px;
  height: 20px;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .event-card {
    padding: 1rem;
  }

  .event-header {
    gap: 0.75rem;
  }

  .event-header h3 {
    font-size: 1.1rem;
  }
}
</style>
