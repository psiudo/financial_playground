// frontpjt/src/router/index.js
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
import FinancialProductListView from '@/views/FinancialProductListView.vue'
import FinancialProductDetailView from '@/views/FinancialProductDetailView.vue'
import ProfileView from '@/views/ProfileView.vue' // ProfileView import 경로 수정 (@/views/)
import { useAuthStore } from '@/stores/authStore'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/login',
    name: 'LoginView', // 기존 'LoginView' 유지
    component: LoginView,
  },
  {
    path: '/dashboard',
    name: 'DashBoardView',
    component: DashBoardView,
    meta: { requiresAuth: true } // 대시보드도 로그인 필요 설정 추가
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
    // meta: { requiresAuth: true } // 필요시 주석 해제
  },
  {
    path: '/marketplace/:listingId',
    name: 'MarketplaceDetailView',
    component: MarketplaceDetailView,
    props: true,
    // meta: { requiresAuth: true } // 필요시 주석 해제
  },
  {
    path: '/strategies',
    name: 'StrategyListView',
    component: StrategyListView,
    meta: { requiresAuth: true }
  },
  {
    path: '/strategies/create',
    name: 'StrategyCreateView',
    component: StrategyCreateView,
    meta: { requiresAuth: true }
  },
  {
    path: '/strategies/:strategyId',
    name: 'StrategyDetailView',
    component: StrategyDetailView,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/deposit-savings',
    name: 'FinancialProductListView', // 기존 'FinancialProductListView' 유지
    component: FinancialProductListView,
  },
  {
    path: '/deposit-savings/:fin_prdt_cd',
    name: 'FinancialProductDetailView', // 기존 'FinancialProductDetailView' 유지
    component: FinancialProductDetailView,
    props: true
  },
  {
    path: '/profile', // 프로필 페이지 라우트 추가
    name: 'profile',
    component: ProfileView,
    meta: { requiresAuth: true } // 프로필 페이지는 로그인 필수
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 네비게이션 가드 설정
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  // requiresAuth 메타 필드가 있고, 사용자가 인증되지 않은 경우
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // 로그인 페이지로 리디렉션
    // 사용자가 로그인 후 원래 가려던 페이지로 돌아갈 수 있도록
    // to.fullPath를 쿼리 파라미터로 전달할 수 있습니다.
    // 예: next({ name: 'LoginView', query: { redirect: to.fullPath } })
    // LoginView.vue에서는 이 redirect 쿼리를 확인하고 로그인 성공 시 해당 경로로 이동시킵니다.
    console.log('인증 필요, 로그인 페이지로 이동:', to.fullPath)
    next({ name: 'LoginView' })
  } else {
    // 그 외의 경우 정상적으로 다음 페이지로 이동
    next()
  }
})

export default router