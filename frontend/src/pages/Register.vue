<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-header">
        <h1>Create Account</h1>
        <p>Join our attendance system</p>
      </div>

      <form @submit.prevent="register" class="register-form">
        <div class="input-group">
          <label for="firstName">First Name</label>
          <div class="input-wrapper">
            <UserIcon class="input-icon" />
            <input 
              type="text" 
              id="firstName" 
              v-model="firstName" 
              placeholder="John"
              required
            >
          </div>
        </div>

        <div class="input-group">
          <label for="middleName">Middle Name (Optional)</label>
          <div class="input-wrapper">
            <UserIcon class="input-icon" />
            <input 
              type="text" 
              id="middleName" 
              v-model="middleName" 
              placeholder="Smith"
            >
          </div>
        </div>

        <div class="input-group">
          <label for="lastName">Last Name</label>
          <div class="input-wrapper">
            <UserIcon class="input-icon" />
            <input 
              type="text" 
              id="lastName" 
              v-model="lastName" 
              placeholder="Doe"
              required
            >
          </div>
        </div>

        <div class="input-group">
          <label for="idNumber">ID Number</label>
          <div class="input-wrapper">
            <UserIcon class="input-icon" />
            <input 
              type="text" 
              id="idNumber" 
              v-model="idNumber" 
              placeholder="2021-12345"
              required
            >
          </div>
        </div>

        <div class="input-group">
          <label for="email">Email Address</label>
          <div class="input-wrapper">
            <EnvelopeIcon class="input-icon" />
            <input 
              type="email" 
              id="email" 
              v-model="email" 
              placeholder="you@example.com"
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
              required
            >
          </div>
        </div>

        <div class="input-group">
          <label for="role">Role</label>
          <div class="input-wrapper">
            <BriefcaseIcon class="input-icon" />
            <select id="role" v-model="role" class="role-select">
              <option value="student">Student</option>
              <option value="teacher">Teacher</option>
              <option value="admin">Administrator</option>
            </select>
          </div>
        </div>

        <Transition name="fade">
          <div v-if="role === 'admin'" class="input-group admin-code-field">
            <label for="adminCode">Admin Secret Code</label>
            <div class="input-wrapper">
              <LockClosedIcon class="input-icon" />
              <input 
                type="password" 
                id="adminCode" 
                v-model="adminSecretCode" 
                placeholder="Enter admin secret code"
                required
              >
            </div>
            <small class="input-hint">Required for administrator registration</small>
          </div>
        </Transition>

        <button type="submit" class="register-button">Create Account</button>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </form>

      <p class="login-link">
        Already have an account? 
        <router-link to="/login" class="link-accent">Sign in</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../config.js';
import { UserIcon, EnvelopeIcon, LockClosedIcon, BriefcaseIcon } from '@heroicons/vue/24/solid';

export default {
  name: 'Register',
  components: {
    UserIcon,
    EnvelopeIcon,
    LockClosedIcon,
    BriefcaseIcon
  },
  data() {
    return {
      firstName: '',
      middleName: '',
      lastName: '',
      idNumber: '',
      email: '',
      password: '',
      role: 'student',
      adminSecretCode: '',
      error: ''
    };
  },
  methods: {
    async register() {
      try {
        this.error = '';
        
        // Validate admin secret code if role is admin
        if (this.role === 'admin' && !this.adminSecretCode) {
          this.error = 'Admin secret code is required for administrator registration';
          return;
        }
        
        // Combine names for backward compatibility
        const nameParts = [this.firstName, this.middleName, this.lastName].filter(Boolean);
        const fullName = nameParts.join(' ');
        
        console.log('Registering with data:', {
          first_name: this.firstName,
          middle_name: this.middleName,
          last_name: this.lastName,
          id_number: this.idNumber,
          name: fullName,
          email: this.email,
          role: this.role
        });
        
        const payload = {
          first_name: this.firstName,
          middle_name: this.middleName || null,
          last_name: this.lastName,
          id_number: this.idNumber,
          name: fullName,
          email: this.email,
          password: this.password,
          role: this.role,
          department_id: null
        };

        // Add admin secret code if role is admin
        if (this.role === 'admin') {
          payload.admin_secret_code = this.adminSecretCode;
        }
        
        const response = await axios.post(`${API_BASE_URL}/auth/register`, payload);
        
        console.log('Registration successful:', response.data);
        alert(`Account created successfully as ${this.role}!`);
        this.$router.push('/login');
      } catch (error) {
        this.error = error.response?.data?.detail || 'Registration failed. Please try again.';
        console.error('Registration failed:', error.response?.data || error);
      }
    }
  }
}
</script>

<style scoped>
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0F5132 0%, #198754 100%);
  padding: 2rem;
}

.register-container {
  padding: 3rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.15);
  width: 100%;
  max-width: 450px;
}

.register-header {
  text-align: center;
  margin-bottom: 2rem;
}

.register-header h1 {
  font-size: 1.75rem;
  color: var(--dark-green);
  margin-bottom: 0.5rem;
}

.register-header p {
  color: var(--gray-600);
  font-size: 0.95rem;
}

.register-form {
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

.input-hint {
  color: var(--gray-600);
  font-size: 0.85rem;
  margin-top: 0.25rem;
  font-style: italic;
}

.admin-code-field {
  background: #fff3cd;
  padding: 1rem;
  border-radius: 8px;
  border: 2px solid #ffc107;
}

.admin-code-field label {
  color: #856404;
}

.admin-code-field .input-hint {
  color: #856404;
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

.register-form input,
.register-form select {
  width: 100%;
  padding: 0.875rem 0.875rem 0.875rem 2.5rem;
  border: 2px solid var(--gray-200);
  border-radius: 8px;
  font-size: 1rem;
  transition: var(--transition);
  background: var(--gray-50);
}

.register-form input:focus,
.register-form select:focus {
  outline: none;
  border-color: var(--medium-green);
  background: white;
  box-shadow: 0 0 0 3px rgba(25, 135, 84, 0.1);
}

.role-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23198754' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 2.5rem;
}

.register-button {
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
  margin-top: 0.5rem;
  box-shadow: 0 4px 12px rgba(25, 135, 84, 0.3);
}

.register-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(25, 135, 84, 0.4);
}

.register-button:active {
  transform: translateY(0);
}

.login-link {
  text-align: center;
  color: var(--gray-600);
  font-size: 0.95rem;
  margin-top: 1rem;
}

.link-accent {
  color: var(--medium-green);
  font-weight: 600;
}

.error-message {
  padding: 1rem;
  background: #F8D7DA;
  color: #842029;
  border: 1px solid #F5C2C7;
  border-radius: 8px;
  margin-top: 1rem;
  font-size: 0.95rem;
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

/* Vue Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@media (max-width: 768px) {
  .register-container {
    padding: 2rem;
  }

  .register-header h1 {
    font-size: 1.5rem;
  }
}
</style>
