<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <div class="logo-circle">
          <CheckBadgeIcon class="logo-icon" />
        </div>
        <h1>Attendance</h1>
        <p>Location-Based Check-in System</p>
      </div>
      
      <form @submit.prevent="login" class="login-form">
        <div class="input-group">
          <label for="email">Email Address</label>
          <div class="input-wrapper">
            <EnvelopeIcon class="input-icon" />
            <input 
              type="email" 
              id="email" 
              v-model="email" 
              placeholder="you@example.com"
              autocomplete="email"
              required
            >
          </div>
        </div>

        <div class="input-group">
          <label for="password">Password</label>
          <div class="input-wrapper">
            <LockClosedIcon class="input-icon" />
            <input 
              type="password" 
              id="password" 
              v-model="password" 
              placeholder="••••••••"
              autocomplete="current-password"
              required
            >
          </div>
        </div>

        <button type="submit" class="login-button">
          <span>Sign In</span>
          <ArrowRightIcon class="button-icon" />
        </button>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </form>

      <div class="divider">or</div>

      <p class="register-link">
        Don't have an account? 
        <router-link to="/register" class="link-accent">Create one</router-link>
      </p>
    </div>

    <div class="login-side">
      <div class="side-content">
        <h2>Welcome Back</h2>
        <p>Track attendance with precision using real-time location technology</p>
        <ul class="features">
          <li><CheckIcon class="check-icon" /> Real-time GPS tracking</li>
          <li><CheckIcon class="check-icon" /> Automatic attendance marking</li>
          <li><CheckIcon class="check-icon" /> Role-based access control</li>
          <li><CheckIcon class="check-icon" /> Detailed attendance reports</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../config.js';
import { CheckBadgeIcon, EnvelopeIcon, LockClosedIcon, ArrowRightIcon, CheckIcon } from '@heroicons/vue/24/solid';

export default {
  name: 'Login',
  components: {
    CheckBadgeIcon,
    EnvelopeIcon,
    LockClosedIcon,
    ArrowRightIcon,
    CheckIcon
  },
  data() {
    return {
      email: '',
      password: '',
      error: ''
    };
  },
  methods: {
    async login() {
      try {
        this.error = '';
        const response = await axios.post(`${API_BASE_URL}/auth/login`, {
          email: this.email,
          password: this.password
        });
        localStorage.setItem('token', response.data.access_token);
        this.$router.push('/dashboard');
      } catch (error) {
        this.error = 'Invalid email or password';
        console.error('Login failed:', error);
      }
    }
  }
}
</script>

<style scoped>
.login-page {
  display: grid;
  grid-template-columns: 1fr 1fr;
  height: 100vh;
  background: linear-gradient(135deg, #0F5132 0%, #198754 100%);
}

.login-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 3rem;
  background: white;
}

.login-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.logo-circle {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #198754, #0F5132);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  box-shadow: 0 4px 15px rgba(25, 135, 84, 0.3);
}

.logo-icon {
  width: 48px;
  height: 48px;
  color: white;
}

.login-header h1 {
  font-size: 2rem;
  color: var(--dark-green);
  margin-bottom: 0.5rem;
}

.login-header p {
  color: var(--gray-600);
  font-size: 0.95rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-group label {
  font-weight: 600;
  color: var(--gray-800);
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  width: 20px;
  height: 20px;
  color: var(--medium-green);
  pointer-events: none;
}

.input-group input {
  width: 100%;
  padding: 0.875rem 0.875rem 0.875rem 2.5rem;
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

.login-button {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #198754, #0F5132);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  box-shadow: 0 4px 12px rgba(25, 135, 84, 0.3);
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(25, 135, 84, 0.4);
}

.login-button:active {
  transform: translateY(0);
}

.button-icon {
  width: 20px;
  height: 20px;
}

.error-message {
  margin-top: 1rem;
  padding: 0.875rem;
  background: #F8D7DA;
  color: #842029;
  border: 2px solid #F5C2C7;
  border-radius: 8px;
  font-weight: 500;
  text-align: center;
  animation: slideIn 0.3s ease-out;
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

.divider {
  text-align: center;
  margin: 1.5rem 0;
  color: var(--gray-300);
  font-weight: 500;
}

.register-link {
  text-align: center;
  color: var(--gray-600);
  font-size: 0.95rem;
}

.link-accent {
  color: var(--medium-green);
  font-weight: 600;
}

.login-side {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background: linear-gradient(135deg, #0F5132 0%, #198754 100%);
  color: white;
}

.side-content h2 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.side-content p {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 2rem;
}

.features {
  list-style: none;
}

.features li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  font-size: 1rem;
  opacity: 0.95;
}

.check-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .login-page {
    grid-template-columns: 1fr;
  }

  .login-side {
    display: none;
  }

  .login-container {
    padding: 2rem;
    justify-content: flex-start;
    padding-top: 4rem;
  }

  .login-header h1 {
    font-size: 1.75rem;
  }
}
</style>
