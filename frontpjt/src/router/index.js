import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '@/views/HomeView.vue';
import LoginView from '@/views/LoginView.vue';
import DashBoardView from '@/views/DashBoardView.vue';
import CommoditiesView from '@/views/CommoditiesView.vue';
import CommodityHistoryView from '@/views/CommodityHistoryView.vue';
import MarketplaceView from '@/views/MarketplaceView.vue';
import MarketplaceDetailView from '@/views/MarketplaceDetailView.vue';
import StrategyListView from '@/views/StrategyListView.vue';
import StrategyCreateView from '@/views/StrategyCreateView.vue';
import StrategyDetailView from '@/views/StrategyDetailView.vue';
import FinancialProductListView from '@/views/FinancialProductListView.vue';
import FinancialProductDetailView from '@/views/FinancialProductDetailView.vue';
import ProfileView from '@/views/ProfileView.vue';
import { useAuthStore } from '@/stores/authStore';
import CommunityHomeView from '../views/community/CommunityHomeView.vue';
import PostListView from '../views/community/PostListView.vue';
import PostDetailView from '../views/community/PostDetailView.vue';
import PostCreateView from '../views/community/PostCreateView.vue';
import PostEditView from '../views/community/PostEditView.vue';
import BankLocationsView from '@/views/BankLocationsView.vue';
// "실시간 종목 분석"을 위한 뷰 컴포넌트 (기존 StockSentimentView.vue 활용)
import StockSentimentView from '../views/StockSentimentView.vue';

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
    meta: { requiresAuth: true },
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
    meta: { requiresAuth: true },
  },
  {
    path: '/strategies/create',
    name: 'StrategyCreateView',
    component: StrategyCreateView,
    meta: { requiresAuth: true },
  },
  {
    path: '/strategies/:strategyId',
    name: 'StrategyDetailView',
    component: StrategyDetailView,
    props: true,
    meta: { requiresAuth: true },
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
    props: true,
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
    meta: { requiresAuth: true },
  },
  // === 실시간 종목 분석 (종목 댓글 기반 감정 분석) 뷰 라우트 ===
  // App.vue에서 'RealtimeStockAnalysis'라는 이름으로 사용하고 있으므로,
  // 이 라우트 이름을 사용하고 StockSentimentView.vue 컴포넌트를 연결합니다.
  {
    path: '/stock-analysis', // 사용자가 접근할 URL 경로 (예: /stock-analysis)
    name: 'RealtimeStockAnalysis', // App.vue 네비게이션에서 사용할 이름
    component: StockSentimentView, // 이 뷰가 종목 검색 및 결과 표시를 담당
  },
  // ==========================================================
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
    meta: { requiresAuth: true },
  },
  {
    path: '/community/posts/:postId/edit',
    name: 'postEdit',
    component: PostEditView,
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: '/bank-locations',
    name: 'bank-locations',
    component: BankLocationsView,
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    console.log('인증 필요, 로그인 페이지로 이동:', to.fullPath);
    next({ name: 'LoginView', query: { redirect: to.fullPath } });
  } else {
    next();
  }
});

export default router;