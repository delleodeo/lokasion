<template>
  <div class="edit-event-page">
    <div class="page-header">
      <div>
        <h2>Edit Event</h2>
        <p>Update event details and location settings</p>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading event...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="$router.push('/teacher-events')" class="btn-secondary">
        Back to Events
      </button>
    </div>

    <div v-else class="event-grid">
      <!-- Form Section -->
      <div class="form-container">
        <form @submit.prevent="updateEvent" class="event-form">
          <div class="input-group">
            <label for="name">Event Name *</label>
            <input 
              type="text" 
              id="name" 
              v-model="event.name" 
              placeholder="e.g., Mathematics Lecture"
              required
            >
          </div>

          <div class="input-group">
            <label for="location_name">Venue Name *</label>
            <input 
              type="text" 
              id="location_name" 
              v-model="event.location_name" 
              placeholder="e.g., Room 301, Main Building"
              required
            >
          </div>

          <div class="location-section">
            <div class="location-header">
              <label>Event Location Coordinates</label>
              <button type="button" @click="useCurrentLocation" class="btn-location" :disabled="isGettingLocation">
                <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span v-if="isGettingLocation">Getting location...</span>
                <span v-else>Update to Current Location</span>
              </button>
            </div>
            
            <div class="coordinate-inputs">
              <div class="input-group">
                <label for="latitude">Latitude *</label>
                <input 
                  type="number" 
                  step="any" 
                  id="latitude" 
                  v-model.number="event.location.latitude" 
                  required
                >
              </div>
              <div class="input-group">
                <label for="longitude">Longitude *</label>
                <input 
                  type="number" 
                  step="any" 
                  id="longitude" 
                  v-model.number="event.location.longitude" 
                  required
                >
              </div>
            </div>

            <div class="input-group">
              <label for="radius">Check-in Radius (meters) *</label>
              <input 
                type="number" 
                id="radius" 
                v-model.number="event.location.radius" 
                min="1" 
                required
              >
              <small class="input-hint">Students must be within this radius to check in</small>
            </div>
          </div>

          <div class="datetime-grid">
            <div class="input-group">
              <label for="check_in_start">Check-in Start Time *</label>
              <input 
                type="datetime-local" 
                id="check_in_start" 
                v-model="event.check_in_start" 
                required
              >
            </div>

            <div class="input-group">
              <label for="check_in_end">Check-in End Time *</label>
              <input 
                type="datetime-local" 
                id="check_in_end" 
                v-model="event.check_in_end" 
                required
              >
            </div>

            <div class="input-group">
              <label for="check_out_start">Check-out Start Time *</label>
              <input 
                type="datetime-local" 
                id="check_out_start" 
                v-model="event.check_out_start" 
                required
              >
            </div>

            <div class="input-group">
              <label for="check_out_end">Check-out End Time *</label>
              <input 
                type="datetime-local" 
                id="check_out_end" 
                v-model="event.check_out_end" 
                required
              >
            </div>
          </div>

          <div v-if="submitError" class="error-message">
            {{ submitError }}
          </div>

          <div class="form-actions">
            <button type="button" @click="$router.push('/teacher-events')" class="btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="isSubmitting">
              <span v-if="isSubmitting">Updating Event...</span>
              <span v-else>Save Changes</span>
            </button>
          </div>
        </form>
      </div>

      <!-- Preview Section -->
      <div class="preview-container">
        <div class="preview-card">
          <h3>Event Preview</h3>
          
          <div class="preview-section">
            <h4>{{ event.name || 'Event Name' }}</h4>
            <div class="preview-detail">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              </svg>
              <span>{{ event.location_name || 'Venue Name' }}</span>
            </div>
          </div>

          <div class="preview-section">
            <h4>Check-in Window</h4>
            <div class="preview-detail">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{{ formatDateTime(event.check_in_start) }} - {{ formatDateTime(event.check_in_end) }}</span>
            </div>
          </div>

          <div class="preview-section">
            <h4>Check-out Window</h4>
            <div class="preview-detail">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{{ formatDateTime(event.check_out_start) }} - {{ formatDateTime(event.check_out_end) }}</span>
            </div>
          </div>

          <div class="preview-section">
            <h4>Location Settings</h4>
            <div class="preview-detail">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              <span>{{ event.location.radius || 0 }}m radius</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../config';

export default {
  name: 'EditEvent',
  data() {
    return {
      event: {
        name: '',
        location_name: '',
        location: {
          latitude: 0,
          longitude: 0,
          radius: 50
        },
        check_in_start: '',
        check_in_end: '',
        check_out_start: '',
        check_out_end: ''
      },
      loading: true,
      error: null,
      isGettingLocation: false,
      isSubmitting: false,
      submitError: null
    };
  },
  async mounted() {
    await this.loadEvent();
  },
  methods: {
    async loadEvent() {
      this.loading = true;
      this.error = null;

      try {
        const token = localStorage.getItem('token');
        const eventId = this.$route.params.id;

        const response = await axios.get(`${API_BASE_URL}/events`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        const event = response.data.find(e => e._id === eventId);

        if (!event) {
          this.error = 'Event not found';
          return;
        }

        // Convert datetime strings to local datetime-local format
        this.event = {
          name: event.name,
          location_name: event.location_name,
          location: {
            latitude: event.location.latitude,
            longitude: event.location.longitude,
            radius: event.location.radius
          },
          check_in_start: this.toLocalDateTimeString(event.check_in_start),
          check_in_end: this.toLocalDateTimeString(event.check_in_end),
          check_out_start: this.toLocalDateTimeString(event.check_out_start),
          check_out_end: this.toLocalDateTimeString(event.check_out_end)
        };

      } catch (error) {
        console.error('Failed to load event:', error);
        this.error = error.response?.data?.detail || 'Failed to load event';
      } finally {
        this.loading = false;
      }
    },

    toLocalDateTimeString(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${year}-${month}-${day}T${hours}:${minutes}`;
    },

    formatDateTime(dateString) {
      if (!dateString) return 'Not set';
      const date = new Date(dateString);
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    useCurrentLocation() {
      this.isGettingLocation = true;
      
      navigator.geolocation.getCurrentPosition(
        (position) => {
          this.event.location.latitude = position.coords.latitude;
          this.event.location.longitude = position.coords.longitude;
          this.isGettingLocation = false;
        },
        (error) => {
          console.error('Geolocation error:', error);
          alert('Unable to get your location. Please enter coordinates manually.');
          this.isGettingLocation = false;
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0
        }
      );
    },

    async updateEvent() {
      this.isSubmitting = true;
      this.submitError = null;

      try {
        const token = localStorage.getItem('token');
        const eventId = this.$route.params.id;

        // Convert datetime-local to ISO strings
        const eventData = {
          name: this.event.name,
          location_name: this.event.location_name,
          location: this.event.location,
          check_in_start: new Date(this.event.check_in_start).toISOString(),
          check_in_end: new Date(this.event.check_in_end).toISOString(),
          check_out_start: new Date(this.event.check_out_start).toISOString(),
          check_out_end: new Date(this.event.check_out_end).toISOString()
        };

        await axios.put(
          `${API_BASE_URL}/events/${eventId}`,
          eventData,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        // Redirect back to teacher events with success message
        this.$router.push({
          path: '/teacher-events',
          query: { success: 'Event updated successfully!' }
        });

      } catch (error) {
        console.error('Failed to update event:', error);
        this.submitError = error.response?.data?.detail || 'Failed to update event. Please try again.';
      } finally {
        this.isSubmitting = false;
      }
    }
  }
};
</script>

<style scoped>
.edit-event-page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h2 {
  font-size: 2rem;
  color: var(--dark-green);
  margin: 0 0 0.5rem 0;
}

.page-header p {
  color: var(--gray-600);
  margin: 0;
}

.loading {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid var(--light-green);
  border-top-color: var(--medium-green);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
}

.error-message p {
  color: #c00;
  margin-bottom: 1rem;
}

.event-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 2rem;
}

.form-container,
.preview-container {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.event-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-group label {
  font-weight: 600;
  color: var(--dark-green);
}

.input-group input,
.input-group select {
  padding: 0.75rem;
  border: 2px solid var(--gray-300);
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.input-group input:focus,
.input-group select:focus {
  outline: none;
  border-color: var(--medium-green);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.input-hint {
  color: var(--gray-600);
  font-size: 0.875rem;
}

.location-section {
  border: 2px solid var(--light-green);
  border-radius: 12px;
  padding: 1.5rem;
  background: var(--light-green);
}

.location-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.location-header label {
  font-weight: 600;
  color: var(--dark-green);
}

.btn-location {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--medium-green);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-location:hover:not(:disabled) {
  background: var(--dark-green);
  transform: translateY(-2px);
}

.btn-location:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.coordinate-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.datetime-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 2px solid var(--light-green);
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
}

.btn-primary {
  background: var(--medium-green);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--dark-green);
  transform: translateY(-2px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--gray-200);
  color: var(--gray-700);
}

.btn-secondary:hover {
  background: var(--gray-300);
}

.preview-card {
  position: sticky;
  top: 2rem;
}

.preview-card h3 {
  font-size: 1.5rem;
  color: var(--dark-green);
  margin: 0 0 1.5rem 0;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--light-green);
}

.preview-section {
  margin-bottom: 1.5rem;
}

.preview-section h4 {
  font-size: 1.1rem;
  color: var(--dark-green);
  margin: 0 0 0.75rem 0;
}

.preview-detail {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--gray-700);
}

.preview-detail .icon {
  width: 20px;
  height: 20px;
  color: var(--medium-green);
  flex-shrink: 0;
}

@media (max-width: 1024px) {
  .event-grid {
    grid-template-columns: 1fr;
  }

  .preview-card {
    position: static;
  }
}

@media (max-width: 768px) {
  .edit-event-page {
    padding: 1rem;
  }

  .datetime-grid,
  .coordinate-inputs {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style>
