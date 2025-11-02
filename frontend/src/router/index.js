import { createRouter, createWebHistory } from 'vue-router'
import Login from '../pages/Login.vue'
import Register from '../pages/Register.vue'
import Dashboard from '../pages/Dashboard.vue'
import Events from '../pages/Events.vue'
import Attendance from '../pages/Attendance.vue'
import AdminPanel from '../pages/AdminPanelNew.vue'
import CreateEvent from '../pages/CreateEventNew.vue'
import Societies from '../pages/Societies.vue'
import EnrollmentManagement from '../pages/EnrollmentManagement.vue'
import TeacherEnrollmentManagement from '../pages/TeacherEnrollmentManagement.vue'
import TeacherEvents from '../pages/TeacherEvents.vue'

const routes = [
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { 
    path: '/dashboard', 
    component: Dashboard,
    children: [
      { path: '', redirect: '/events' },
      { path: '/events', component: Events },
      { path: '/societies', component: Societies },
      { path: '/attendance', component: Attendance },
      { path: '/admin', component: AdminPanel, meta: { requiresAdmin: true } },
      { path: '/create-event', name: 'CreateEvent', component: CreateEvent, meta: { requiresTeacher: true }, props: true },
      { path: '/enrollments', component: EnrollmentManagement, meta: { requiresTeacher: true } },
      { path: '/teacher-enrollments', component: TeacherEnrollmentManagement, meta: { requiresAdmin: true } },
      { path: '/teacher-events', component: TeacherEvents, meta: { requiresTeacher: true } },
    ]
  },
  { path: '/', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

import { jwtDecode } from 'jwt-decode';

router.beforeEach((to, from, next) => {
  const publicPages = ['/login', '/register'];
  const authRequired = !publicPages.includes(to.path);
  const loggedIn = localStorage.getItem('token');

  if (authRequired && !loggedIn) {
    return next('/login');
  }

  if (loggedIn) {
    const decodedToken = jwtDecode(loggedIn);
    const userRole = decodedToken.role;

    if (to.meta.requiresAdmin && userRole !== 'admin') {
      return next('/dashboard');
    }
    if (to.meta.requiresTeacher && userRole !== 'teacher') {
      return next('/dashboard');
    }
    if (to.meta.requiresStudent && userRole !== 'student') {
      return next('/dashboard');
    }
  }

  next();
})

export default router
