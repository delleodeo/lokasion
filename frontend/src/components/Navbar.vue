<template>
  <nav class="navbar">
    <div class="navbar-content">
      <button class="hamburger-button show-mobile" @click="$emit('toggle-sidebar')" aria-label="Toggle navigation" title="Toggle navigation">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <path d="M4 6H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M4 12H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M4 18H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <div class="navbar-title">
        <h1>{{ pageTitle }}</h1>
      </div>
      <div class="user-profile">
        <div class="user-info">
          <div class="user-avatar">
            {{ initials }}
          </div>
          <div class="user-details">
            <p class="user-name">{{ userName }}</p>
            <p class="user-role">{{ roleName }}</p>
          </div>
        </div>
        <button @click="logout" class="logout-button" title="Sign out">
          <ArrowRightOnRectangleIcon class="button-icon" />
        </button>
      </div>
    </div>
  </nav>
</template>

<script>
import { ArrowRightOnRectangleIcon } from '@heroicons/vue/24/solid';
import { jwtDecode } from 'jwt-decode';

export default {
  name: 'Navbar',
  components: {
    ArrowRightOnRectangleIcon
  },
  emits: ['toggle-sidebar'],
  data() {
    return {
      userName: 'User',
      userRole: '',
      pageTitle: 'Dashboard'
    };
  },
  computed: {
    initials() {
      return this.userName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    },
    roleName() {
      const roleMap = {
        student: 'Student',
        teacher: 'Teacher',
        admin: 'Administrator'
      };
      return roleMap[this.userRole] || 'User';
    }
  },
  created() {
    const token = localStorage.getItem('token');
    if (token) {
      const decodedToken = jwtDecode(token);
      this.userName = decodedToken.name;
      this.userRole = decodedToken.role;
    }
    this.updatePageTitle();
  },
  watch: {
    '$route'() {
      this.updatePageTitle();
    }
  },
  methods: {
    updatePageTitle() {
      const routeNames = {
        '/events': 'Events',
        '/attendance': 'My Attendance',
        '/admin': 'Admin Panel',
        '/create-event': 'Create Event',
        '/dashboard': 'Dashboard'
      };
      this.pageTitle = routeNames[this.$route.path] || 'Dashboard';
    },
    logout() {
      localStorage.removeItem('token');
      this.$router.push('/login');
    }
  }
}
</script>

<style scoped>
.navbar {
  background: white;
  border-bottom: 1px solid var(--gray-200);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.navbar-content {
  padding: 1.25rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 100%;
}

.hamburger-button {
  display: none;
  background: none;
  border: none;
  padding: 0.5rem;
  margin-right: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  color: var(--gray-800);
}

.hamburger-button:focus {
  outline: none;
  box-shadow: 0 0 0 4px rgba(11,110,253,0.12);
}

.navbar-title h1 {
  font-size: 1.5rem;
  color: var(--dark-green);
  margin: 0;
  font-weight: 700;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-avatar {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #198754, #0F5132);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.user-details {
  text-align: right;
}

.user-name {
  margin: 0;
  font-weight: 600;
  color: var(--gray-800);
  font-size: 0.95rem;
}

.user-role {
  margin: 0;
  color: var(--gray-600);
  font-size: 0.85rem;
}

.logout-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: var(--transition);
  color: var(--gray-600);
}

.logout-button:hover {
  background-color: var(--gray-100);
  color: var(--dark-green);
}

.button-icon {
  width: 22px;
  height: 22px;
}

@media (max-width: 768px) {
  .navbar-content {
    padding: 1rem 1rem;
  }

  .navbar-title h1 {
    font-size: 1.25rem;
  }

  .user-details {
    display: none;
  }
  .hamburger-button { display: inline-flex; }
}
</style>
