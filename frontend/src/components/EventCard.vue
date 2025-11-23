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

    <!-- Camera Modal - Teleported to body to prevent parent hover effects -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="showCameraModal" class="modal-overlay" @click.self="closeCameraModal">
          <div class="modal-content">
            <button @click="closeCameraModal" class="close-button">✕</button>
            <h3>Face Verification</h3>
            <Transition name="text-fade" mode="out-in">
              <p v-if="!isCapturing" key="instruction">Position your face within the circle</p>
              <p v-else key="scanning" class="scanning-text">{{ scanningMessage }}</p>
            </Transition>
            <div class="camera-container">
              <video ref="video" autoplay playsinline muted class="camera-feed"></video>
              <canvas ref="canvas" class="camera-feed-hidden"></canvas>
              <Transition name="fade">
                <div v-if="!isCapturing" class="face-guide" key="guide">
                  <div class="guide-circle"></div>
                </div>
              </Transition>
              <Transition name="fade">
                <div v-if="isCapturing" class="scanning-overlay" key="scanning">
                  <div class="countdown-circle">
                    <span class="countdown-number">{{ countdown }}</span>
                  </div>
                  <div class="scanning-line"></div>
                </div>
              </Transition>
            </div>
            <Transition name="fade">
              <div v-if="!isCapturing" class="modal-actions" key="actions">
                <button @click="closeCameraModal" class="btn-secondary">Cancel</button>
                <button @click="startAutoCapture" class="btn-primary" :disabled="!cameraReady">
                  <span v-if="cameraReady">Start Verification</span>
                  <span v-else>Loading Camera...</span>
                </button>
              </div>
            </Transition>
          </div>
        </div>
      </Transition>
    </Teleport>
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
      currentTime: new Date(),
      showCameraModal: false,
      stream: null,
      cameraReady: false,
      isCapturing: false,
      countdown: 3,
      countdownInterval: null,
      capturedImage: null,
      scanningMessage: 'Initializing...',
      checkoutMode: false
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
    this.stopCamera();
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
    async checkIn() {
      // Open camera modal instead of direct check-in
      this.showCameraModal = true;
      await this.startCamera();
    },
    async startCamera() {
      try {
        this.cameraReady = false;
        this.stream = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'user',
            frameRate: { ideal: 30 }
          } 
        });
        
        await this.$nextTick();
        
        if (this.$refs.video) {
          const video = this.$refs.video;
          video.srcObject = this.stream;
          
          await new Promise((resolve) => {
            video.onloadedmetadata = () => {
              video.play().then(() => {
                this.cameraReady = true;
                resolve();
              }).catch(err => {
                console.error('Error playing video:', err);
                resolve();
              });
            };
          });
        }
      } catch (error) {
        console.error('Error accessing camera:', error);
        this.statusMessage = 'Could not access camera. Please allow camera access.';
        this.statusClass = 'status-error';
        this.showCameraModal = false;
      }
    },
    stopCamera() {
      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop());
        this.stream = null;
      }
      if (this.countdownInterval) {
        clearInterval(this.countdownInterval);
        this.countdownInterval = null;
      }
    },
    closeCameraModal() {
      this.isCapturing = false;
      if (this.countdownInterval) {
        clearInterval(this.countdownInterval);
        this.countdownInterval = null;
      }
      this.stopCamera();
      // Delay state reset to allow smooth transition
      setTimeout(() => {
        this.showCameraModal = false;
        this.cameraReady = false;
        this.countdown = 3;
        this.capturedImage = null;
        this.checkoutMode = false;
      }, 300);
    },
    startAutoCapture() {
      if (!this.cameraReady || this.isCapturing) return;
      
      this.isCapturing = true;
      this.countdown = 3;
      this.scanningMessage = 'Get ready...';
      
      // Use requestAnimationFrame for smoother updates
      let lastTime = Date.now();
      
      this.countdownInterval = setInterval(() => {
        const currentTime = Date.now();
        const elapsed = currentTime - lastTime;
        
        if (elapsed >= 1000) {
          this.countdown--;
          lastTime = currentTime;
          
          if (this.countdown > 0) {
            this.scanningMessage = `Capturing in ${this.countdown}...`;
          } else {
            this.scanningMessage = 'Capturing...';
            clearInterval(this.countdownInterval);
            this.countdownInterval = null;
            
            // Small delay for smooth capture
            requestAnimationFrame(() => {
              setTimeout(() => {
                this.captureAndCheckIn();
              }, 300);
            });
          }
        }
      }, 100);
    },
    async captureAndCheckIn() {
      const video = this.$refs.video;
      const canvas = this.$refs.canvas;
      
      if (!video) {
        // Reset state if video is not available
        this.resetCameraState();
        return;
      }
      
      try {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        const imageBlob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
        
        this.stopCamera();
        this.showCameraModal = false;
        
        // Reset capturing state
        this.isCapturing = false;
        this.countdown = 3;
        
        if (this.checkoutMode) {
          this.performCheckOut(imageBlob);
          this.checkoutMode = false;
        } else {
          this.performCheckIn(imageBlob);
        }
      } catch (error) {
        console.error('Error capturing image:', error);
        this.resetCameraState();
        this.statusMessage = 'Failed to capture image. Please try again.';
        this.statusClass = 'status-error';
      }
    },
    resetCameraState() {
      // Clear countdown interval if running
      if (this.countdownInterval) {
        clearInterval(this.countdownInterval);
        this.countdownInterval = null;
      }
      
      // Reset all camera-related state
      this.isCapturing = false;
      this.countdown = 3;
      this.cameraReady = false;
      this.capturedImage = null;
      this.scanningMessage = 'Initializing...';
      
      // Stop camera stream
      this.stopCamera();
    },
    performCheckIn(imageBlob) {
      this.isLoading = true;
      this.statusMessage = 'Getting your location...';
      this.statusClass = 'status-loading';
      
      navigator.geolocation.getCurrentPosition(async position => {
        const { latitude, longitude, accuracy } = position.coords;
        
        console.log('📍 Student location:', { latitude, longitude, accuracy });
        
        try {
          const token = localStorage.getItem('token');
          const formData = new FormData();
          formData.append('event_id', this.event._id);
          formData.append('latitude', latitude);
          formData.append('longitude', longitude);
          if (imageBlob) {
            formData.append('image', imageBlob, 'checkin.jpg');
          }
          
          const response = await axios.post(`${API_BASE_URL}/attendance/checkin`, formData, {
            headers: { 
              Authorization: `Bearer ${token}`,
              'Content-Type': 'multipart/form-data'
            }
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
          // Reset camera state so user can try again
          this.resetCameraState();
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
    async checkOut() {
      // Open camera modal for checkout as well
      this.showCameraModal = true;
      this.checkoutMode = true;
      await this.startCamera();
    },
    async performCheckOut(imageBlob) {
      this.isLoading = true;
      this.statusMessage = 'Getting your location...';
      this.statusClass = 'status-loading';
      
      navigator.geolocation.getCurrentPosition(async position => {
        const { latitude, longitude } = position.coords;
        
        try {
          const token = localStorage.getItem('token');
          const formData = new FormData();
          formData.append('event_id', this.event._id);
          formData.append('latitude', latitude);
          formData.append('longitude', longitude);
          if (imageBlob) {
            formData.append('image', imageBlob, 'checkout.jpg');
          }
          
          const response = await axios.post(`${API_BASE_URL}/attendance/checkout`, formData, {
            headers: { 
              Authorization: `Bearer ${token}`,
              'Content-Type': 'multipart/form-data'
            }
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
          // Reset camera state so user can try again
          this.resetCameraState();
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

/* Camera Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  position: relative;
}

.close-button {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-button:hover {
  background: #f3f4f6;
  color: #111827;
}

.modal-content h3 {
  color: var(--dark-green);
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
}

.modal-content p {
  color: #6b7280;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.scanning-text {
  color: var(--medium-green);
  font-weight: 600;
  font-size: 1.1rem;
}

.camera-container {
  position: relative;
  width: 100%;
  aspect-ratio: 4/3;
  background: #000;
  border-radius: 16px;
  overflow: hidden;
  margin: 1.5rem 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.camera-feed {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  /* Prevent layout shifts */
  position: absolute;
  top: 0;
  left: 0;
}

.camera-feed-hidden {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: none;
}

.face-guide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.guide-circle {
  width: 60%;
  height: 70%;
  border: 3px dashed rgba(16, 185, 129, 0.8);
  border-radius: 50%;
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    border-color: rgba(16, 185, 129, 0.6);
    transform: scale(1);
  }
  50% {
    border-color: rgba(16, 185, 129, 1);
    transform: scale(1.05);
  }
}

.scanning-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.4);
  /* Hardware acceleration */
  transform: translateZ(0);
  will-change: opacity, transform;
}

.countdown-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgba(16, 185, 129, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: scaleIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 0 40px rgba(16, 185, 129, 0.6);
  /* Hardware acceleration */
  transform: translateZ(0);
}

.countdown-number {
  font-size: 3rem;
  font-weight: 700;
  color: white;
  /* Smooth font rendering */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

@keyframes scaleIn {
  from {
    transform: scale(0) translateZ(0);
    opacity: 0;
  }
  to {
    transform: scale(1) translateZ(0);
    opacity: 1;
  }
}

.scanning-line {
  position: absolute;
  width: 80%;
  height: 3px;
  background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 1), transparent);
  animation: scan 2s linear infinite;
}

@keyframes scan {
  0% {
    top: 0;
  }
  100% {
    top: 100%;
  }
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 1rem;
}

.btn-primary, .btn-secondary {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
  flex: 1;
  max-width: 180px;
}

.btn-primary {
  background: var(--medium-green);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--dark-green);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #e5e7eb;
  color: #374151;
}

.btn-secondary:hover {
  background: #d1d5db;
}

/* Vue Transition Styles */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.modal-fade-enter-from {
  opacity: 0;
}

.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .modal-content {
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-fade-enter-from .modal-content {
  transform: scale(0.9) translateY(-20px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-from {
  transform: translateY(10px);
}

.text-fade-enter-active,
.text-fade-leave-active {
  transition: opacity 0.25s ease;
}

.text-fade-enter-from,
.text-fade-leave-to {
  opacity: 0;
}

/* Smooth scanning line animation with hardware acceleration */
.scanning-line {
  transform: translateZ(0);
  will-change: transform;
}
</style>
