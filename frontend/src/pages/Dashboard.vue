<template>
  <div class="dashboard-layout">
    <Sidebar :mobile-open="mobileSidebarOpen" @request-close="closeSidebar" />
    <div :class="['sidebar-backdrop', { show: mobileSidebarOpen }]" @click="closeSidebar" aria-hidden="true"></div>
    <div class="main-content" :aria-hidden="mobileSidebarOpen ? 'true' : 'false'">
      <Navbar @toggle-sidebar="toggleSidebar" />
      <main class="content-body">
        <div class="content-wrapper">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import Sidebar from '../components/Sidebar.vue';
import Navbar from '../components/Navbar.vue';

export default {
  name: 'Dashboard',
  components: {
    Sidebar,
    Navbar
  },
  data() {
    return {
      mobileSidebarOpen: false
    };
  },
  methods: {
    toggleSidebar() {
      this.mobileSidebarOpen = !this.mobileSidebarOpen;
    },
    closeSidebar() {
      this.mobileSidebarOpen = false;
    }
  }
}
</script>

<style scoped>
  .dashboard-layout {
  display: flex;
  height: 100vh;
}

.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-body {
  flex-grow: 1;
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafb 0%, #E9F7EF 100%);
  overflow-y: auto;
}

.content-wrapper {
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}

@media (max-width: 768px) {
  .dashboard-layout {
    flex-direction: column;
  }

  .content-body {
    padding: 1rem;
  }
}

/* Backdrop controlled by parent - appears when sidebar is open on small screens */
.sidebar-backdrop {
  display: none;
}

@media (max-width: 768px) {
  .sidebar-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.35);
    z-index: 50;
    display: none;
  }
  .sidebar-backdrop.show {
    display: block;
  }
}
</style>
