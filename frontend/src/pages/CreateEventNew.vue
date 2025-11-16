<template>
  <div class="create-event-page">
    <!-- Not Enrolled Warning -->
    <div v-if="!isApproved" class="warning-banner">
      <div class="warning-content">
        <svg class="warning-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
        </svg>
        <div>
          <h3>Enrollment Required</h3>
          <p>You must be approved for a department before creating events. Please go to <router-link to="/societies" class="warning-link">Societies</router-link> to request enrollment.</p>
        </div>
      </div>
    </div>

    <div class="page-header">
      <div>
        <h2>Create New Event</h2>
        <p>Set up an event with location-based attendance tracking</p>
      </div>
    </div>

    <div v-if="isApproved" class="event-grid">
      <!-- Form Section -->
      <div class="form-container">
        <form @submit.prevent="createEvent" class="event-form">
          <div class="input-group">
            <label for="department">Society/Department *</label>
            <select 
              id="department" 
              v-model="event.department_id" 
              required
              class="department-select"
            >
              <option value="">Select a society</option>
              <option 
                v-for="dept in teacherDepartments" 
                :key="dept.department_id" 
                :value="dept.department_id"
              >
                {{ dept.department_name }}
              </option>
            </select>
            <small class="input-hint">Choose which society this event belongs to</small>
          </div>

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
              placeholder="e.g., Room 301, Main Building or Manila City Hall"
              required
            >
            <small class="input-hint">Help students know exactly where to go</small>
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
                <span v-else>Use My Current Location</span>
              </button>
            </div>

            <div class="location-inputs">
              <div class="input-group">
                <label for="latitude">Latitude *</label>
                <input 
                  type="number" 
                  step="any" 
                  id="latitude" 
                  v-model.number="event.latitude" 
                  @input="onManualLocationChange"
                  placeholder="e.g., 14.5995"
                  required
                >
              </div>

              <div class="input-group">
                <label for="longitude">Longitude *</label>
                <input 
                  type="number" 
                  step="any" 
                  id="longitude" 
                  v-model.number="event.longitude" 
                  @input="onManualLocationChange"
                  placeholder="e.g., 120.9842"
                  required
                >
              </div>
            </div>
            <p class="location-hint">Click on the map, use your current location, or enter coordinates manually</p>
          </div>

          <div class="input-group">
            <label for="radius">Check-in Radius (meters) *</label>
            <input 
              type="range" 
              id="radius" 
              v-model.number="event.radius" 
              min="10"
              max="500"
              step="10"
            >
            <div class="radius-display">{{ event.radius }}m</div>
          </div>

          <div class="time-inputs">
            <div class="input-group">
              <label for="start_time">Event Start Time *</label>
              <input 
                type="datetime-local" 
                id="start_time" 
                v-model="event.start_time" 
                required
              >
              <small class="input-hint">Select the exact time for the event</small>
            </div>

            <div class="input-group">
              <label for="end_time">Event End Time *</label>
              <input 
                type="datetime-local" 
                id="end_time" 
                v-model="event.end_time" 
                required
              >
              <small class="input-hint">Select the exact time for the event</small>
            </div>
          </div>

          <!-- Check-in Period -->
          <div class="section-divider">
            <h3>📥 Check-In Period</h3>
            <p class="section-description">Set when students can check in to the event</p>
          </div>

          <div class="time-inputs">
            <div class="input-group">
              <label for="check_in_start">Check-In Opens</label>
              <input 
                type="datetime-local" 
                id="check_in_start" 
                v-model="event.check_in_start"
                placeholder="Optional (defaults to event start)"
              >
              <small class="input-hint">Leave empty to use event start time</small>
            </div>

            <div class="input-group">
              <label for="check_in_end">Check-In Closes</label>
              <input 
                type="datetime-local" 
                id="check_in_end" 
                v-model="event.check_in_end"
                placeholder="Optional (defaults to event end)"
              >
              <small class="input-hint">Leave empty to use event end time</small>
            </div>
          </div>

          <!-- Check-out Period -->
          <div class="section-divider">
            <h3>📤 Check-Out Period</h3>
            <p class="section-description">Set when students must check out from the event</p>
          </div>

          <div class="time-inputs">
            <div class="input-group">
              <label for="check_out_start">Check-Out Opens</label>
              <input 
                type="datetime-local" 
                id="check_out_start" 
                v-model="event.check_out_start"
                placeholder="Optional (defaults to event end)"
              >
              <small class="input-hint">Leave empty to use event end time</small>
            </div>

            <div class="input-group">
              <label for="check_out_end">Check-Out Closes</label>
              <input 
                type="datetime-local" 
                id="check_out_end" 
                v-model="event.check_out_end"
                placeholder="Optional"
              >
              <small class="input-hint">Leave empty for no deadline</small>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-primary" :disabled="isLoading || !event.latitude">
              <span v-if="isLoading">Creating...</span>
              <span v-else>Create Event</span>
            </button>
            <button type="button" class="btn-secondary" @click="resetForm">Clear</button>
          </div>

          <div v-if="message" :class="['message', messageType]">
            {{ message }}
          </div>
        </form>
      </div>

      <!-- Map Section -->
      <div class="map-container">
        <div class="map-header">
          <h3>Select Event Location</h3>
          <p>Click on the map to set the event location</p>
        </div>
        <div id="map" class="map"></div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../config.js';
import { jwtDecode } from 'jwt-decode';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in Leaflet with bundlers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

export default {
  name: 'CreateEvent',
  props: {
    departmentId: {
      type: String,
      default: null
    },
    departmentName: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      event: {
        name: '',
        location_name: '',
        latitude: null,
        longitude: null,
        radius: 100,
        start_time: '',
        end_time: '',
        check_in_start: '',
        check_in_end: '',
        check_out_start: '',
        check_out_end: '',
        department_id: ''
      },
      teacherDepartments: [],
      message: '',
      messageType: '',
      isLoading: false,
      isApproved: false,
      isGettingLocation: false,
      map: null,
      marker: null,
      circle: null
    };
  },
  async mounted() {
    await this.checkEnrollmentStatus();
    if (this.isApproved) {
      await this.fetchTeacherDepartments();
      this.initMap();
    }
  },
  methods: {
    async checkEnrollmentStatus() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/enrollments/my-enrollments`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        // Check if teacher has any approved enrollment
        const approvedEnrollment = response.data.find(e => e.status === 'approved');
        this.isApproved = !!approvedEnrollment;
        
        if (!this.isApproved) {
          this.message = 'You must be enrolled and approved in a department to create events';
          this.messageType = 'error';
        }
      } catch (error) {
        console.error('Error checking enrollment status:', error);
        this.isApproved = false;
      }
    },
    async fetchTeacherDepartments() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/enrollments/teacher/departments`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.teacherDepartments = response.data;
        
        // Check if department was passed via query params (from Societies page)
        const departmentId = this.$route.query.departmentId;
        if (departmentId && this.teacherDepartments.some(d => d.department_id === departmentId)) {
          this.event.department_id = departmentId;
        }
        // Don't auto-select - teacher must explicitly choose the society
      } catch (error) {
        console.error('Error fetching teacher departments:', error);
      }
    },
    initMap() {
      // Initialize map centered on a default location
      this.map = L.map('map').setView([14.5995, 120.9842], 13); // Manila coordinates as default

      // Add OpenStreetMap tiles
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
      }).addTo(this.map);

      // Add click event to set marker
      this.map.on('click', (e) => {
        this.setLocation(e.latlng.lat, e.latlng.lng);
      });

      // Try to get user's current location
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const { latitude, longitude } = position.coords;
            this.map.setView([latitude, longitude], 15);
            this.message = 'Location access granted! Map centered on your location.';
            this.messageType = 'success';
            setTimeout(() => { this.message = ''; }, 3000);
          },
          (error) => {
            if (error.code === 1) {
              this.message = 'Location access denied. Using default location (Manila). Click on the map to set your event location.';
              this.messageType = 'info';
            } else {
              console.log('Could not get current location:', error);
              this.message = 'Could not get your location. Using default location (Manila). Click on the map to set your event location.';
              this.messageType = 'info';
            }
            setTimeout(() => { this.message = ''; }, 5000);
          }
        );
      }
    },
    useCurrentLocation() {
      if (!navigator.geolocation) {
        this.message = 'Geolocation is not supported by your browser';
        this.messageType = 'error';
        return;
      }

      this.isGettingLocation = true;
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          this.setLocation(latitude, longitude);
          this.map.setView([latitude, longitude], 17);
          this.message = 'Using your current location!';
          this.messageType = 'success';
          setTimeout(() => { this.message = ''; }, 3000);
          this.isGettingLocation = false;
        },
        (error) => {
          console.error('Geolocation error:', error);
          if (error.code === 1) {
            this.message = 'Location access denied. Please enable location services.';
          } else if (error.code === 2) {
            this.message = 'Location unavailable. Please try again.';
          } else {
            this.message = 'Error getting location. Please try again.';
          }
          this.messageType = 'error';
          setTimeout(() => { this.message = ''; }, 5000);
          this.isGettingLocation = false;
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0
        }
      );
    },
    onManualLocationChange() {
      // When user manually types coordinates, update the map
      if (this.event.latitude && this.event.longitude) {
        const lat = parseFloat(this.event.latitude);
        const lng = parseFloat(this.event.longitude);
        
        // Validate coordinates
        if (!isNaN(lat) && !isNaN(lng) && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
          this.setLocation(lat, lng);
          this.map.setView([lat, lng], 15);
        }
      }
    },
    setLocation(lat, lng) {
      this.event.latitude = parseFloat(lat.toFixed(6));
      this.event.longitude = parseFloat(lng.toFixed(6));

      // Remove existing marker and circle if any
      if (this.marker) {
        this.map.removeLayer(this.marker);
      }
      if (this.circle) {
        this.map.removeLayer(this.circle);
      }

      // Add new marker
      this.marker = L.marker([lat, lng]).addTo(this.map);
      this.marker.bindPopup(`<b>Event Location</b><br>Lat: ${lat.toFixed(6)}<br>Lng: ${lng.toFixed(6)}`).openPopup();

      // Add circle showing radius
      this.updateCircle();
    },
    updateCircle() {
      if (this.circle) {
        this.map.removeLayer(this.circle);
      }
      
      if (this.event.latitude && this.event.longitude) {
        this.circle = L.circle([this.event.latitude, this.event.longitude], {
          color: '#198754',
          fillColor: '#198754',
          fillOpacity: 0.2,
          radius: this.event.radius
        }).addTo(this.map);
      }
    },
    async createEvent() {
      if (!this.event.latitude || !this.event.longitude) {
        this.message = 'Please select a location on the map';
        this.messageType = 'error';
        return;
      }

      // Validate that a department is selected
      if (!this.event.department_id) {
        this.message = 'Please select a society/department for this event';
        this.messageType = 'error';
        return;
      }

      this.isLoading = true;
      try {
        const token = localStorage.getItem('token');
        const decodedToken = jwtDecode(token);
        
        // Convert datetime-local to local time string WITHOUT UTC conversion
        const toLocalDateTime = (datetimeLocal) => {
          if (!datetimeLocal) return null;
          // datetime-local format: "2025-11-16T18:46"
          // Return as-is with seconds appended (backend expects YYYY-MM-DDTHH:mm:ss)
          return datetimeLocal.length === 16 ? datetimeLocal + ':00' : datetimeLocal;
        };
        
        const eventData = {
          name: this.event.name,
          location_name: this.event.location_name || null,
          latitude: this.event.latitude,
          longitude: this.event.longitude,
          radius: this.event.radius,
          teacher_id: decodedToken.user_id,
          department_id: this.event.department_id,
          start_time: toLocalDateTime(this.event.start_time),
          end_time: toLocalDateTime(this.event.end_time),
        };

        // Add optional check-in/check-out times if provided
        if (this.event.check_in_start) {
          eventData.check_in_start = toLocalDateTime(this.event.check_in_start);
        }
        if (this.event.check_in_end) {
          eventData.check_in_end = toLocalDateTime(this.event.check_in_end);
        }
        if (this.event.check_out_start) {
          eventData.check_out_start = toLocalDateTime(this.event.check_out_start);
        }
        if (this.event.check_out_end) {
          eventData.check_out_end = toLocalDateTime(this.event.check_out_end);
        }

        console.log('📅 Sending event data:', eventData);

        await axios.post(`${API_BASE_URL}/events/`, eventData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        this.message = 'Event created successfully!';
        this.messageType = 'success';
        
        setTimeout(() => {
          this.$router.push('/events');
        }, 1500);
      } catch (error) {
        console.error('Failed to create event:', error);
        this.message = error.response?.data?.detail || 'Failed to create event. Please check your input.';
        this.messageType = 'error';
      } finally {
        this.isLoading = false;
      }
    },
    resetForm() {
      this.event = {
        name: '',
        location_name: '',
        latitude: null,
        longitude: null,
        radius: 100,
        start_time: '',
        end_time: '',
        check_in_start: '',
        check_in_end: '',
        check_out_start: '',
        check_out_end: ''
      };
      
      if (this.marker) {
        this.map.removeLayer(this.marker);
      }
      if (this.circle) {
        this.map.removeLayer(this.circle);
      }
    }
  },
  watch: {
    'event.radius'() {
      this.updateCircle();
    }
  },
  beforeUnmount() {
    if (this.map) {
      this.map.remove();
    }
  }
}
</script>

<style scoped>
.create-event-page {
  max-width: 1600px;
}

.warning-banner {
  background: linear-gradient(135deg, #FEF3C7, #FDE68A);
  border: 2px solid #F59E0B;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.2);
}

.warning-content {
  display: flex;
  gap: 1rem;
  align-items: start;
}

.warning-icon {
  width: 32px;
  height: 32px;
  color: #D97706;
  flex-shrink: 0;
}

.warning-content h3 {
  color: #92400E;
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.warning-content p {
  color: #78350F;
  margin: 0;
  line-height: 1.5;
}

.warning-link {
  color: #D97706;
  font-weight: 600;
  text-decoration: underline;
}

.warning-link:hover {
  color: #B45309;
}

.page-header {
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

.department-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #DBEAFE, #BFDBFE);
  color: #1E40AF;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  border: 2px solid #3B82F6;
  margin-top: 0.5rem;
}

.badge-icon {
  width: 20px;
  height: 20px;
}

.event-grid {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 2rem;
  align-items: start;
}

.form-container {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--gray-200);
  height: fit-content;
}

.event-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-group label {
  font-weight: 600;
  color: var(--gray-800);
  margin-bottom: 0.75rem;
  font-size: 0.95rem;
}

.input-group input[type="text"],
.input-group input[type="number"],
.input-group input[type="datetime-local"] {
  padding: 0.875rem;
  border: 2px solid var(--gray-200);
  border-radius: 10px;
  font-size: 1rem;
  transition: var(--transition);
  background: var(--gray-50);
}

.input-group input:focus {
  outline: none;
  border-color: var(--medium-green);
  background: white;
  box-shadow: 0 0 0 4px rgba(25, 135, 84, 0.1);
}

.input-group input[readonly] {
  background: var(--gray-100);
  cursor: not-allowed;
}

.location-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.location-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.location-header label {
  font-weight: 600;
  color: var(--gray-800);
  font-size: 0.95rem;
}

.btn-location {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, #3B82F6, #2563EB);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-location:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563EB, #1D4ED8);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
}

.btn-location:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-location .btn-icon {
  width: 18px;
  height: 18px;
}

.location-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.location-hint {
  font-size: 0.875rem;
  color: var(--gray-600);
  margin: 0;
  font-style: italic;
}

.section-divider {
  margin: 2rem 0 1.5rem;
  padding-top: 1.5rem;
  border-top: 2px solid var(--gray-200);
}

.section-divider h3 {
  color: var(--dark-green);
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.section-description {
  color: var(--gray-600);
  font-size: 0.875rem;
  margin: 0;
}

.input-hint {
  display: block;
  font-size: 0.75rem;
  color: var(--gray-500);
  margin-top: 0.25rem;
  font-style: italic;
}

.time-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.input-group input[type="range"] {
  width: 100%;
  height: 8px;
  border-radius: 5px;
  background: linear-gradient(to right, #D1E7DD 0%, #198754 100%);
  outline: none;
  -webkit-appearance: none;
  appearance: none;
}

.input-group input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--medium-green);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(25, 135, 84, 0.4);
}

.input-group input[type="range"]::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--medium-green);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(25, 135, 84, 0.4);
  border: none;
}

.radius-display {
  text-align: center;
  font-weight: 700;
  color: var(--medium-green);
  font-size: 1.25rem;
  margin-top: 0.5rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.btn-primary {
  flex: 1;
  padding: 1rem;
  background: linear-gradient(135deg, #198754, #0F5132);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  transition: var(--transition);
  box-shadow: 0 4px 15px rgba(25, 135, 84, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(25, 135, 84, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  padding: 1rem 1.5rem;
  background: white;
  color: var(--dark-green);
  border: 2px solid var(--gray-300);
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  transition: var(--transition);
}

.btn-secondary:hover {
  background: var(--gray-50);
  border-color: var(--medium-green);
}

.map-container {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--gray-200);
  position: sticky;
  top: 2rem;
}

.map-header {
  margin-bottom: 1rem;
}

.map-header h3 {
  color: var(--dark-green);
  font-size: 1.25rem;
  margin-bottom: 0.25rem;
}

.map-header p {
  color: var(--gray-600);
  font-size: 0.9rem;
}

.map {
  height: 500px;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid var(--gray-200);
}

.message {
  padding: 1rem;
  border-radius: 10px;
  font-weight: 500;
  animation: slideIn 0.3s ease-out;
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

.message.info {
  background: #D1ECF1;
  color: #0C5460;
  border: 2px solid #17A2B8;
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

@media (max-width: 1200px) {
  .event-grid {
    grid-template-columns: 1fr;
  }

  .map-container {
    position: static;
  }
}

@media (max-width: 768px) {
  .location-inputs,
  .time-inputs {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
  }

  .map {
    height: 400px;
  }
}
</style>
