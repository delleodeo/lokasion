<template>
  <aside :class="['sidebar', { open: mobileOpen }]">
    <div class="sidebar-header">
      <button class="sidebar-close show-mobile" @click="$emit('request-close')" aria-label="Close navigation" title="Close navigation">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <path d="M6 18L18 6M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <div class="logo-badge">
        <MapPinIcon class="logo-icon" />
      </div>
      <h2>Attendance</h2>
    </div>

    <nav class="navigation" @click="hideOnMobile">
      <ul>
        <li>
          <!-- Dashboard should appear active when we are anywhere in the dashboard area -->
          <router-link
            to="/dashboard"
            class="nav-link"
            :class="{ 'router-link-active': isDashboardActive }"
          >
            <HomeIcon class="nav-icon" />
            <span>Dashboard</span>
          </router-link>
        </li>
        <!-- Student & Teacher -->
        <li v-if="userRole === 'student' || userRole === 'teacher'">
          <router-link to="/societies" class="nav-link" active-class="" exact-active-class="router-link-active">
            <BuildingLibraryIcon class="nav-icon" />
            <span>Societies</span>
          </router-link>
        </li>
        <!-- Student & Teacher -->
        <li v-if="userRole === 'student' || userRole === 'teacher'">
          <router-link to="/events" class="nav-link" active-class="" exact-active-class="router-link-active">
            <CalendarIcon class="nav-icon" />
            <span>Events</span>
          </router-link>
        </li>
        <!-- Student -->
        <li v-if="userRole === 'student'">
          <router-link to="/attendance" class="nav-link" active-class="" exact-active-class="router-link-active">
            <ClockIcon class="nav-icon" />
            <span>My Attendance</span>
          </router-link>
        </li>
        <!-- Teacher -->
        <li v-if="userRole === 'teacher'">
          <router-link to="/create-event" class="nav-link" active-class="" exact-active-class="router-link-active">
            <PlusCircleIcon class="nav-icon" />
            <span>Create Event</span>
          </router-link>
        </li>
        <li v-if="userRole === 'teacher'">
          <router-link to="/teacher-events" class="nav-link" active-class="" exact-active-class="router-link-active">
            <CalendarIcon class="nav-icon" />
            <span>My Events</span>
          </router-link>
        </li>
        <li v-if="userRole === 'teacher'">
          <router-link to="/enrollments" class="nav-link" active-class="" exact-active-class="router-link-active">
            <ClipboardDocumentCheckIcon class="nav-icon" />
            <span>Enrollments</span>
          </router-link>
        </li>
         <!-- Admin -->
        <li v-if="userRole === 'admin'">
          <router-link to="/admin" class="nav-link" active-class="" exact-active-class="router-link-active">
            <Cog6ToothIcon class="nav-icon" />
            <span>Admin Panel</span>
          </router-link>
        </li>
        <li v-if="userRole === 'admin'">
          <router-link to="/teacher-enrollments" class="nav-link" active-class="" exact-active-class="router-link-active">
            <UserGroupIcon class="nav-icon" />
            <span>Teacher Requests</span>
          </router-link>
        </li>
        <li v-if="userRole === 'admin'">
          <router-link to="/user-management" class="nav-link" active-class="" exact-active-class="router-link-active">
            <UsersIcon class="nav-icon" />
            <span>User Management</span>
          </router-link>
        </li>
        <!-- All Users -->
        <li>
          <router-link to="/profile" class="nav-link" active-class="" exact-active-class="router-link-active">
            <UserCircleIcon class="nav-icon" />
            <span>My Profile</span>
          </router-link>
        </li>
      </ul>
    </nav>

    <div class="sidebar-footer">
      <div class="role-badge">
        <span>{{ roleName }}</span>
      </div>
    </div>
  </aside>
</template>

<script>
import { HomeIcon, CalendarIcon, ClockIcon, Cog6ToothIcon, PlusCircleIcon, MapPinIcon, BuildingLibraryIcon, ClipboardDocumentCheckIcon, UserGroupIcon, UserCircleIcon } from '@heroicons/vue/24/solid';
import { UsersIcon } from '@heroicons/vue/24/outline';
import { jwtDecode } from 'jwt-decode';

export default {
  name: 'Sidebar',
  components: {
    HomeIcon,
    CalendarIcon,
    ClockIcon,
    Cog6ToothIcon,
    PlusCircleIcon,
    MapPinIcon,
    BuildingLibraryIcon,
    ClipboardDocumentCheckIcon,
    UserGroupIcon,
    UserCircleIcon,
    UsersIcon
  },
  props: ['mobileOpen'],
  emits: ['request-close'],
  data() {
    return {
      userRole: ''
    };
  },
  computed: {
    isDashboardActive() {
      // Active when user is exactly on /dashboard or when the current route has been marked as part of the dashboard
      const path = this.$route.path;
      if (path === '/dashboard') return true;
      return !!(this.$route.meta && this.$route.meta.inDashboard);
    }
  },
  computed: {
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
      this.userRole = decodedToken.role;
    }
  },

  methods: {
    hideOnMobile() {
      // Only request close for narrow screens — keep desktop unchanged
      if (window.innerWidth <= 768) {
        this.$emit('request-close');
      }
    }
  }
}
</script>

<style scoped>
.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #0F5132 0%, #097043 100%);
  color: white;
  display: flex;
  flex-direction: column;
  height: 100vh;
  box-shadow: 4px 0 12px rgba(0, 0, 0, 0.15);
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: -100%;
    top: 0;
    z-index: 1000;
    transition: left 0.3s ease;
  }

  .sidebar.open {
    left: 0;
  }

  .sidebar-close {
    display: block !important;
  }
}

.sidebar-header {
  padding: 2rem 1.5rem;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-close {
  display: none;
  position: absolute;
  left: 12px;
  top: 12px;
  background: none;
  border: none;
  color: white;
  padding: 0.5rem;
  border-radius: 8px;
}

.sidebar-close svg { width: 18px; height: 18px; }

.logo-badge {
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
}

.logo-icon {
  width: 32px;
  height: 32px;
  color: white;
}

.sidebar-header h2 {
  font-size: 1.5rem;
  margin: 0;
  font-weight: 700;
}

.navigation {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
}

.navigation ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: var(--transition);
  position: relative;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-link span {
  margin-left: 0.75rem;
}

@media (max-width: 768px) {
  .nav-link {
    padding: 0.875rem 1.25rem;
  }
  
  .nav-link span {
    display: inline;
    font-size: 0.95rem;
  }
}

.router-link-active {
  background-color: rgba(255, 255, 255, 0.15);
  color: white;
  border-left: 3px solid white;
  padding-left: calc(1.5rem - 3px);
}

.nav-icon {
  width: 22px;
  height: 22px;
  margin-right: 1rem;
  flex-shrink: 0;
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.role-badge {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  padding: 0.75rem;
  text-align: center;
  font-size: 0.875rem;
  font-weight: 600;
  color: white;
}

/* overlay that'll be controlled by the dashboard parent when sidebar is open */
.sidebar-backdrop {
  display: none;
}

@media (max-width: 768px) {
  .sidebar-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.35);
    z-index: 50;
    display: none; /* parent should toggle */
  }
  .sidebar-backdrop.show { display: block; }
}
</style>
