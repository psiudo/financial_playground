<!-- frontpjt/src/views/MarketplaceView.vue -->
<template>
    <div class="marketplace-view">
      <h1>전략 마켓플레이스</h1>
      <button @click="showCreateListingModal = true" class="create-listing-btn">내 전략 판매 등록하기</button>
  
      <div v-if="loading" class="loading-spinner">로딩 중...</div>
      <div v-if="error" class="error-message">{{ error }}</div>
  
      <div class="listings-grid" v-if="!loading && !error && listings.length > 0">
        <div v-for="listing in listings" :key="listing.id" class="listing-card">
          <h2>{{ listing.strategy_name }}</h2>
          <p><strong>판매자:</strong> {{ listing.seller }}</p>
          <p><strong>가격:</strong> {{ listing.price_point }} 포인트</p>
          <p><strong>판매 횟수:</strong> {{ listing.sales }}</p>
          <p><strong>등록일:</strong> {{ formatDate(listing.created_at) }}</p>
          <router-link :to="{ name: 'MarketplaceDetailView', params: { listingId: listing.id } }" class="details-btn">
            상세보기 및 구매
          </router-link>
        </div>
      </div>
      <p v-if="!loading && !error && listings.length === 0">
        마켓플레이스에 등록된 전략이 없습니다.
      </p>
  
      <div v-if="showCreateListingModal" class="modal-overlay" @click.self="showCreateListingModal = false">
        <div class="modal-content">
          <h3>새 전략 판매 등록</h3>
          <form @submit.prevent="handleCreateListing">
            <div>
              <label for="strategySelect">판매할 전략 선택:</label>
              <select id="strategySelect" v-model="newListing.strategy" required>
                <option disabled value="">전략을 선택하세요</option>
                <option v-for="strat in userStrategies" :key="strat.id" :value="strat.id">
                  {{ strat.name }}
                </option>
              </select>
              <div v-if="!userStrategies.length && !strategiesLoading">
                  판매할 수 있는 내 전략이 없습니다. 먼저 전략을 생성해주세요.
                  <router-link to="/strategies">나의 전략 관리로 이동</router-link>
              </div>
               <div v-if="strategiesLoading">내 전략 목록 로딩중...</div>
            </div>
            <div>
              <label for="pricePoint">판매 가격 (포인트):</label>
              <input type="number" id="pricePoint" v-model.number="newListing.price_point" min="0" required />
            </div>
            <div class="modal-actions">
              <button type="submit" :disabled="listingCreating">등록</button>
              <button type="button" @click="showCreateListingModal = false">취소</button>
            </div>
            <p v-if="createError" class="error-message">{{ createError }}</p>
          </form>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import api from '@/utils/api';
  
  const router = useRouter();
  const listings = ref([]);
  const loading = ref(true);
  const error = ref(null);
  
  const showCreateListingModal = ref(false);
  const userStrategies = ref([]); // 사용자의 전략 목록
  const strategiesLoading = ref(false);
  const newListing = ref({
    strategy: '', // strategy ID
    price_point: 0,
  });
  const listingCreating = ref(false);
  const createError = ref(null);
  
  const fetchListings = async () => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.get('/marketplace/');
      listings.value = response.data;
    } catch (err) {
      console.error('마켓플레이스 목록 조회 실패:', err);
      error.value = '목록을 불러오는 데 실패했습니다.';
    } finally {
      loading.value = false;
    }
  };
  
  const fetchUserStrategies = async () => {
      strategiesLoading.value = true;
      try {
          // 사용자의 전략 목록을 가져오는 API 엔드포인트 (예시: /api/strategies/)
          // 이 API는 이미 '나의 전략' 페이지를 위해 구현되었을 수 있습니다.
          const response = await api.get('/strategies/strategies/');
          userStrategies.value = response.data.filter(strat => 
              !listings.value.some(listing => listing.strategy === strat.id) // 이미 마켓에 등록된 전략 제외
          );
      } catch (err) {
          console.error('사용자 전략 목록 조회 실패:', err);
          createError.value = '내 전략 목록을 불러오는 데 실패했습니다.'; // 모달 내 에러 메시지로 표시
      } finally {
          strategiesLoading.value = false;
      }
  };
  
  
  const handleCreateListing = async () => {
    listingCreating.value = true;
    createError.value = null;
    try {
      await api.post('/marketplace/', newListing.value);
      alert('전략이 마켓플레이스에 성공적으로 등록되었습니다!');
      showCreateListingModal.value = false;
      newListing.value = { strategy: '', price_point: 0 }; // 폼 초기화
      fetchListings(); // 목록 새로고침
    } catch (err) {
      console.error('마켓플레이스 전략 등록 실패:', err);
      if (err.response && err.response.data) {
          // 백엔드에서 전달하는 구체적인 에러 메시지 사용
          const errorData = err.response.data;
          if (errorData.strategy && Array.isArray(errorData.strategy)) {
               createError.value = errorData.strategy.join(' ');
          } else if (typeof errorData === 'string') {
               createError.value = errorData;
          } else {
               createError.value = '등록에 실패했습니다. 입력값을 확인해주세요.';
          }
      } else {
          createError.value = '등록 중 오류가 발생했습니다.';
      }
    } finally {
      listingCreating.value = false;
    }
  };
  
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('ko-KR', options);
  };
  
  onMounted(() => {
    fetchListings();
    // 모달을 열 때 사용자 전략을 로드하도록 변경 가능
    // fetchUserStrategies(); 
  });
  
  // 모달이 열릴 때마다 사용자 전략 목록을 새로고침 (이미 등록된 전략 제외 로직 포함)
  watch(showCreateListingModal, (newValue) => {
      if (newValue) {
          fetchUserStrategies();
      }
  });
  </script>
  
  <style scoped>
  .marketplace-view {
    padding: 20px;
  }
  .create-listing-btn {
    background-color: #4CAF50;
    color: white;
    padding: 10px 15px;
    margin-bottom: 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  .create-listing-btn:hover {
    background-color: #45a049;
  }
  .listings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
  }
  .listing-card {
    border: 1px solid #ddd;
    padding: 15px;
    border-radius: 8px;
    background-color: #f9f9f9;
  }
  .listing-card h2 {
    margin-top: 0;
    font-size: 1.5em;
  }
  .details-btn {
    display: inline-block;
    margin-top: 10px;
    padding: 8px 12px;
    background-color: #007bff;
    color: white;
    text-decoration: none;
    border-radius: 4px;
  }
  .details-btn:hover {
    background-color: #0056b3;
  }
  .loading-spinner, .error-message {
    text-align: center;
    margin-top: 20px;
    font-size: 1.2em;
  }
  .error-message {
    color: red;
  }
  
  /* 모달 스타일 */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .modal-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    width: 90%;
    max-width: 500px;
  }
  .modal-content h3 {
    margin-top: 0;
  }
  .modal-content div {
    margin-bottom: 15px;
  }
  .modal-content label {
    display: block;
    margin-bottom: 5px;
  }
  .modal-content input, .modal-content select {
    width: 100%;
    padding: 8px;
    box-sizing: border-box;
  }
  .modal-actions {
    text-align: right;
  }
  .modal-actions button {
    margin-left: 10px;
    padding: 8px 15px;
  }
  </style>