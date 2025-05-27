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
import api from '@/utils/api';
// import Chart from 'chart.js/auto'; // (선택) Chart.js 사용 시

const route = useRoute();
const symbol = ref(route.params.symbol);
const history = ref([]);
const fromDate = ref('');
const toDate = ref('');
const loading = ref(false); // 초기 로딩은 false로 설정하고, 조회 버튼 시 true
const error = ref(null);
const initialLoad = ref(true); // 최초 진입 시 "데이터 없음" 메시지 방지

// (선택) 차트 인스턴스
// let priceChartInstance = null;

const fetchHistory = async () => {
  if (!symbol.value) return;
  loading.value = true;
  error.value = null;
  initialLoad.value = false; // 조회 버튼을 눌렀으므로 더 이상 초기 로드가 아님

  let url = `/commodities/${symbol.value}/history/`;
  const params = new URLSearchParams();
  if (fromDate.value) params.append('from', fromDate.value);
  if (toDate.value) params.append('to', toDate.value);

  const queryString = params.toString();
  if (queryString) {
    url += `?${queryString}`;
  }

  try {
    const response = await api.get(url);
    history.value = response.data;
    // (선택) 차트 업데이트 로직 호출
    // updateChart();
  } catch (err) {
    console.error(`${symbol.value} 가격 내역 조회 실패:`, err);
    error.value = '데이터를 불러오는 데 실패했습니다. 필터 값을 확인하거나 잠시 후 다시 시도해주세요.';
    history.value = []; // 에러 발생 시 기존 데이터 초기화
  } finally {
    loading.value = false;
  }
};

const formatPrice = (price) => {
  return new Intl.NumberFormat('ko-KR', { style: 'currency', currency: 'KRW' }).format(price); // 예시: 원화
};

// (선택) 차트 업데이트 함수
/*
const updateChart = () => {
  const chartElement = document.getElementById('priceChart');
  if (!chartElement) return;

  const labels = history.value.map(item => item.date);
  const dataPoints = history.value.map(item => item.price);

  if (priceChartInstance) {
    priceChartInstance.destroy();
  }

  priceChartInstance = new Chart(chartElement, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: `${symbol.value} 가격`,
        data: dataPoints,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      scales: {
        x: {
          title: {
            display: true,
            text: '날짜'
          }
        },
        y: {
          title: {
            display: true,
            text: '가격 (KRW)' // 통화에 맞게 수정
          }
        }
      }
    }
  });
};
*/

// 컴포넌트 마운트 시 또는 symbol 변경 시 기본 데이터 로드 (예: 전체 기간)
onMounted(() => {
  // 초기에는 전체 기간 또는 기본 기간으로 조회할 수 있습니다.
  // 여기서는 사용자가 조회 버튼을 눌렀을 때만 데이터를 가져오도록 설정했습니다.
  // 만약 페이지 진입 시 바로 데이터를 로드하고 싶다면 fetchHistory()를 여기서 호출합니다.
});

// (선택) props로 전달된 symbol이 변경될 경우를 감지 (라우터 이동 없이 파라미터만 변경될 때)
watch(() => route.params.symbol, (newSymbol) => {
  if (newSymbol) {
    symbol.value = newSymbol;
    history.value = []; // 심볼 변경 시 이전 데이터 초기화
    // fromDate.value = ''; // 날짜 필터도 초기화할 수 있음
    // toDate.value = '';
    // fetchHistory(); // 새 심볼로 데이터 다시 로드
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