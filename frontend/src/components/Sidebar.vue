<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="logo-badge">
        <MapPinIcon class="logo-icon" />
      </div>
      <h2>Attendance</h2>
    </div>

    <nav class="navigation">
      <ul>
        <li>
          <router-link to="/dashboard" class="nav-link">
            <HomeIcon class="nav-icon" />
            <span>Dashboard</span>
          </router-link>
        </li>
        <!-- Student & Teacher -->
        <li v-if="userRole === 'student' || userRole === 'teacher'">
          <router-link to="/societies" class="nav-link">
            <BuildingLibraryIcon class="nav-icon" />
            <span>Societies</span>
          </router-link>
        </li>
        <!-- Student & Teacher -->
        <li v-if="userRole === 'student' || userRole === 'teacher'">
          <router-link to="/events" class="nav-link">
            <CalendarIcon class="nav-icon" />
            <span>Events</span>
          </router-link>
        </li>
        <!-- Student -->
        <li v-if="userRole === 'student'">
          <router-link to="/attendance" class="nav-link">
            <ClockIcon class="nav-icon" />
            <span>My Attendance</span>
          </router-link>
        </li>
        <!-- Teacher -->
        <li v-if="userRole === 'teacher'">
          <router-link to="/create-event" class="nav-link">
            <PlusCircleIcon class="nav-icon" />
            <span>Create Event</span>
          </router-link>
        </li>
        <li v-if="userRole === 'teacher'">
          <router-link to="/teacher-events" class="nav-link">
            <CalendarIcon class="nav-icon" />
            <span>My Events</span>
          </router-link>
        </li>
        <li v-if="userRole === 'teacher'">
          <router-link to="/enrollments" class="nav-link">
            <ClipboardDocumentCheckIcon class="nav-icon" />
            <span>Enrollments</span>
          </router-link>
        </li>
         <!-- Admin -->
        <li v-if="userRole === 'admin'">
          <router-link to="/admin" class="nav-link">
            <Cog6ToothIcon class="nav-icon" />
            <span>Admin Panel</span>
          </router-link>
        </li>
        <li v-if="userRole === 'admin'">
          <router-link to="/teacher-enrollments" class="nav-link">
            <UserGroupIcon class="nav-icon" />
            <span>Teacher Requests</span>
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
import { HomeIcon, CalendarIcon, ClockIcon, Cog6ToothIcon, PlusCircleIcon, MapPinIcon, BuildingLibraryIcon, ClipboardDocumentCheckIcon, UserGroupIcon } from '@heroicons/vue/24/solid';
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
    UserGroupIcon
  },
  data() {
    return {
      userRole: ''
    };
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

.sidebar-header {
  padding: 2rem 1.5rem;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

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

@media (max-width: 768px) {
  .sidebar {
    width: 70px;
  }

  .sidebar-header h2 {
    display: none;
  }

  .nav-link {
    padding: 1rem;
    justify-content: center;
  }

  .nav-link span {
    display: none;
  }

  .nav-icon {
    margin-right: 0;
  }
}
</style>
