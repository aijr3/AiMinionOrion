import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('../views/Home.vue') },
  { path: '/scenarios', component: () => import('../views/HistoryView.vue') },
  { path: '/scenarios/new', component: () => import('../views/ScenarioIntake.vue') },
  { path: '/scenarios/:id/analysis', component: () => import('../views/AnalysisView.vue') },
  { path: '/scenarios/:id/frameworks', component: () => import('../views/FrameworkView.vue') },
  { path: '/scenarios/:id/personas', component: () => import('../views/PersonaView.vue') },
  { path: '/scenarios/:id/strategy', component: () => import('../views/StrategyView.vue') },
  { path: '/scenarios/:id/pain-points', component: () => import('../views/PainPointView.vue') },
  { path: '/scenarios/:id/campaigns', component: () => import('../views/CampaignView.vue') },
  { path: '/scenarios/:id/roadmap', component: () => import('../views/RoadmapView.vue') },
  { path: '/scenarios/:id/dashboard', component: () => import('../views/DashboardView.vue') },
  { path: '/scenarios/:id/mirofish', component: () => import('../views/MiroFishView.vue') },
  { path: '/scenarios/:id/greene', component: () => import('../views/GreeneView.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
