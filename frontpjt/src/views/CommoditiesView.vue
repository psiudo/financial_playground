<template>
  <div class="commodities-view">
    <h1>기초자산 목록</h1>
    <div v-if="loading" class="loading-spinner">로딩 중...</div>
    <div v-if="error" class="error-message">{{ error }}</div>
    <table v-if="!loading && !error && commodities.length > 0">
      <thead>
        <tr>
          <th>심볼</th>
          <th>이름</th>
          <th>최신 가격</th>
          <th>상세보기</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="commodity in commodities" :key="commodity.symbol">
          <td>{{ commodity.symbol }}</td>
          <td>{{ commodity.name }}</td>
          <td>{{ commodity.latest_price !== null ? formatPrice(commodity.latest_price) : 'N/A' }}</td>
          <td>
            <router-link :to="{ name: 'CommodityHistory', params: { symbol: commodity.symbol } }">
              내역 보기
            </router-link>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-if="!loading && !error && commodities.length === 0">
      표시할 기초자산 정보가 없습니다.
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/utils/api'; // Axios 인스턴스

const commodities = ref([]);
const loading = ref(true);
const error = ref(null);

const fetchCommodities = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await api.get('/commodities/list/');
    commodities.value = response.data;
  } catch (err) {
    console.error('기초자산 목록 조회 실패:', err);
    error.value = '데이터를 불러오는 데 실패했습니다. 잠시 후 다시 시도해주세요.';
  } finally {
    loading.value = false;
  }
};

const formatPrice = (price) => {
  // 필요에 따라 가격 포맷팅 (예: 소수점, 통화 기호 등)
  return new Intl.NumberFormat('ko-KR', { style: 'currency', currency: 'KRW' }).format(price); // 예시: 원화
};

onMounted(() => {
  fetchCommodities();
});
</script>

<style scoped>
.commodities-view {
  padding: 20px;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}
th, td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}
th {
  background-color: #f2f2f2;
}
.loading-spinner, .error-message {
  text-align: center;
  margin-top: 20px;
  font-size: 1.2em;
}
.error-message {
  color: red;
}
</style>