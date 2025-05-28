<template>
  <div class="container mt-5 marketplace-detail-page">
    <div v-if="loading" class="text-center loading-section">
      <p>데이터를 불러오는 중...</p>
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger error-section">
      <p>{{ error }}</p>
      <RouterLink :to="{ name: 'MarketplaceView' }" class="btn btn-secondary">마켓플레이스로 돌아가기</RouterLink>
    </div>

    <div v-else-if="listing && listing.strategy" class="card strategy-detail-card">
      <div class="card-header">
        <h2>{{ listing.strategy.name }}</h2>
        <p class="mb-0">
            <span class="badge me-2" :class="listing.strategy.is_public ? 'bg-info' : 'bg-secondary'">{{ listing.strategy.is_public ? '공개 전략' : '비공개 전략' }}</span>
            <span v-if="listing.price_point > 0" class="badge bg-warning text-dark">유료 ({{ listing.price_point }}P)</span>
            <span v-else class="badge bg-success">무료</span>
        </p>
      </div>
      <div class="card-body">
        <p><strong>판매자:</strong> {{ listing.seller_username || '정보 없음' }}</p>
        <p><strong>설명:</strong> {{ listing.strategy.description || '설명이 없습니다.' }}</p>
        <p><strong>판매 수:</strong> {{ listing.sales_count !== undefined ? listing.sales_count : '정보 없음' }}</p>
        <p><strong>등록일:</strong> {{ formatDate(listing.created_at) }}</p>
        
        <hr/>
        <h4>전략 규칙</h4>
        <div v-if="listing.strategy.rule_json && (isOwner || listing.strategy.is_purchased || (listing.strategy.is_public && listing.price_point === 0))" class="mt-3 rule-display-container">
            <RuleDisplay :rules="listing.strategy.rule_json" />
        </div>
        <div v-else class="alert alert-info mt-3">
          <p v-if="isOwner">이 전략은 귀하의 소유이므로 규칙을 볼 수 있습니다. (백엔드에서 규칙이 제공되지 않았거나, rule_json 필드가 없을 수 있습니다.)</p>
          <p v-else-if="listing.strategy.is_purchased">이미 구매한 전략입니다. 규칙을 확인할 수 있습니다. (백엔드에서 규칙이 제공되지 않았거나, rule_json 필드가 없을 수 있습니다.)</p>
          <p v-else-if="listing.strategy.is_public && listing.price_point === 0">무료 공개 전략입니다. (규칙이 공개되지 않았거나 판매자가 비공개했을 수 있습니다. 또는 rule_json 필드가 없을 수 있습니다.)</p>
          <p v-else>유료 전략입니다. 규칙의 상세 내용은 구매 후 확인할 수 있습니다.</p>
        </div>
      </div>

      <div class="card-footer text-end">
        <div v-if="isOwner" class="owner-actions">
          <p class="text-info text-start mb-2">✔ 자신이 판매하는 전략입니다.</p>
          </div>
        <div v-else-if="listing.strategy.is_purchased" class="purchased-actions">
          <p class="text-success text-start mb-2">✔ 이 전략을 이미 구매했습니다.</p>
          <RouterLink :to="{ name: 'StrategyListView' }" class="btn btn-outline-primary btn-sm mt-2">
            나의 전략 목록으로 이동
          </RouterLink>
        </div>
        <div v-else-if="listing.price_point > 0" class="purchase-actions">
          <button @click="purchaseStrategy" class="btn btn-success" :disabled="purchaseLoading">
            <span v-if="purchaseLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            {{ purchaseLoading ? '구매 처리 중...' : `${listing.price_point}P로 구매하기` }}
          </button>
        </div>
        <div v-else class="fork-actions"> 
          <button @click="forkFreeStrategy" class="btn btn-primary" :disabled="purchaseLoading">
            <span v-if="purchaseLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            {{ purchaseLoading ? '가져오는 중...' : '무료로 나의 전략에 추가 (Fork)' }}
          </button>
        </div>
        <RouterLink :to="{ name: 'MarketplaceView' }" class="btn btn-outline-secondary ms-2">
          마켓 목록으로
        </RouterLink>
      </div>
    </div>
      <div v-else class="alert alert-warning">
      <p>리스팅 또는 전략 정보를 찾을 수 없습니다. 마켓플레이스 목록으로 돌아가거나 다시 시도해주세요.</p>
      <RouterLink :to="{ name: 'MarketplaceView' }" class="btn btn-secondary">마켓플레이스로 돌아가기</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter, RouterLink } from 'vue-router';
import api from '@/utils/api';
import RuleDisplay from '@/components/RuleDisplay.vue';
import { useAuthStore } from '@/stores/authStore';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const listing = ref(null);
const loading = ref(true);
const error = ref(''); 
const purchaseLoading = ref(false);

const currentUsername = computed(() => authStore.user?.username); 

const getValidListingId = (param) => {
  if (Array.isArray(param)) {
    return param[0];
  }
  if (param === undefined || param === null || String(param).trim() === '') {
    return null;
  }
  return String(param);
};

const listingId = computed(() => getValidListingId(route.params.listingId));

const isOwner = computed(() => {
  if (!listing.value || !listing.value.seller_username || !currentUsername.value) {
    return false;
  }
  return listing.value.seller_username === currentUsername.value;
});

const formatDate = (dateString) => {
  if (!dateString) return '날짜 정보 없음';
  return new Date(dateString).toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' });
};

const fetchListingDetails = async () => {
  loading.value = true;
  error.value = ''; 
  listing.value = null; 

  const idForApi = listingId.value;

  if (!idForApi) {
      error.value = `잘못된 매물 ID(${idForApi})로 데이터를 요청할 수 없습니다.`;
      loading.value = false;
      return;
  }

  try {
    // ★★★ API 경로 수정: 'v1' 추가 ★★★
    const response = await api.get(`v1/marketplace/${idForApi}/`, { // 수정된 경로
      params: { for_listing_detail: true } 
    });
    listing.value = response.data;
    
    if (!listing.value || !listing.value.strategy) {
        error.value = '전략 상세 정보를 올바르게 불러오지 못했습니다. (서버 응답 데이터 구조 확인 필요)';
        listing.value = null; 
    }
  } catch (err) {
    let detailErrorMessage = err.response?.data?.detail || (typeof err.response?.data === 'string' ? err.response.data : err.message);
    if (err.response?.status === 404) {
      error.value = `해당 마켓플레이스 매물을 찾을 수 없습니다 (ID: ${idForApi}). ${detailErrorMessage || ''}`;
    } else {
      error.value = `리스팅 정보 로딩 중 오류 발생 (상태: ${err.response?.status}). ${detailErrorMessage || ''}`;
    }
    listing.value = null;
  } finally {
    loading.value = false;
  }
};

const purchaseStrategy = async () => {
  if (!listing.value || !listing.value.strategy) {
    alert('구매할 전략 정보가 없습니다.');
    return;
  }
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.');
    router.push({ name: 'LoginView', query: { redirect: route.fullPath } });
    return;
  }

  const idForApi = listingId.value;
  if (!idForApi) {
    alert('잘못된 매물 ID로 구매를 시도할 수 없습니다.');
    return;
  }

  purchaseLoading.value = true;
  try {
    // ★★★ API 경로 수정: 'v1' 추가 ★★★
    const response = await api.post(`v1/marketplace/${idForApi}/purchase/`); // 수정된 경로
    alert('전략을 성공적으로 구매했습니다! 나의 전략 목록에 추가되었습니다.');
    
    const clonedStrategyId = response.data.cloned_strategy_id;

    await fetchListingDetails(); 

    if (clonedStrategyId) {
      if (confirm("구매한 전략이 나의 전략 목록에 추가되었습니다. 해당 전략 상세 페이지로 이동하시겠습니까?")) {
        router.push({ name: 'StrategyDetailView', params: { strategyId: clonedStrategyId } });
      }
    } else {
        if (confirm("나의 전략 목록으로 이동하여 구매한 전략을 확인하시겠습니까?")) {
            router.push({ name: 'StrategyListView' });
        }
    }
  } catch (err) {
    console.error('전략 구매에 실패했습니다:', err.response || err);
    alert(`전략 구매에 실패했습니다: ${err.response?.data?.detail || '서버 오류가 발생했습니다.'}`);
  } finally {
    purchaseLoading.value = false;
  }
};

const forkFreeStrategy = async () => {
  if (!listing.value || !listing.value.strategy) {
    alert('가져올 전략 정보가 없습니다.');
    return;
  }
  if (listing.value.price_point > 0) { 
      alert('이 전략은 유료입니다. 구매 버튼을 이용해주세요.');
      return;
  }
  await purchaseStrategy(); 
};

onMounted(async () => {
  if (authStore.token && !authStore.user) {
    await authStore.fetchUser();
  }

  const idFromRoute = getValidListingId(route.params.listingId);
  if (idFromRoute) {
    fetchListingDetails();
  } else {
    loading.value = false;
    error.value = `잘못되었거나 없는 마켓플레이스 매물 ID입니다. (라우트 파라미터 값: "${route.params.listingId}")`;
  }
});

watch(listingId, (newId, oldId) => {
  if (newId && newId !== oldId) { 
    fetchListingDetails();
  }
});
</script>

<style scoped>
/* ... 기존 스타일 코드 ... */
.marketplace-detail-page {
  padding-bottom: 3rem; 
}
.loading-section, .error-section {
  padding: 2rem;
  text-align: center;
}
.strategy-detail-card {
  border: 1px solid var(--joomak-border-subtle, #dee2e6);
  box-shadow: 0 4px 8px rgba(0,0,0,0.05);
}
.card-header {
  background-color: var(--joomak-surface, #f8f9fa);
  border-bottom: 1px solid var(--joomak-border-subtle, #dee2e6);
}
.card-header h2 {
  margin-bottom: 0.5rem;
  color: var(--joomak-text-strong);
}
.card-body p {
  margin-bottom: 0.75rem;
  color: var(--joomak-text-body);
}
.card-body strong {
  color: var(--joomak-text-strong);
}
.card-body h4 {
  color: var(--joomak-text-strong);
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}
.rule-display-container {
  background-color: var(--joomak-background-mute, #f8f9fa);
  padding: 15px;
  border-radius: 5px;
  border: 1px solid var(--joomak-border-subtle, #e9ecef);
}
.card-footer {
  background-color: var(--joomak-surface, #f8f9fa);
  border-top: 1px solid var(--joomak-border-subtle, #dee2e6);
}
.badge {
    font-size: 0.85em;
    padding: 0.4em 0.6em;
}
</style>