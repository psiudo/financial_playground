<template>
    <div class="marketplace-detail-view">
      <div v-if="loading" class="loading-spinner">로딩 중...</div>
      <div v-if="error" class="error-message">{{ error }}</div>
  
      <div v-if="listing && !loading && !error" class="listing-details">
        <h1>{{ listing.strategy_name }}</h1>
        <p><strong>판매자:</strong> {{ listing.seller }}</p>
        <p><strong>가격:</strong> {{ listing.price_point }} 포인트</p>
        <p><strong>판매 횟수:</strong> {{ listing.sales }}</p>
        <p><strong>등록일:</strong> {{ formatDate(listing.created_at) }}</p>
  
        <div v-if="listing.strategy_description" class="strategy-description">
          <h3>전략 설명</h3>
          <pre>{{ listing.strategy_description }}</pre>
        </div>
  
        <button 
          @click="handlePurchase" 
          :disabled="purchaseLoading || !canPurchase"
          class="purchase-btn">
          {{ purchaseButtonText }}
        </button>
        <p v-if="purchaseError" class="error-message">{{ purchaseError }}</p>
        <p v-if="purchaseSuccess" class="success-message">{{ purchaseSuccess }}</p>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import api from '@/utils/api';
  // import { useAuthStore } from '@/stores/auth'; // (선택) Pinia 스토어 사용 시
  
  // const authStore = useAuthStore(); // (선택)
  const route = useRoute();
  const router = useRouter();
  const listingId = ref(route.params.listingId);
  const listing = ref(null);
  const loading = ref(true);
  const error = ref(null);
  
  const purchaseLoading = ref(false);
  const purchaseError = ref(null);
  const purchaseSuccess = ref(null);
  const isOwner = ref(false);
  const alreadyPurchased = ref(false); 
  
  const fetchListingDetail = async () => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.get(`/marketplace/${listingId.value}/`);
      listing.value = response.data;
  
      // (선택) 추가적으로 strategy의 상세 정보를 가져오는 로직
      // if (listing.value && listing.value.strategy) {
      //   const stratResponse = await api.get(`/strategies/${listing.value.strategy}/`);
      //   listing.value.strategy_description = stratResponse.data.description; 
      //   // rule_json 등 필요한 정보 추가
      // }
  
  
      // (선택) 현재 사용자가 판매자인지, 이미 구매했는지 확인
      // 이 정보는 백엔드에서 함께 내려주거나, 별도 API 호출이 필요할 수 있습니다.
      // 예시: 현재 사용자 정보 가져오기 (Pinia 스토어 또는 /api/accounts/me/ 활용)
      // const currentUser = authStore.user; // Pinia 사용 시
      // if (currentUser && listing.value) {
      //   isOwner.value = currentUser.username === listing.value.seller;
      // }
      // 이미 구매했는지 여부는 /api/marketplace/purchases/ 등을 통해 확인 가능
  
    } catch (err) {
      console.error('마켓플레이스 상세 정보 조회 실패:', err);
      error.value = '상세 정보를 불러오는 데 실패했습니다.';
      if (err.response && err.response.status === 404) {
          error.value = '해당 판매 전략을 찾을 수 없습니다.';
      }
    } finally {
      loading.value = false;
    }
  };
  
  const handlePurchase = async () => {
    purchaseLoading.value = true;
    purchaseError.value = null;
    purchaseSuccess.value = null;
    try {
      const response = await api.post(`/marketplace/${listingId.value}/purchase/`);
      purchaseSuccess.value = `"<span class="math-inline">\{listing\.value\.strategy\_name\}" 전략 구매가 완료되었습니다\. \(</span>{listing.value.price_point}P 차감)`;
      // (선택) 사용자 포인트 정보 업데이트 (Pinia 스토어 등)
      // authStore.fetchUser(); // 예시
      alreadyPurchased.value = true; // 구매 완료 상태로 변경
      // 필요하다면 리스팅 정보 다시 로드 (예: 판매 횟수 업데이트)
      fetchListingDetail(); 
    } catch (err) {
      console.error('전략 구매 실패:', err);
      if (err.response && err.response.data && err.response.data.error) {
        purchaseError.value = err.response.data.error;
      } else {
        purchaseError.value = '전략 구매 중 오류가 발생했습니다.';
      }
    } finally {
      purchaseLoading.value = false;
    }
  };
  
  const canPurchase = computed(() => {
      // 실제 로직은 로그인한 사용자 정보(authStore.user.username)와 비교하거나
      // 백엔드에서 내려주는 is_owner, already_purchased 같은 플래그를 사용해야 합니다.
      // 아래는 임시 로직입니다.
      // if (!authStore.isAuthenticated) return false; // 로그인 안했으면 구매 불가
      // if (isOwner.value) return false; // 자신의 전략이면 구매 불가
      // if (alreadyPurchased.value) return false; // 이미 구매했으면 구매 불가
      return true; // 임시로 항상 구매 가능하게 설정
  });
  
  const purchaseButtonText = computed(() => {
      // if (!authStore.isAuthenticated) return '로그인 후 구매 가능';
      // if (isOwner.value) return '내 전략은 구매 불가';
      // if (alreadyPurchased.value) return '이미 구매한 전략';
      if (purchaseLoading.value) return '구매 처리 중...';
      return `${listing.value?.price_point} 포인트로 구매하기`;
  });
  
  
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString('ko-KR', options);
  };
  
  onMounted(() => {
    fetchListingDetail();
  });
  </script>
  
  <style scoped>
  .marketplace-detail-view {
    padding: 20px;
  }
  .listing-details {
    background-color: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  }
  .listing-details h1 {
    margin-top: 0;
  }
  .strategy-description {
    margin-top: 20px;
    padding: 15px;
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 4px;
  }
  .strategy-description pre {
    white-space: pre-wrap; /* 줄바꿈 처리 */
    word-wrap: break-word;
  }
  .purchase-btn {
    margin-top: 20px;
    padding: 10px 20px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1.1em;
  }
  .purchase-btn:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  .purchase-btn:hover:not(:disabled) {
    background-color: #218838;
  }
  .loading-spinner, .error-message, .success-message {
    text-align: center;
    margin-top: 20px;
    font-size: 1.2em;
  }
  .error-message {
    color: red;
  }
  .success-message {
    color: green;
  }
  </style>