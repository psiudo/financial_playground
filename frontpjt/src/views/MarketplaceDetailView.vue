<template>
    <div class="container mt-5">
      <div v-if="loading" class="text-center">
        <p>데이터를 불러오는 중...</p>
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
  
      <div v-else-if="error" class="alert alert-danger">
        <p>{{ error }}</p>
        <RouterLink :to="{ name: 'MarketplaceView' }" class="btn btn-secondary">마켓플레이스로 돌아가기</RouterLink>
      </div>
  
      <div v-else-if="listing && listing.strategy" class="card">
        <div class="card-header">
          <h2>{{ listing.strategy.name }}</h2>
          <p class="mb-0">
              <span class="badge bg-info me-2">{{ listing.strategy.is_public ? '공개 전략' : '비공개 전략' }}</span>
              <span v-if="listing.price_point > 0" class="badge bg-warning text-dark">유료 ({{ listing.price_point }}P)</span>
              <span v-else class="badge bg-success">무료</span>
          </p>
        </div>
        <div class="card-body">
          <p><strong>판매자:</strong> {{ listing.seller }}</p>
          <p><strong>설명:</strong> {{ listing.strategy.description || '설명이 없습니다.' }}</p>
          <p><strong>판매 수:</strong> {{ listing.sales }}</p>
          <p><strong>등록일:</strong> {{ new Date(listing.created_at).toLocaleDateString() }}</p>
          
          <hr/>
          <h4>전략 규칙 (Rule JSON)</h4>
          <div v-if="listing.strategy.rule_json" class="mt-3">
            <pre class="bg-light p-3 rounded"><code>{{ JSON.stringify(listing.strategy.rule_json, null, 2) }}</code></pre>
          </div>
          <div v-else class="alert alert-info mt-3">
            <p v-if="isOwner">이 전략은 귀하의 소유이므로 규칙을 볼 수 있습니다. (실제 규칙이 정의되지 않았거나, 백엔드에서 접근 권한에 따라 rule_json이 제공되지 않았을 수 있습니다.)</p>
            <p v-else-if="listing.strategy.is_purchased">이미 구매한 전략입니다. 규칙을 확인할 수 있습니다. (실제 규칙이 정의되지 않았거나, 백엔드에서 접근 권한에 따라 rule_json이 제공되지 않았을 수 있습니다.)</p>
            <p v-else-if="listing.strategy.is_public && listing.price_point === 0">무료 공개 전략입니다. (규칙이 공개되지 않았거나 판매자가 비공개했을 수 있습니다.)</p>
            <p v-else>유료 전략입니다. 규칙의 상세 내용은 구매 후 확인할 수 있습니다.</p>
          </div>
        </div>
  
        <div class="card-footer">
          <div v-if="isOwner">
            <p class="text-info">✔ 자신이 판매하는 전략입니다.</p>
          </div>
          <div v-else-if="listing.strategy.is_purchased">
            <p class="text-success">✔ 이 전략을 이미 구매했습니다.</p>
            <RouterLink :to="{ name: 'StrategyListView' }" class="btn btn-outline-primary btn-sm mt-2">
              나의 전략 목록으로 이동
            </RouterLink>
          </div>
          <div v-else-if="listing.price_point > 0">
            <button @click="purchaseStrategy" class="btn btn-success" :disabled="purchaseLoading">
              <span v-if="purchaseLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              {{ purchaseLoading ? '구매 처리 중...' : `${listing.price_point}P로 구매하기` }}
            </button>
          </div>
          <div v-else> <button @click="forkFreeStrategy" class="btn btn-primary" :disabled="purchaseLoading">
              <span v-if="purchaseLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              {{ purchaseLoading ? '가져오는 중...' : '무료로 나의 전략에 추가하기 (Fork)' }}
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
  import { ref, onMounted, computed, watch } from 'vue'
  import { useRoute, useRouter, RouterLink } from 'vue-router' // RouterLink는 script setup에서 사용 안 함
  import api from '@/utils/api'
  
  const route = useRoute()
  const router = useRouter()
  
  console.log('[MarketplaceDetailView] 스크립트 setup 실행');
  
  const listing = ref(null)
  const loading = ref(true)
  const error = ref('') 
  const purchaseLoading = ref(false)
  
  const currentUsername = ref(localStorage.getItem('username')) 
  
  const getValidListingId = (param) => {
    if (Array.isArray(param)) {
      console.warn('[MarketplaceDetailView] listingId가 배열로 전달됨:', param, '첫 번째 요소를 사용합니다.');
      return param[0];
    }
    if (param !== null && typeof param === 'object') {
      console.error('[MarketplaceDetailView] listingId가 객체 형태로 전달됨:', param);
      return null; 
    }
    if (param === undefined || param === null || String(param).trim() === '') {
      console.error('[MarketplaceDetailView] listingId가 undefined, null 또는 빈 문자열입니다:', param);
      return null;
    }
    return String(param); // 일관성을 위해 문자열로 변환
  };
  
  const listingId = computed(() => getValidListingId(route.params.listingId));
  
  const isOwner = computed(() => {
    if (!listing.value || !listing.value.seller || !currentUsername.value) {
      return false
    }
    return listing.value.seller === currentUsername.value
  })
  
  // 데이터를 가져오는 유일한 함수: /api/marketplace/${id}/ 호출
  const fetchListingDetails = async () => {
    loading.value = true
    error.value = '' 
    listing.value = null 
  
    const idForApi = listingId.value; // computed를 통해 한번 검증된 ID 사용
    console.log(`[MarketplaceDetailView] fetchListingDetails 호출 시작. API 호출에 사용될 ID: "${idForApi}"`, '타입:', typeof idForApi);
  
    if (!idForApi) { // 여기서 null 또는 빈 문자열 등도 체크
        console.error('[MarketplaceDetailView] fetchListingDetails: API 호출 전 listingId가 유효하지 않음!', idForApi);
        error.value = `잘못된 매물 ID(${idForApi})로 데이터를 요청할 수 없습니다. 이전 페이지로 돌아가 다시 시도해주세요.`;
        loading.value = false;
        return;
    }
  
    try {
      // *** 유일한 데이터 요청 API 호출 ***
      const response = await api.get(`/marketplace/${idForApi}/`); // API 경로 확인
      console.log('[MarketplaceDetailView] /marketplace/:id/ API 응답:', JSON.parse(JSON.stringify(response.data))); // 순환 참조 방지하며 로그
      listing.value = response.data
      
      if (!listing.value || !listing.value.strategy) {
          console.error('[MarketplaceDetailView] API 응답에서 listing 또는 listing.strategy 객체를 찾을 수 없습니다.', response.data);
          error.value = '전략 상세 정보를 올바르게 불러오지 못했습니다. (서버 응답 데이터 구조 확인 필요)'
          listing.value = null; 
      }
  
    } catch (err) {
      console.error(`[MarketplaceDetailView] fetchListingDetails 실패 (요청 ID: ${idForApi})`, err);
      if (err.response) {
        console.error('Error response data:', err.response.data);
        console.error('Error response status:', err.response.status);
        let detailErrorMessage = err.response.data.detail || (typeof err.response.data === 'string' ? err.response.data : err.message);
        if (err.response.status === 404) {
          error.value = `해당 마켓플레이스 매물을 찾을 수 없습니다 (ID: ${idForApi}). 서버 응답: ${detailErrorMessage}`;
        } else {
          error.value = `리스팅 정보 로딩 중 오류 발생 (상태: ${err.response.status}). 서버 응답: ${detailErrorMessage}`;
        }
      } else {
        error.value = `리스팅 정보 로딩 중 네트워크 또는 기타 오류 발생: ${err.message}`;
      }
      listing.value = null;
    } finally {
      loading.value = false;
    }
  }
  
  const purchaseStrategy = async () => {
    if (!listing.value || !listing.value.strategy) {
      alert('구매할 전략 정보가 없습니다.');
      return;
    }
  
    const idForApi = listingId.value;
    if (!idForApi) {
      alert('잘못된 매물 ID로 구매를 시도할 수 없습니다.');
      return;
    }
  
    purchaseLoading.value = true;
    try {
      const response = await api.post(`/marketplace/${idForApi}/purchase/`); // API 경로 확인
      alert('전략을 성공적으로 구매했습니다! 나의 전략 목록에 추가되었습니다.');
      
      const clonedStrategyId = response.data.cloned_strategy_id;
  
      // 구매 성공 후, 프론트엔드 상태 업데이트
      // 백엔드의 PurchaseAPIView 응답에 업데이트된 listing 정보가 포함되어 있다고 가정
      if (response.data && response.data.listing && response.data.listing.strategy) {
          listing.value = response.data.listing; 
      } else {
          // 응답에 최신 리스팅 정보가 없다면, 다시 fetch하여 화면을 갱신
          await fetchListingDetails();
      }
  
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
      console.error('전략 구매에 실패했습니다:', err);
      alert(`전략 구매에 실패했습니다: ${err.response?.data?.detail || '서버 오류가 발생했습니다.'}`);
    } finally {
      purchaseLoading.value = false;
    }
  }
  
  const forkFreeStrategy = async () => {
    if (!listing.value || !listing.value.strategy) {
      alert('가져올 전략 정보가 없습니다.');
      return;
    }
     if (listing.value.price_point > 0) { 
        alert('이 전략은 유료입니다. 구매 버튼을 이용해주세요.');
        return;
    }
    // 무료 전략도 백엔드의 purchase API를 사용하여 복제 (백엔드에서 price_point가 0이면 포인트 차감 없이 처리)
    await purchaseStrategy(); 
  }
  
  onMounted(() => {
    console.log('[MarketplaceDetailView] onMounted 시작. route.params.listingId 원본:', route.params.listingId, '| 타입:', typeof route.params.listingId);
    const idFromRoute = getValidListingId(route.params.listingId);
    console.log('[MarketplaceDetailView] onMounted - getValidListingId 후 ID:', idFromRoute);
  
    if (idFromRoute) {
      fetchListingDetails();
    } else {
      loading.value = false;
      error.value = `잘못되었거나 없는 마켓플레이스 매물 ID입니다. (라우트 파라미터 값: "${route.params.listingId}")`;
      console.error(error.value);
    }
  })
  
  watch(listingId, (newId, oldId) => { // listingId는 computed이므로 .value 없이 사용
    console.log(`[MarketplaceDetailView] listingId (computed) 변경 감지: ${oldId} -> ${newId}`, '| 새 ID 타입:', typeof newId);
    if (newId && newId !== oldId) { 
      // newId가 이미 getValidListingId를 거친 값이므로 바로 사용 가능
      fetchListingDetails();
    } else if (!newId && oldId) { 
      console.log('[MarketplaceDetailView] watch에서 listingId가 유효하지 않은 값으로 변경됨 (아마도 페이지 이동).');
      // listing.value = null; // 필요시 데이터 초기화
      // error.value = '매물 ID 정보가 유효하지 않습니다.';
      // loading.value = false;
    }
  });
  
  </script>
  
  <style scoped>
  .card-header h2 {
    margin-bottom: 0;
  }
  pre {
    white-space: pre-wrap;
    word-break: break-all;
    background-color: #f8f9fa !important; 
    border: 1px solid #dee2e6;
  }
  .badge {
      font-size: 0.85em;
  }
  </style>