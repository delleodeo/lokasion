<template>
  <div class="event-card">
    <div class="event-header">
      <div class="event-icon">
        <CalendarDaysIcon />
      </div>
      <div class="event-title-section">
        <h3>{{ event.name }}</h3>
        <p v-if="event.location_name" class="location-badge">
          <MapPinIcon class="location-badge-icon" />
          {{ event.location_name }}
        </p>
      </div>
    </div>

    <div class="event-body">
      <!-- Event Duration -->
      <div class="timing-section">
        <h4 class="section-title">📅 Event Schedule</h4>
        <div class="event-detail">
          <ClockIcon class="detail-icon" />
          <div>
            <p class="detail-label">Event Start</p>
            <p class="detail-value">{{ formatDateTime(event.start_time) }}</p>
          </div>
        </div>
        <div class="event-detail">
          <ClockIcon class="detail-icon" />
          <div>
            <p class="detail-label">Event End</p>
            <p class="detail-value">{{ formatDateTime(event.end_time) }}</p>
          </div>
        </div>
      </div>

      <!-- Check-In Window -->
      <div class="timing-section">
        <h4 class="section-title">📥 Check-In Period</h4>
        <div class="event-detail">
          <ClockIcon class="detail-icon" />
          <div>
            <p class="detail-label">Check-In Opens</p>
            <p class="detail-value">{{ formatDateTime(event.check_in_start || event.start_time) }}</p>
          </div>
        </div>
        <div class="event-detail">
          <ClockIcon class="detail-icon" />
          <div>
            <p class="detail-label">Check-In Closes</p>
            <p class="detail-value">{{ formatDateTime(event.check_in_end || event.end_time) }}</p>
          </div>
        </div>
      </div>

      <!-- Check-Out Window -->
      <div class="timing-section">
        <h4 class="section-title">📤 Check-Out Period</h4>
        <div class="event-detail">
          <ClockIcon class="detail-icon" />
          <div>
            <p class="detail-label">Check-Out Opens</p>
            <p class="detail-value">{{ formatDateTime(event.check_out_start || event.end_time) }}</p>
          </div>
        </div>
        <div class="event-detail" v-if="event.check_out_end">
          <ClockIcon class="detail-icon" />
          <div>
            <p class="detail-label">Check-Out Closes</p>
            <p class="detail-value">{{ formatDateTime(event.check_out_end) }}</p>
          </div>
        </div>
      </div>

      <!-- Location Info -->
      <div class="timing-section location-highlight">
        <h4 class="section-title">📍 Location Details</h4>
        <div class="event-detail">
          <MapPinIcon class="detail-icon" />
          <div>
            <p class="detail-label">GPS Coordinates</p>
            <p class="detail-value">{{ event.latitude.toFixed(4) }}, {{ event.longitude.toFixed(4) }}</p>
          </div>
        </div>
        <div class="event-detail">
          <ArrowsPointingOutIcon class="detail-icon" />
          <div>
            <p class="detail-label">Check-in Radius</p>
            <p class="detail-value">{{ event.radius }} meters</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Check-In Button (always visible) -->
    <div class="action-buttons">
      <button 
        @click="checkIn" 
        class="check-in-button" 
        :disabled="hasCheckedIn || !canCheckIn"
        :title="checkInButtonTitle"
      >
        <CheckCircleIcon class="button-icon" />
        <span>{{ hasCheckedIn ? 'Checked In ✓' : 'Check In' }}</span>
      </button>
    </div>

    <!-- Time Window Status for Check-In -->
    <div v-if="!hasCheckedIn && !canCheckIn" class="time-warning">
      ⏰ {{ checkInStatusMessage }}
    </div>

    <!-- Check-Out Section (shown at bottom when checked in) -->
    <div v-if="hasCheckedIn && !hasCheckedOut" class="checkout-section">
      <div class="checkout-divider"></div>
      <div class="action-buttons">
        <button 
          @click="checkOut" 
          class="check-out-button"
          :disabled="!canCheckOut"
          :title="checkOutButtonTitle"
        >
          <CheckCircleIcon class="button-icon" />
          <span>Check Out</span>
        </button>
      </div>
      <div v-if="!canCheckOut" class="time-warning">
        ⏰ {{ checkOutStatusMessage }}
      </div>
    </div>

    <div v-if="statusMessage" :class="['status-message', statusClass]">
      <CheckIcon v-if="statusClass === 'success'" class="status-icon" />
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
      statusClass: '',
      isLoading: false,
      hasCheckedIn: false,
      hasCheckedOut: false,
      currentTime: new Date()
    };
  },
  computed: {
    canCheckIn() {
      // Use browser's local time directly - NO CONVERSION
      const now = new Date();
      const checkInStart = new Date(this.event.check_in_start || this.event.start_time);
      const checkInEnd = new Date(this.event.check_in_end || this.event.end_time);
      
      const canCheck = now >= checkInStart && now <= checkInEnd;
      console.log('🔍 Check-in validation (local time, no conversion):', {
        now: now.toString(),
        checkInStart: checkInStart.toString(),
        checkInEnd: checkInEnd.toString(),
        canCheckIn: canCheck
      });
      return canCheck;
    },
    canCheckOut() {
      // Use browser's local time directly - NO CONVERSION
      const now = new Date();
      const checkOutStart = new Date(this.event.check_out_start || this.event.end_time);
      const checkOutEnd = this.event.check_out_end ? new Date(this.event.check_out_end) : null;
      
      let canCheck;
      if (checkOutEnd) {
        canCheck = now >= checkOutStart && now <= checkOutEnd;
      } else {
        canCheck = now >= checkOutStart;
      }
      
      console.log('🔍 Check-out validation (local time, no conversion):', {
        now: now.toString(),
        checkOutStart: checkOutStart.toString(),
        checkOutEnd: checkOutEnd ? checkOutEnd.toString() : 'No end limit',
        canCheckOut: canCheck
      });
      return canCheck;
    },
    checkInStatusMessage() {
      const now = new Date();
      const checkInStart = new Date(this.event.check_in_start || this.event.start_time);
      const checkInEnd = new Date(this.event.check_in_end || this.event.end_time);
      
      if (now < checkInStart) {
        return `Check-in opens at ${this.formatDateTime(checkInStart)}`;
      } else if (now > checkInEnd) {
        return 'Check-in period has ended';
      }
      return '';
    },
    checkOutStatusMessage() {
      const now = new Date();
      const checkOutStart = new Date(this.event.check_out_start || this.event.end_time);
      const checkOutEnd = this.event.check_out_end ? new Date(this.event.check_out_end) : null;
      
      if (now < checkOutStart) {
        return `Check-out opens at ${this.formatDateTime(checkOutStart)}`;
      } else if (checkOutEnd && now > checkOutEnd) {
        return 'Check-out period has ended';
      }
      return '';
    },
    checkInButtonTitle() {
      if (this.hasCheckedIn) return 'Already checked in';
      if (!this.canCheckIn) return this.checkInStatusMessage;
      return 'Click to check in to this event';
    },
    checkOutButtonTitle() {
      if (!this.canCheckOut) return this.checkOutStatusMessage;
      return 'Click to check out from this event';
    }
  },
  async mounted() {
    // Check if student has already checked in to this event
    await this.checkAttendanceStatus();
    
    // Update current time every 30 seconds to refresh button states
    this.timeInterval = setInterval(() => {
      this.currentTime = new Date();
      this.$forceUpdate();
    }, 30000);
  },
  beforeUnmount() {
    if (this.timeInterval) {
      clearInterval(this.timeInterval);
    }
  },
  methods: {
    async checkAttendanceStatus() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `${API_BASE_URL}/attendance/status/${this.event._id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        
        if (response.data.has_checked_in) {
          this.hasCheckedIn = true;
        }
        if (response.data.has_checked_out) {
          this.hasCheckedOut = true;
        }
      } catch (error) {
        // If endpoint doesn't exist or error, just continue
        console.log('Could not check attendance status:', error.message);
      }
    },
    formatDateTime(dateString) {
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
    },
    checkIn() {
      this.isLoading = true;
      this.statusMessage = 'Getting your location...';
      this.statusClass = 'status-loading';
      
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
          this.statusMessage = response.data.message;
          this.statusClass = 'status-success';
          this.hasCheckedIn = true;
          
          this.$emit('checkin', this.status);
        } catch (error) {
          console.error('Check-in failed:', error);
          this.status = 'Error';
          this.statusMessage = error.response?.data?.detail || 'Check-in failed. Please try again.';
          this.statusClass = 'status-error';
        } finally {
          this.isLoading = false;
        }
      }, error => {
        console.error('Geolocation error:', error);
        this.status = 'Error';
        this.statusClass = 'status-error';
        
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
    },
    checkOut() {
      this.isLoading = true;
      this.statusMessage = 'Getting your location...';
      this.statusClass = 'status-loading';
      
      navigator.geolocation.getCurrentPosition(async position => {
        const { latitude, longitude } = position.coords;
        
        try {
          const token = localStorage.getItem('token');
          const response = await axios.post(`${API_BASE_URL}/attendance/checkout`, {
            event_id: this.event._id,
            latitude,
            longitude
          }, {
            headers: { Authorization: `Bearer ${token}` }
          });
          
          this.status = response.data.status;
          this.statusMessage = response.data.message;
          this.statusClass = 'status-success';
          this.hasCheckedOut = true;
          
          this.$emit('checkout', this.status);
        } catch (error) {
          console.error('Check-out failed:', error);
          this.statusMessage = error.response?.data?.detail || 'Check-out failed. Please try again.';
          this.statusClass = 'status-error';
        } finally {
          this.isLoading = false;
        }
      }, error => {
        console.error('Geolocation error:', error);
        this.statusMessage = 'Unable to access your location.';
        this.statusClass = 'status-error';
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

.event-title-section {
  flex: 1;
}

.event-header h3 {
  margin: 0 0 0.5rem 0;
  color: var(--dark-green);
  font-size: 1.25rem;
  font-weight: 700;
}

.location-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
  color: #2E7D32;
  padding: 0.375rem 0.875rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  margin: 0;
  border: 1px solid #A5D6A7;
}

.location-badge-icon {
  width: 14px;
  height: 14px;
}

.event-body {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.timing-section {
  padding: 1rem;
  background: #F9FAFB;
  border-radius: 8px;
  border-left: 4px solid #198754;
  transition: all 0.3s ease;
}

.timing-section:hover {
  background: #F3F4F6;
  transform: translateX(2px);
}

.location-highlight {
  background: linear-gradient(135deg, #E8F5E9, #F1F8F4);
  border-left: 4px solid #2E7D32;
}

.location-name-display {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  margin-bottom: 0.75rem;
  border: 2px solid #A5D6A7;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.location-icon-large {
  width: 40px;
  height: 40px;
  color: #2E7D32;
  flex-shrink: 0;
}

.location-name-text {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.location-label {
  font-size: 0.75rem;
  color: #6B7280;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.location-name-value {
  font-size: 1.1rem;
  color: #1F2937;
  font-weight: 700;
}

.location-name-value.not-set {
  color: #9CA3AF;
  font-style: italic;
  font-weight: 500;
}

.section-title {
  margin: 0 0 0.75rem 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.event-detail {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.event-detail:last-child {
  margin-bottom: 0;
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

.action-buttons {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 0;
}

.check-in-button, .check-out-button {
  flex: 1;
  padding: 1rem;
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
}

.check-in-button {
  background: linear-gradient(135deg, #198754, #0F5132);
  box-shadow: 0 4px 12px rgba(25, 135, 84, 0.3);
}

.check-in-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(25, 135, 84, 0.4);
}

.check-in-button:disabled {
  background: #6C757D;
  cursor: not-allowed;
  opacity: 0.6;
}

.check-out-button {
  background: linear-gradient(135deg, #3B82F6, #2563EB);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.check-out-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
}

.check-out-button:disabled {
  background: #6C757D;
  cursor: not-allowed;
  opacity: 0.6;
}

.checkout-section {
  margin-top: 1.5rem;
}

.checkout-divider {
  height: 1px;
  background: linear-gradient(to right, transparent, var(--gray-300), transparent);
  margin-bottom: 1rem;
}

.check-in-button:active, .check-out-button:active {
  transform: translateY(0);
}

.time-warning {
  margin-top: 1rem;
  padding: 0.875rem;
  background: #FEF3C7;
  border: 1px solid #FCD34D;
  border-radius: 8px;
  color: #92400E;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
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

  /* make action buttons stack nicely on small screens */
  .action-buttons {
    flex-direction: column;
  }

  .check-in-button, .check-out-button { width: 100%; }
}
</style>
