<template>
  <div class="profile-page">
    <div class="profile-header">
      <div class="avatar">
        <UserCircleIcon class="avatar-icon" />
      </div>
      <h1>{{ isEditing ? 'Edit Profile' : 'My Profile' }}</h1>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading profile...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="loadProfile" class="btn-primary">Retry</button>
    </div>

    <div v-else class="profile-content">
      <!-- Profile Information Card -->
      <div class="profile-card">
        <div class="card-header">
          <h2>Personal Information</h2>
          <button v-if="!isEditing" @click="startEditing" class="btn-edit">
            <PencilIcon class="icon" />
            Edit Profile
          </button>
        </div>

        <form @submit.prevent="saveProfile" class="profile-form">
          <div class="form-grid">
            <div class="form-group">
              <label>First Name</label>
              <input 
                v-model="formData.first_name" 
                type="text" 
                :disabled="!isEditing"
                required
              />
            </div>

            <div class="form-group">
              <label>Middle Name</label>
              <input 
                v-model="formData.middle_name" 
                type="text" 
                :disabled="!isEditing"
              />
            </div>

            <div class="form-group">
              <label>Last Name</label>
              <input 
                v-model="formData.last_name" 
                type="text" 
                :disabled="!isEditing"
                required
              />
            </div>

            <div class="form-group">
              <label>ID Number</label>
              <input 
                v-model="formData.id_number" 
                type="text" 
                :disabled="!isEditing"
                required
              />
            </div>

            <div class="form-group">
              <label>Email</label>
              <input 
                v-model="formData.email" 
                type="email" 
                :disabled="!isEditing"
                required
              />
            </div>

            <div class="form-group">
              <label>Role</label>
              <input 
                :value="profile.role" 
                type="text" 
                disabled
                class="readonly"
              />
            </div>

            <div class="form-group" v-if="profile.department_id">
              <label>Department</label>
              <input 
                :value="departmentName" 
                type="text" 
                disabled
                class="readonly"
              />
            </div>

            <div class="form-group full-width" v-if="isEditing">
              <label>New Password (leave blank to keep current)</label>
              <input 
                v-model="formData.password" 
                type="password" 
                placeholder="Enter new password"
              />
            </div>
          </div>

          <div class="form-actions" v-if="isEditing">
            <button type="button" @click="cancelEditing" class="btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="saving">
              <span v-if="saving">Saving...</span>
              <span v-else>Save Changes</span>
            </button>
          </div>
        </form>
      </div>

      <!-- Face Registration Status -->
      <div class="profile-card">
        <div class="card-header">
          <h2>Face Recognition</h2>
        </div>
        <div class="face-status">
          <div v-if="profile.has_face_registered" class="status-badge success">
            <CheckCircleIcon class="icon" />
            Face Registered
          </div>
          <div v-else class="status-badge warning">
            <ExclamationCircleIcon class="icon" />
            Face Not Registered
          </div>
          <button 
            v-if="!profile.has_face_registered" 
            @click="goToFaceRegistration" 
            class="btn-primary"
          >
            Register Face
          </button>
        </div>
      </div>

      <!-- Success Message -->
      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { UserCircleIcon, PencilIcon, CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/vue/24/outline';

export default {
  name: 'Profile',
  components: {
    UserCircleIcon,
    PencilIcon,
    CheckCircleIcon,
    ExclamationCircleIcon
  },
  data() {
    return {
      profile: null,
      formData: {
        first_name: '',
        middle_name: '',
        last_name: '',
        id_number: '',
        email: '',
        password: ''
      },
      isEditing: false,
      loading: true,
      saving: false,
      error: null,
      successMessage: '',
      departmentName: ''
    };
  },
  async mounted() {
    await this.loadProfile();
  },
  methods: {
    async loadProfile() {
      this.loading = true;
      this.error = null;
      
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        this.profile = response.data;
        this.formData = {
          first_name: response.data.first_name || '',
          middle_name: response.data.middle_name || '',
          last_name: response.data.last_name || '',
          id_number: response.data.id_number || '',
          email: response.data.email || '',
          password: ''
        };

        // Load department name if exists
        if (response.data.department_id) {
          await this.loadDepartment(response.data.department_id);
        }
        
      } catch (error) {
        console.error('Failed to load profile:', error);
        this.error = error.response?.data?.detail || 'Failed to load profile';
      } finally {
        this.loading = false;
      }
    },

    async loadDepartment(departmentId) {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/departments`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const department = response.data.find(d => d._id === departmentId);
        this.departmentName = department?.name || 'Unknown Department';
      } catch (error) {
        console.error('Failed to load department:', error);
        this.departmentName = 'Unknown Department';
      }
    },

    startEditing() {
      this.isEditing = true;
      this.successMessage = '';
    },

    cancelEditing() {
      this.isEditing = false;
      this.formData = {
        first_name: this.profile.first_name || '',
        middle_name: this.profile.middle_name || '',
        last_name: this.profile.last_name || '',
        id_number: this.profile.id_number || '',
        email: this.profile.email || '',
        password: ''
      };
    },

    async saveProfile() {
      this.saving = true;
      this.error = null;
      this.successMessage = '';

      try {
        const token = localStorage.getItem('token');
        const updateData = {
          first_name: this.formData.first_name,
          middle_name: this.formData.middle_name,
          last_name: this.formData.last_name,
          id_number: this.formData.id_number,
          email: this.formData.email
        };

        // Only include password if it's been changed
        if (this.formData.password) {
          updateData.password = this.formData.password;
        }

        const response = await axios.put(
          `${API_BASE_URL}/auth/profile`,
          updateData,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        this.profile = response.data.user;
        this.isEditing = false;
        this.successMessage = 'Profile updated successfully!';
        this.formData.password = '';

        // Hide success message after 3 seconds
        setTimeout(() => {
          this.successMessage = '';
        }, 3000);

      } catch (error) {
        console.error('Failed to update profile:', error);
        this.error = error.response?.data?.detail || 'Failed to update profile';
      } finally {
        this.saving = false;
      }
    },

    goToFaceRegistration() {
      this.$router.push('/face-registration');
    }
  }
};
</script>

<style scoped>
.profile-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.profile-header {
  text-align: center;
  margin-bottom: 2rem;
}

.avatar {
  width: 120px;
  height: 120px;
  margin: 0 auto 1rem;
  background: var(--light-green);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-icon {
  width: 80px;
  height: 80px;
  color: var(--medium-green);
}

.profile-header h1 {
  font-size: 2rem;
  color: var(--dark-green);
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

.success-message {
  background: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
  text-align: center;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.profile-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--light-green);
}

.card-header h2 {
  font-size: 1.5rem;
  color: var(--dark-green);
  margin: 0;
}

.btn-edit {
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

.btn-edit:hover {
  background: var(--dark-green);
  transform: translateY(-2px);
}

.btn-edit .icon {
  width: 18px;
  height: 18px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-weight: 600;
  color: var(--dark-green);
  margin-bottom: 0.5rem;
}

.form-group input {
  padding: 0.75rem;
  border: 2px solid var(--gray-300);
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: var(--medium-green);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.form-group input:disabled {
  background: var(--gray-100);
  cursor: not-allowed;
}

.form-group input.readonly {
  background: var(--light-green);
  color: var(--dark-green);
  font-weight: 600;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1.5rem;
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
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: var(--gray-200);
  color: var(--gray-700);
}

.btn-secondary:hover {
  background: var(--gray-300);
}

.face-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
}

.status-badge.success {
  background: #d4edda;
  color: #155724;
}

.status-badge.warning {
  background: #fff3cd;
  color: #856404;
}

.status-badge .icon {
  width: 24px;
  height: 24px;
}

@media (max-width: 768px) {
  .profile-page {
    padding: 1rem;
  }

  .form-grid {
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
