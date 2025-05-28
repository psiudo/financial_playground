<template>
  <div class="commodity-history-view">
    <h1>{{ symbol }} 가격 내역</h1>
    <div class="filters">
      <label for="fromDate">시작일:</label>
      <input type="date" id="fromDate" v-model="fromDate" />
      <label for="toDate">종료일:</label>
      <input type="date" id="toDate" v-model="toDate" />
      <button @click="fetchHistory" :disabled="loading">조회</button>
    </div>

    <div v-if="loading" class="loading-spinner">로딩 중...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="!loading && !error && history.length > 0">
      <h3>상세 내역</h3>
      <table>
        <thead>
          <tr>
            <th>날짜</th>
            <th>가격</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in history" :key="item.date">
            <td>{{ item.date }}</td>
            <td>{{ formatPrice(item.price) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-if="!loading && !error && history.length === 0 && !initialLoad">
      선택된 기간에 해당하는 데이터가 없습니다.
    </p>
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/utils/api'; // baseURL: 'http://127.0.0.1:8000/api'
// import Chart from 'chart.js/auto'; // Chart.js 사용 시

const route = useRoute();
const symbol = ref(route.params.symbol);
const history = ref([]);
const fromDate = ref('');
const toDate = ref('');
const loading = ref(false);
const error = ref(null);
const initialLoad = ref(true);

const fetchHistory = async () => {
  if (!symbol.value) return;
  loading.value = true;
  error.value = null;
  initialLoad.value = false;

  // ★★★ API 경로 수정: 'v1/' 추가 ★★★
  let url = `v1/commodities/${symbol.value.toUpperCase()}/history/`; // 경로 수정 및 대문자화
  const params = new URLSearchParams(); // URLSearchParams 사용 권장
  if (fromDate.value) params.append('from', fromDate.value);
  if (toDate.value) params.append('to', toDate.value);

  const queryString = params.toString();
  if (queryString) {
    url += `?${queryString}`;
  }

  try {
    const response = await api.get(url); // api 인스턴스 사용, baseURL 자동 적용됨
    // 페이지네이션 응답을 사용하는 경우 response.data.results를 사용해야 할 수 있습니다.
    history.value = response.data.results ? response.data.results : response.data;
  } catch (err) {
    console.error(`${symbol.value} 가격 내역 조회 실패:`, err.response?.data || err.message, err);
    error.value = `데이터를 불러오는 데 실패했습니다: ${err.response?.data?.detail || err.message}`;
    history.value = [];
  } finally {
    loading.value = false;
  }
};

const formatPrice = (price) => {
  if (price === null || price === undefined) return 'N/A';
  // 백엔드에서 DecimalField로 소수점 2자리까지 올 수 있으므로 parseFloat 처리
  return new Intl.NumberFormat('ko-KR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(parseFloat(price));
};

onMounted(() => {
  // 기본적으로 페이지 진입 시 데이터를 로드하지 않고, 사용자가 조회 버튼을 누르도록 합니다.
  // 만약 진입 시 특정 기간(예: 최근 1년)을 기본으로 조회하고 싶다면 여기서 fetchHistory() 호출
});

watch(() => route.params.symbol, (newSymbol) => {
  if (newSymbol && newSymbol.toUpperCase() !== symbol.value.toUpperCase()) {
    symbol.value = newSymbol.toUpperCase();
    history.value = []; 
    initialLoad.value = true; // 심볼 변경 시 초기 로드 상태로
    // fetchHistory(); // 새 심볼로 자동 데이터 로드 원하면 주석 해제
  }
});
</script>

<style scoped>
.commodity-history-view {
  padding: 20px;
}
.filters {
  margin-bottom: 20px;
}
.filters label {
  margin-right: 5px;
}
.filters input[type="date"] {
  margin-right: 15px;
  padding: 5px;
}
.filters button {
  padding: 5px 10px;
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