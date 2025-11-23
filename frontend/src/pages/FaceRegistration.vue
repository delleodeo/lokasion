<template>
  <div class="face-registration-page">
    <div class="registration-card">
      <div class="header">
        <h2>Face Registration</h2>
        <Transition name="text-fade" mode="out-in">
          <p v-if="!isCapturing" key="instruction">Position your face within the circle</p>
          <p v-else key="scanning" class="scanning-text">{{ scanningMessage }}</p>
        </Transition>
      </div>

      <div class="camera-container">
        <video ref="video" autoplay playsinline muted class="camera-feed"></video>
        <canvas ref="canvas" class="camera-feed-hidden"></canvas>
        
        <Transition name="fade">
          <div v-if="!isCapturing && !capturedImage" class="camera-overlay" key="guide">
            <div class="face-guide"></div>
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

      <div class="actions">
        <Transition name="fade" mode="out-in">
          <button 
            v-if="!capturedImage && !isCapturing" 
            @click="startAutoCapture" 
            class="btn-primary" 
            :disabled="!cameraReady"
            key="start"
          >
            <span class="icon">📸</span> 
            <span v-if="cameraReady">Start Scanning</span>
            <span v-else>Loading Camera...</span>
          </button>
          <div v-else-if="capturedImage" class="action-buttons" key="captured">
            <button @click="retakeImage" class="btn-secondary">
              <span class="icon">🔄</span> Retake
            </button>
            <button @click="registerFace" class="btn-primary" :disabled="loading">
              <span class="icon" v-if="!loading">✅</span>
              <span v-else class="spinner"></span>
              {{ loading ? 'Registering...' : 'Confirm & Register' }}
            </button>
          </div>
        </Transition>
      </div>

      <Transition name="fade">
        <div v-if="message" :class="['message', messageType]">
          {{ message }}
        </div>
      </Transition>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../config.js';

export default {
  name: 'FaceRegistration',
  data() {
    return {
      stream: null,
      capturedImage: null,
      loading: false,
      message: '',
      messageType: '',
      cameraReady: false,
      isCapturing: false,
      countdown: 3,
      countdownInterval: null,
      scanningMessage: 'Initializing...'
    };
  },
  async mounted() {
    await this.startCamera();
  },
  beforeUnmount() {
    this.stopCamera();
    if (this.countdownInterval) {
      clearInterval(this.countdownInterval);
    }
  },
  methods: {
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
        this.message = 'Could not access camera. Please allow camera access.';
        this.messageType = 'error';
      }
    },
    stopCamera() {
      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop());
        this.stream = null;
      }
    },
    startAutoCapture() {
      if (!this.cameraReady || this.isCapturing) return;
      
      this.isCapturing = true;
      this.countdown = 3;
      this.scanningMessage = 'Get ready...';
      
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
            
            requestAnimationFrame(() => {
              setTimeout(() => {
                this.captureImage();
              }, 300);
            });
          }
        }
      }, 100);
    },
    captureImage() {
      try {
        const video = this.$refs.video;
        const canvas = this.$refs.canvas;
        
        if (!video) {
          this.resetCameraState();
          return;
        }
        
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        this.capturedImage = canvas.toDataURL('image/jpeg');
        this.isCapturing = false;
        this.countdown = 3;
      } catch (error) {
        console.error('Error capturing image:', error);
        this.message = 'Failed to capture image. Please try again.';
        this.messageType = 'error';
        this.resetCameraState();
      }
    },
    resetCameraState() {
      if (this.countdownInterval) {
        clearInterval(this.countdownInterval);
        this.countdownInterval = null;
      }
      this.isCapturing = false;
      this.countdown = 3;
      this.scanningMessage = 'Initializing...';
    },
    retakeImage() {
      this.capturedImage = null;
      this.message = '';
      this.resetCameraState();
    },
    async registerFace() {
      if (!this.capturedImage) return;
      
      this.loading = true;
      this.message = '';
      
      try {
        // Convert base64 to blob
        const res = await fetch(this.capturedImage);
        const blob = await res.blob();
        
        const formData = new FormData();
        formData.append('file', blob, 'face.jpg');
        
        const token = localStorage.getItem('token');
        await axios.post(`${API_BASE_URL}/auth/register-face`, formData, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        });
        
        this.message = 'Face registered successfully!';
        this.messageType = 'success';
        
        setTimeout(() => {
          this.$router.push('/dashboard');
        }, 2000);
        
      } catch (error) {
        console.error('Error registering face:', error);
        this.message = error.response?.data?.detail || 'Failed to register face';
        this.messageType = 'error';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.face-registration-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  padding: 2rem;
}

.registration-card {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  text-align: center;
}

.header h2 {
  color: var(--dark-green);
  margin-bottom: 0.5rem;
}

.header p {
  color: var(--gray-600);
  margin-bottom: 2rem;
  min-height: 1.5rem;
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
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 2rem;
  transform: translateZ(0);
  will-change: transform;
}

.camera-feed {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
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

.camera-overlay {
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

.face-guide {
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
  transform: translateZ(0);
}

.countdown-number {
  font-size: 3rem;
  font-weight: 700;
  color: white;
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
  transform: translateZ(0);
  will-change: transform;
}

@keyframes scan {
  0% {
    top: 0;
  }
  100% {
    top: 100%;
  }
}

.actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  width: 100%;
}

.btn-primary, .btn-secondary {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  flex: 1;
}

.btn-primary {
  background: var(--medium-green);
  color: white;
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background: var(--dark-green);
}

.btn-secondary {
  background: white;
  color: var(--gray-600);
  border: 2px solid var(--gray-200);
}

.btn-secondary:hover {
  border-color: var(--gray-400);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.message {
  margin-top: 1.5rem;
  padding: 1rem;
  border-radius: 8px;
  font-weight: 500;
}

.message.success {
  background: #d1e7dd;
  color: #0f5132;
}

.message.error {
  background: #f8d7da;
  color: #842029;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Vue Transition Styles */
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
</style>
