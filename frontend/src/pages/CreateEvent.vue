<template>
  <div class="create-event-page">
    <div class="page-header">
      <h2>Create New Event</h2>
      <p>Set up an event with location-based attendance</p>
    </div>

    <div class="form-container">
      <form @submit.prevent="createEvent" class="event-form">
        <div class="form-grid">
          <div class="input-group">
            <label for="name">Event Name *</label>
            <input 
              type="text" 
              id="name" 
              v-model="event.name" 
              placeholder="e.g., Mathematics Class"
              required
            >
          </div>

          <div class="input-group">
            <label for="latitude">Latitude *</label>
            <input 
              type="number" 
              step="any" 
              id="latitude" 
              v-model.number="event.latitude" 
              placeholder="e.g., 37.7749"
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
              placeholder="e.g., -122.4194"
              required
            >
          </div>

          <div class="input-group">
            <label for="radius">Radius (meters) *</label>
            <input 
              type="number" 
              id="radius" 
              v-model.number="event.radius" 
              placeholder="e.g., 100"
              required
            >
          </div>

          <div class="input-group">
            <label for="start_time">Start Time *</label>
            <input 
              type="datetime-local" 
              id="start_time" 
              v-model="event.start_time" 
              required
            >
          </div>

          <div class="input-group">
            <label for="end_time">End Time *</label>
            <input 
              type="datetime-local" 
              id="end_time" 
              v-model="event.end_time" 
              required
            >
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn-primary" :disabled="isLoading">
            {{ isLoading ? 'Creating...' : 'Create Event' }}
          </button>
          <button type="button" class="btn-secondary" @click="resetForm">Clear</button>
        </div>

        <div v-if="message" :class="['message', messageType]">
          {{ message }}
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../config.js';
import { jwtDecode } from 'jwt-decode';

export default {
  name: 'CreateEvent',
  data() {
    return {
      event: {
        name: '',
        latitude: 0,
        longitude: 0,
        radius: 100,
        start_time: '',
        end_time: ''
      },
      message: '',
      messageType: '',
      isLoading: false
    };
  },
  methods: {
    async createEvent() {
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
          ...this.event,
          teacher_id: decodedToken.user_id,
          start_time: toLocalDateTime(this.event.start_time),
          end_time: toLocalDateTime(this.event.end_time)
        };

        await axios.post(`${API_BASE_URL}/events/`, eventData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        this.message = 'Event created successfully!';
        this.messageType = 'success';
        this.resetForm();
        
        setTimeout(() => {
          this.message = '';
        }, 3000);
      } catch (error) {
        console.error('Failed to create event:', error);
        this.message = 'Failed to create event. Please check your input.';
        this.messageType = 'error';
      } finally {
        this.isLoading = false;
      }
    },
    resetForm() {
      this.event = {
        name: '',
        latitude: 0,
        longitude: 0,
        radius: 100,
        start_time: '',
        end_time: ''
      };
    }
  }
}
</script>

<style scoped>
.create-event-page {
  max-width: 900px;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h2 {
  color: var(--dark-green);
  margin-bottom: 0.5rem;
  font-size: 2rem;
}

.page-header p {
  color: var(--gray-600);
}

.form-container {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--gray-200);
}

.event-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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

.input-group input {
  padding: 0.875rem;
  border: 2px solid var(--gray-200);
  border-radius: 8px;
  font-size: 1rem;
  transition: var(--transition);
  background: var(--gray-50);
}

.input-group input:focus {
  outline: none;
  border-color: var(--medium-green);
  background: white;
  box-shadow: 0 0 0 3px rgba(25, 135, 84, 0.1);
}

.form-actions {
  display: flex;
  gap: 1rem;
}

.btn-primary {
  flex: 1;
  padding: 1rem;
  background: linear-gradient(135deg, #198754, #0F5132);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  transition: var(--transition);
  box-shadow: 0 4px 12px rgba(25, 135, 84, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(25, 135, 84, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  flex: 1;
  padding: 1rem;
  background: var(--gray-100);
  color: var(--dark-green);
  border: 2px solid var(--gray-300);
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  transition: var(--transition);
}

.btn-secondary:hover {
  background: var(--gray-200);
}

.message {
  padding: 1rem;
  border-radius: 8px;
  animation: slideIn 0.3s ease-out;
}

.message.success {
  background: #D1E7DD;
  color: #0F5132;
  border: 1px solid #198754;
}

.message.error {
  background: #F8D7DA;
  color: #842029;
  border: 1px solid #F5C2C7;
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
  .form-container {
    padding: 1.5rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
  }
}
</style>
