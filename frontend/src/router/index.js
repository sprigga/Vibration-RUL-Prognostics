import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import FrequencyCalculator from '../views/FrequencyCalculator.vue'
import Algorithms from '../views/Algorithms.vue'
import PHMTraining from '../views/PHMTraining.vue'
import PHMDatabase from '../views/PHMDatabase.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: Dashboard
    },
    {
      path: '/frequency',
      name: 'frequency',
      component: FrequencyCalculator
    },
    {
      path: '/algorithms',
      name: 'algorithms',
      component: Algorithms
    },
    {
      path: '/phm-training',
      name: 'phm-training',
      component: PHMTraining
    },
    {
      path: '/phm-database',
      name: 'phm-database',
      component: PHMDatabase
    }
  ]
})

export default router
