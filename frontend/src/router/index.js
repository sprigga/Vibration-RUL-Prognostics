import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Algorithms from '../views/Algorithms.vue'
import TimeDomainAnalysis from '../views/TimeDomainAnalysis.vue'
import FrequencyDomainAnalysis from '../views/FrequencyDomainAnalysis.vue'
import EnvelopeAnalysis from '../views/EnvelopeAnalysis.vue'
import TimeFrequencyAnalysis from '../views/TimeFrequencyAnalysis.vue'
import HigherOrderStatistics from '../views/HigherOrderStatistics.vue'
import PHMTraining from '../views/PHMTraining.vue'
import PHMDatabase from '../views/PHMDatabase.vue'
import ProjectAnalysis from '../views/ProjectAnalysis.vue'
// NEW - Phase 1: Real-time analysis
import RealtimeAnalysis from '../views/RealtimeAnalysis.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: Dashboard
    },
    {
      path: '/algorithms',
      name: 'algorithms',
      component: Algorithms
    },
    {
      path: '/time-domain',
      name: 'time-domain',
      component: TimeDomainAnalysis
    },
    {
      path: '/frequency-domain',
      name: 'frequency-domain',
      component: FrequencyDomainAnalysis
    },
    {
      path: '/envelope-analysis',
      name: 'envelope-analysis',
      component: EnvelopeAnalysis
    },
    {
      path: '/time-frequency',
      name: 'time-frequency',
      component: TimeFrequencyAnalysis
    },
    {
      path: '/higher-order-statistics',
      name: 'higher-order-statistics',
      component: HigherOrderStatistics
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
    },
    {
      path: '/project-analysis',
      name: 'project-analysis',
      component: ProjectAnalysis
    },
    // NEW - Phase 1: Real-time analysis
    {
      path: '/realtime-analysis',
      name: 'realtime-analysis',
      component: RealtimeAnalysis
    }
  ]
})

export default router
