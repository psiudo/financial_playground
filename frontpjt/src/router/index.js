// front/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import DashBoardView from '@/views/DashBoardView.vue'
import CommoditiesView from '@/views/CommoditiesView.vue'
import CommodityHistoryView from '@/views/CommodityHistoryView.vue'
import MarketplaceView from '@/views/MarketplaceView.vue';
import MarketplaceDetailView from '@/views/MarketplaceDetailView.vue';
import StrategyListView from '@/views/StrategyListView.vue';
import StrategyCreateView from '@/views/StrategyCreateView.vue';
import StrategyDetailView from '@/views/StrategyDetailView.vue';


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
  {
    path: '/marketplace',
    name: 'MarketplaceView',
    component: MarketplaceView,
    // meta: { requiresAuth: true } // 로그인 필요 여부
  },
  {
    path: '/marketplace/:listingId', // URL 파라미터 이름은 일관성 있게 (예: listingId)
    name: 'MarketplaceDetailView',
    component: MarketplaceDetailView,
    props: true, // listingId를 props로 전달
    // meta: { requiresAuth: true }
  },
  {
    path: '/strategies',
    name: 'StrategyListView',
    component: StrategyListView,
    meta: { requiresAuth: true } // 로그인 필요
  },
  {
    path: '/strategies/create',
    name: 'StrategyCreateView',
    component: StrategyCreateView,
    meta: { requiresAuth: true }
  },
  {
    path: '/strategies/:strategyId', // URL 파라미터 이름은 일관성 있게
    name: 'StrategyDetailView',
    component: StrategyDetailView,
    props: true, // strategyId를 props로 전달
    meta: { requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
