<!-- frontpjt/src/components/ProductRecommendationList.vue -->
<template>
  <div class="recommendation-section mt-4 p-3 border rounded shadow-sm">
    <h4 class="mb-3">
      {{ recommendationStore.recommendationMessage || '맞춤 금융상품 추천 🎁' }}
    </h4>

    <div v-if="recommendationStore.isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
        <span class="visually-hidden">추천 상품을 불러오는 중...</span>
      </div>
      <p class="mt-2 text-muted">고객님께 맞는 상품을 열심히 찾고 있습니다...</p>
    </div>

    <div v-else-if="recommendationStore.needsProfileUpdate" class="alert alert-warning d-flex flex-column align-items-center text-center">
      <p class="mb-2">{{ recommendationStore.recommendationMessage || '프로필 정보(투자 성향, 생년월일)를 입력하시면 더 정확한 맞춤 추천을 받을 수 있습니다.' }}</p>
      <RouterLink :to="{ name: 'profile' }" class="btn btn-sm btn-primary mt-2">
        프로필 설정 바로가기 <i class="bi bi-arrow-right-circle-fill ms-1"></i>
      </RouterLink>
    </div>

    <div v-else-if="recommendationStore.error && !recommendationStore.needsProfileUpdate" class="alert alert-danger d-flex flex-column align-items-center text-center">
      <p class="mb-2">{{ recommendationStore.error }}</p>
      <button @click="retryFetch" class="btn btn-sm btn-warning mt-2">
        <i class="bi bi-arrow-clockwise me-1"></i> 다시 시도
      </button>
    </div>

    <div v-else-if="!recommendationStore.recommendedProducts || recommendationStore.recommendedProducts.length === 0" class="alert alert-info text-center">
      <p>{{ recommendationStore.recommendationMessage || '현재 추천 드릴 수 있는 상품이 없습니다. 나중에 다시 확인해주세요.' }}</p>
    </div>

    <div v-else class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
      <div v-for="item in recommendationStore.recommendedProducts" :key="item.fin_prdt_cd" class="col">
        <div class="card h-100 shadow-sm product-card">
          <div class="card-body d-flex flex-column">
            <h5 class="card-title text-primary mb-1">{{ item.fin_prdt_nm }}</h5>
            <h6 class="card-subtitle mb-2 text-muted">{{ item.bank.name }}</h6>
            
            <div class="product-details mt-2">
              <p class="mb-1" v-if="item.options && item.options.length > 0">
                <small>
                  <i class="bi bi-graph-up-arrow text-success me-1"></i>
                  <strong>최고 금리:</strong> 
                  <span class="text-success fw-bold">{{ getMaxRate(item.options, 'intr_rate2') }}%</span>
                  (기본: {{ getMaxRate(item.options, 'intr_rate') }}%)
                </small>
              </p>
              <p class="mb-1" v-if="item.options && item.options.length > 0">
                <small>
                  <i class="bi bi-calendar3 text-info me-1"></i>
                  <strong>가입 기간:</strong> {{ getTermRange(item.options) }}
                </small>
              </p>
              <p class="mb-1" v-if="item.product_type">
                <small>
                  <i class="bi bi-tags-fill text-secondary me-1"></i>
                  <strong>상품 유형:</strong> {{ item.product_type === 'deposit' ? '정기예금' : '적금' }}
                </small>
              </p>
            </div>

            <div v-if="item.recommendation_reason" class="recommendation-info mt-3 p-2 bg-light-subtle border rounded-1 small">
              <p class="mb-1">
                <i class="bi bi-patch-check-fill text-info me-1"></i>
                <strong>추천 이유:</strong> {{ item.recommendation_reason }}
              </p>
              <p v-if="item.recommendation_score" class="mb-0">
                <i class="bi bi-gem text-warning me-1"></i>
                <strong>적합도 점수:</strong> {{ item.recommendation_score.toFixed(0) }}점
              </p>
            </div>
            
            <RouterLink :to="{ name: 'FinancialProductDetailView', params: { fin_prdt_cd: item.fin_prdt_cd }}" class="btn btn-outline-primary btn-sm mt-auto align-self-start">
              상품 상세보기 <i class="bi bi-chevron-right"></i>
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useRecommendationStore } from '@/stores/recommendationStore'
import { useAuthStore } from '@/stores/authStore' // authStore import

const recommendationStore = useRecommendationStore()
const authStore = useAuthStore() // authStore 인스턴스

// 사용자의 로그인 상태나 프로필 정보 변경을 감지하여 추천 목록을 다시 불러올 수 있도록 watch 설정
// ProfileView에서 프로필 저장 후 recommendationStore.refreshRecommendationsOnProfileUpdate()를 호출하는 것이 더 명시적일 수 있음
const unwatchAuth = watch(
  () => authStore.isAuthenticated, // 로그인 상태 감시
  (isAuth) => {
    if (isAuth) {
      // 로그인 되었을 때, 혹은 이미 로그인 된 상태로 컴포넌트 접근 시
      // authStore.user 정보가 로드된 후 추천을 요청해야 함
      if (authStore.user && (authStore.user.risk_grade && authStore.user.birth_date)) {
        console.log('ProductRecommendationList: Auth state changed to authenticated with profile, fetching recommendations.');
        recommendationStore.fetchRecommendations();
      } else if (authStore.user) {
        // 사용자는 있지만 프로필 정보가 부족한 경우 (fetchRecommendations 내부에서 처리)
        console.log('ProductRecommendationList: Auth state changed to authenticated but profile might be incomplete, attempting fetch.');
        recommendationStore.fetchRecommendations();
      }
    } else {
      // 로그아웃 되었을 때 추천 목록 초기화
      console.log('ProductRecommendationList: Auth state changed to not authenticated, clearing recommendations.');
      recommendationStore.clearRecommendations();
    }
  }
);

// 컴포넌트 마운트 시 초기 데이터 로드
onMounted(async () => {
  console.log('ProductRecommendationList: Component mounted.');
  if (authStore.isAuthenticated) {
    // App.vue 또는 DashboardView.vue에서 이미 fetchUser를 호출했을 수 있음
    // authStore.user가 아직 없다면 기다리거나, fetchRecommendations 내부에서 처리하도록 위임
    // fetchRecommendations 내부에서 authStore.user 로드 및 프로필 체크 로직이 있으므로 바로 호출
    await recommendationStore.fetchRecommendations();
  } else {
    recommendationStore.clearRecommendations();
    console.log('ProductRecommendationList: User not authenticated on mount.');
  }
});

// 컴포넌트 언마운트 시 watch 정리
onUnmounted(() => {
  unwatchAuth();
});

// 상품 옵션에서 특정 금리 유형의 최대값 추출 (소수점 2자리까지)
const getMaxRate = (options, rateType) => {
  if (!options || options.length === 0) return 'N/A';
  const rates = options.map(opt => {
    const rateValue = opt && opt[rateType] !== null && opt[rateType] !== undefined ? parseFloat(opt[rateType]) : NaN;
    return isNaN(rateValue) ? -Infinity : rateValue; // 유효하지 않은 값은 최소값으로 처리
  });
  const maxRate = Math.max(...rates);
  return maxRate === -Infinity ? 'N/A' : maxRate.toFixed(2);
};

// 상품 옵션에서 가입 기간 범위 추출
const getTermRange = (options) => {
  if (!options || options.length === 0) return 'N/A';
  const terms = options.map(opt => {
    const termValue = opt && opt.save_trm !== null && opt.save_trm !== undefined ? parseInt(opt.save_trm) : NaN;
    return isNaN(termValue) ? null : termValue;
  }).filter(term => term !== null); // 유효한 기간만 필터링

  if (terms.length === 0) return 'N/A';
  const minTerm = Math.min(...terms);
  const maxTerm = Math.max(...terms);
  return minTerm === maxTerm ? `${minTerm}개월` : `${minTerm}~${maxTerm}개월`;
};

// "다시 시도" 버튼 클릭 시
const retryFetch = () => {
  console.log('ProductRecommendationList: Retrying fetch recommendations...');
  recommendationStore.fetchRecommendations(true); // 강제 새로고침으로 재시도
}

</script>

<style scoped>
.recommendation-section {
  background-color: #f8f9fa; /* 밝은 배경색 */
}
.product-card {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  display: flex; /* 내부 컨텐츠 정렬을 위해 추가 */
  flex-direction: column; /* 내부 컨텐츠 세로 정렬 */
}
.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1) !important;
}
.card-title {
  font-size: 1.05rem; /* 약간 줄임 */
  font-weight: bold;
}
.card-subtitle {
  font-size: 0.9rem;
}
.product-details small {
  display: block; /* 각 상세 정보 줄바꿈 */
  line-height: 1.4;
}
.recommendation-info {
  background-color: #e9ecef; /* 추천 정보 배경색 변경 */
  font-size: 0.85rem;
}
.recommendation-info p {
  margin-bottom: 0.3rem !important;
}
.recommendation-info p:last-child {
  margin-bottom: 0 !important;
}

/* 아이콘 스타일 (Bootstrap Icons 사용 가정) */
.bi {
  vertical-align: -0.125em; /* 아이콘 정렬 미세 조정 */
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}
</style>