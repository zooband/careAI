import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../views/LoginPage.vue'
import CaregiverDashboard from '../views/CaregiverDashboard.vue'
import ElderlyPortal from '../views/ElderlyPortal.vue'
import ElderlyPlayer from '../views/ElderlyPlayer.vue'
import AdminPage from '../views/AdminPage.vue'
import { requireAuth } from '../auth'

const routes = [
  { path: '/', name: 'login', component: LoginPage },
  {
    path: '/caregiver',
    name: 'caregiver',
    component: CaregiverDashboard,
    beforeEnter: (to, from, next) => {
      if (!requireAuth('caregiver')) next('/')
      else next()
    },
  },
  {
    path: '/elderly',
    name: 'elderly',
    component: ElderlyPortal,
    beforeEnter: (to, from, next) => {
      if (!requireAuth('elderly')) next('/')
      else next()
    },
  },
  {
    path: '/admin',
    name: 'admin',
    component: AdminPage,
  },
  {
    path: '/elderly/play',
    name: 'elderly-player',
    component: ElderlyPlayer,
    beforeEnter: (to, from, next) => {
      if (!requireAuth('elderly')) next('/')
      else next()
    },
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
