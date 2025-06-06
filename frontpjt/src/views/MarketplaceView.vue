<template>
  <div class="marketplace-view">
    <h1>전략 마켓플레이스</h1>
    <button @click="showCreateListingModal = true" class="create-listing-btn">내 전략 판매 등록하기</button>

    <div v-if="loading" class="loading-spinner">로딩 중...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div class="listings-grid" v-if="!loading && !error && listings.length > 0">
      <div v-for="listing in listings" :key="listing.id" class="listing-card">
        <h2>{{ listing.strategy_name }}</h2>
        <p><strong>판매자:</strong> {{ listing.seller_username || listing.seller }}</p> <p><strong>가격:</strong> {{ listing.price_point }} 포인트</p>
        <p><strong>판매 횟수:</strong> {{ listing.sales_count !== undefined ? listing.sales_count : listing.sales }}</p> <p><strong>등록일:</strong> {{ formatDate(listing.created_at) }}</p>
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
import api from '@/utils/api'; // Axios 인스턴스

const router = useRouter();
const listings = ref([]);
const loading = ref(true);
const error = ref(null);

const showCreateListingModal = ref(false);
const userStrategies = ref([]);
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
    // ★★★ API 경로 수정: 'v1' 추가 ★★★
    const response = await api.get('v1/marketplace/'); // 수정된 경로
    // API 응답이 페이지네이션을 사용하는 경우, 실제 데이터는 response.data.results에 있을 수 있습니다.
    listings.value = response.data.results ? response.data.results : response.data;
    if (!Array.isArray(listings.value)) {
      console.warn('Marketplace listings API did not return an array in "results" or directly:', response.data);
      listings.value = []; // 배열이 아니면 빈 배열로 처리
    }
  } catch (err) {
    console.error('마켓플레이스 목록 조회 실패:', err);
    error.value = `목록을 불러오는 데 실패했습니다: ${err.response?.data?.detail || err.message}`;
  } finally {
    loading.value = false;
  }
};

const fetchUserStrategies = async () => {
    strategiesLoading.value = true;
    createError.value = null; // 이전 에러 메시지 초기화
    try {
        // TODO: 백엔드의 '나의 전략 목록' API 경로를 확인하고 정확히 입력해주세요.
        // 페이지네이션을 사용한다면 response.data.results를 사용해야 할 수 있습니다.
        // 현재는 'v1/strategies/'로 가정하고, 응답에 따라 .results를 사용합니다.
        const response = await api.get('v1/strategies/');
        let fetchedStrategies = response.data.results ? response.data.results : response.data;

        if (Array.isArray(fetchedStrategies)) {
            userStrategies.value = fetchedStrategies.filter(strat => 
                !listings.value.some(listing => listing.strategy === strat.id || listing.strategy?.id === strat.id)
            );
        } else {
            userStrategies.value = [];
            console.warn('User strategies API did not return an array:', response.data);
            createError.value = '내 전략 목록을 불러오는 데 실패했습니다 (데이터 형식 오류).';
        }
    } catch (err) {
        console.error('사용자 전략 목록 조회 실패:', err);
        createError.value = `내 전략 목록을 불러오는 데 실패했습니다: ${err.response?.data?.detail || err.message}`;
    } finally {
        strategiesLoading.value = false;
    }
};

const handleCreateListing = async () => {
  listingCreating.value = true;
  createError.value = null;
  if (!newListing.value.strategy) {
    createError.value = "판매할 전략을 선택해주세요.";
    listingCreating.value = false;
    return;
  }
  try {
    // ★★★ API 경로 수정: 'v1' 추가 ★★★
    await api.post('v1/marketplace/', newListing.value); // 수정된 경로
    alert('전략이 마켓플레이스에 성공적으로 등록되었습니다!');
    showCreateListingModal.value = false;
    newListing.value = { strategy: '', price_point: 0 };
    fetchListings(); // 목록 새로고침
  } catch (err) {
    console.error('마켓플레이스 전략 등록 실패:', err.response || err);
    if (err.response && err.response.data) {
      const errorData = err.response.data;
      let errorMessage = '등록에 실패했습니다. ';
      if (typeof errorData === 'string') {
        errorMessage += errorData;
      } else if (errorData.detail) {
        errorMessage += errorData.detail;
      } else {
        // 필드별 에러 메시지 조합
        const fieldErrors = [];
        for (const key in errorData) {
          if (Array.isArray(errorData[key])) {
            fieldErrors.push(`${key}: ${errorData[key].join(', ')}`);
          }
        }
        if (fieldErrors.length > 0) {
          errorMessage += fieldErrors.join(' ');
        } else {
          errorMessage += '입력값을 확인해주세요.';
        }
      }
      createError.value = errorMessage;
    } else {
      createError.value = '등록 중 네트워크 또는 서버 오류가 발생했습니다.';
    }
  } finally {
    listingCreating.value = false;
  }
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString('ko-KR', options);
};

onMounted(() => {
  fetchListings();
});

watch(showCreateListingModal, (newValue) => {
    if (newValue) {
        fetchUserStrategies();
    }
});
</script>

<style scoped>
.marketplace-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
.create-listing-btn {
  background-color: #4CAF50;
  color: white;
  padding: 10px 15px;
  margin-bottom: 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
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
  padding: 20px;
  border-radius: 8px;
  background-color: #f9f9f9;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.listing-card h2 {
  margin-top: 0;
  font-size: 1.5em;
  color: #333;
}
.listing-card p {
  margin-bottom: 8px;
  font-size: 0.95em;
  color: #555;
}
.details-btn {
  display: inline-block;
  margin-top: 15px;
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}
.details-btn:hover {
  background-color: #0056b3;
}
.loading-spinner, .error-message {
  text-align: center;
  margin-top: 30px;
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
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}
.modal-content h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 1.8em;
  color: #333;
}
.modal-content div {
  margin-bottom: 15px;
}
.modal-content label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #444;
}
.modal-content input[type="number"], .modal-content select {
  width: 100%;
  padding: 10px;
  box-sizing: border-box;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.modal-actions {
  text-align: right;
  margin-top: 20px;
}
.modal-actions button {
  margin-left: 10px;
  padding: 10px 20px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}
.modal-actions button[type="submit"] {
  background-color: #28a745;
  color: white;
}
.modal-actions button[type="submit"]:hover {
  background-color: #218838;
}
.modal-actions button[type="button"] {
  background-color: #6c757d;
  color: white;
}
.modal-actions button[type="button"]:hover {
  background-color: #5a6268;
}
</style>