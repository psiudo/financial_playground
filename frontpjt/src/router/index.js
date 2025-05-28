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
import CommunityHomeView from '../views/community/CommunityHomeView.vue' // 커뮤니티 메인 (게시판 선택 등)
import PostListView from '../views/community/PostListView.vue'       // 게시글 목록
import PostDetailView from '../views/community/PostDetailView.vue'     // 게시글 상세
import PostCreateView from '../views/community/PostCreateView.vue'     // 게시글 작성
import PostEditView from '../views/community/PostEditView.vue'         // 게시글 수정 (선택적)
import BankLocationsView from '@/views/BankLocationsView.vue' // ★ 은행 위치 지도 View 추가
import SentimentAnalysisView from '../views/SentimentAnalysisView.vue';
import StockSentimentView from '../views/StockSentimentView.vue';

// routes 배열에서 중복된 HomeView 경로 하나를 제거하고, BankLocationsView 경로를 추가합니다.
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
    meta: { requiresAuth: true }
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
  },
  {
    path: '/marketplace/:listingId',
    name: 'MarketplaceDetailView',
    component: MarketplaceDetailView,
    props: true,
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
    name: 'FinancialProductListView',
    component: FinancialProductListView,
  },
  {
    path: '/deposit-savings/:fin_prdt_cd',
    name: 'FinancialProductDetailView',
    component: FinancialProductDetailView,
    props: true
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  // === 종목 감정 분석 뷰 라우트 추가 ===
  {
    path: '/stock-sentiment', // URL 경로
    name: 'StockSentimentView', // 라우트 이름
    component: StockSentimentView
  },
  // =====================================
  // community routes
  {
    path: '/community',
    name: 'communityHome',
    component: CommunityHomeView,
  },
  {
    path: '/community/:boardType',
    name: 'postList',
    component: PostListView,
    props: true,
  },
  {
    path: '/community/posts/:postId',
    name: 'postDetail',
    component: PostDetailView,
    props: true,
  },
  {
    path: '/community/create',
    name: 'postCreate',
    component: PostCreateView,
  },
  {
    path: '/community/posts/:postId/edit',
    name: 'postEdit',
    component: PostEditView,
    props: true,
  },
  // ★ 은행 위치 지도 페이지 라우트 추가
  {
    path: '/bank-locations',
    name: 'bank-locations',
    component: BankLocationsView
  },
  // ★ 감정 분석 페이지 라우트 추가
  {
    path: '/realtime-stock-analysis', // URL 경로 (예시)
    name: 'RealtimeStockAnalysis',    // 라우트 이름
    component: SentimentAnalysisView  // 위에서 수정한 뷰 컴포넌트
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes, // routes: routes 와 동일
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    console.log('인증 필요, 로그인 페이지로 이동:', to.fullPath)
    next({ name: 'LoginView', query: { redirect: to.fullPath } }) // 로그인 후 돌아갈 경로 전달
  } else {
    next()
  }
})

export default router