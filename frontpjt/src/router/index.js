// front/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import DashBoardView from '@/views/DashBoardView.vue'
import CommoditiesView from '@/views/CommoditiesView.vue'
import CommodityHistoryView from '@/views/CommodityHistoryView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/login',
    name: 'LoginView',
    component: LoginView,
  },
  {
    path: '/dashboard',
    name: 'DashBoardView',
    component: DashBoardView,
  },
  {
    path: '/commodities',
    name: 'Commodities',
    component: CommoditiesView,
  },
  {
    path: '/commodities/:symbol/history',
    name: 'CommodityHistory',
    component: CommodityHistoryView,
    props: true,
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
