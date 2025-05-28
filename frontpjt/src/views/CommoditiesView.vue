<!-- frontpjt/src/views/CommoditiesView.vue -->
<template>
  <div class="container py-4 commodities-view">
    <h1 class="mb-4 text-center">현물 자산 시세</h1>

    <div class="controls mb-4 p-3 border rounded bg-light shadow-sm">
      <h5 class="mb-3">조회 기간 설정</h5>
      <div class="row g-3 align-items-center">
        <div class="col-md-5">
          <label for="startDate" class="form-label">시작일:</label>
          <input type="date" id="startDate" v-model="startDate" class="form-control" />
        </div>
        <div class="col-md-5">
          <label for="endDate" class="form-label">종료일:</label>
          <input type="date" id="endDate" v-model="endDate" class="form-control" />
        </div>
        <div class="col-md-2 d-flex align-items-end">
          <button @click="fetchAllChartData" class="btn btn-primary w-100" :disabled="commodityStore.isLoadingList || commodityStore.isLoadingHistoryGold || commodityStore.isLoadingHistorySilver">
            <span v-if="commodityStore.isLoadingList || commodityStore.isLoadingHistoryGold || commodityStore.isLoadingHistorySilver" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            전체 조회
          </button>
        </div>
      </div>
    </div>

    <div v-if="commodityStore.isLoadingList" class="text-center py-5">
      <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
        <span class="visually-hidden">상품 목록 로딩 중...</span>
      </div>
      <p class="mt-2">상품 목록을 불러오는 중입니다...</p>
    </div>

    <div v-else-if="commodityStore.error && commodityStore.commodityList.length === 0" class="alert alert-danger">
      {{ commodityStore.error }}
    </div>

    <div v-else class="row g-4">
      <div class="col-lg-6">
        <div class="commodity-chart-card p-3 border rounded shadow-sm">
          <h4 class="mb-3 d-flex justify-content-between align-items-center">
            <span>🥇 {{ goldData?.name || '금' }} 시세</span>
            <small v-if="goldData?.latest_price" class="text-muted">최신가: {{ parseFloat(goldData.latest_price).toLocaleString() }}</small>
          </h4>
          <div v-if="commodityStore.isLoadingHistoryGold" class="text-center py-3">
            <div class="spinner-border spinner-border-sm text-secondary" role="status"></div>
            <p class="mt-1 small">금 시세 로딩 중...</p>
          </div>
          <div v-else-if="chartDataGold.datasets && chartDataGold.datasets[0].data.length > 0" class="chart-container">
            <Line :data="chartDataGold" :options="chartOptionsGold" />
          </div>
          <div v-else-if="fetchedGoldHistory" class="alert alert-info small">
            선택하신 기간에 대한 금 시세 데이터가 없습니다.
          </div>
           <div v-else class="alert alert-secondary small p-2 text-center">
            조회 버튼을 눌러 금 시세를 확인하세요.
          </div>
        </div>
      </div>

      <div class="col-lg-6">
        <div class="commodity-chart-card p-3 border rounded shadow-sm">
          <h4 class="mb-3 d-flex justify-content-between align-items-center">
            <span>🥈 {{ silverData?.name || '은' }} 시세</span>
            <small v-if="silverData?.latest_price" class="text-muted">최신가: {{ parseFloat(silverData.latest_price).toLocaleString() }}</small>
          </h4>
           <div v-if="commodityStore.isLoadingHistorySilver" class="text-center py-3">
            <div class="spinner-border spinner-border-sm text-secondary" role="status"></div>
            <p class="mt-1 small">은 시세 로딩 중...</p>
          </div>
          <div v-else-if="chartDataSilver.datasets && chartDataSilver.datasets[0].data.length > 0" class="chart-container">
            <Line :data="chartDataSilver" :options="chartOptionsSilver" />
          </div>
          <div v-else-if="fetchedSilverHistory" class="alert alert-info small">
            선택하신 기간에 대한 은 시세 데이터가 없습니다.
          </div>
          <div v-else class="alert alert-secondary small p-2 text-center">
            조회 버튼을 눌러 은 시세를 확인하세요.
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useCommodityStore } from '@/stores/commodityStore' // 경로는 실제 파일 위치에 맞게
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  TimeSeriesScale
} from 'chart.js'
import 'chartjs-adapter-date-fns';
import { ko } from 'date-fns/locale'; // 한글 locale import

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  TimeSeriesScale
)

const commodityStore = useCommodityStore()

// 상태 변수들
const startDate = ref('') // YYYY-MM-DD
const endDate = ref('')   // YYYY-MM-DD
const fetchedGoldHistory = ref(false)
const fetchedSilverHistory = ref(false)

// 상품 정보 가져오기 (금, 은)
const goldData = computed(() => commodityStore.commodityList.find(c => c.symbol === 'GOLD'))
const silverData = computed(() => commodityStore.commodityList.find(c => c.symbol === 'SILVER'))

// --- 차트 데이터 및 옵션 ---
const createChartData = (historyData, label, color) => {
  if (!historyData || historyData.length === 0) {
    return { labels: [], datasets: [{ data: [], label: label, borderColor: color, backgroundColor: color, tension: 0.1, fill: false }] };
  }
  return {
    labels: historyData.map(item => item.date),
    datasets: [
      {
        label: label,
        backgroundColor: color,
        borderColor: color,
        data: historyData.map(item => parseFloat(item.price)),
        fill: false,
        tension: 0.1,
        pointRadius: 2, // 점 크기
        pointHoverRadius: 5, // 호버 시 점 크기
      }
    ]
  }
}

const createChartOptions = (titleText) => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: { // 툴팁 및 호버 상호작용 모드
      intersect: false,
      mode: 'index',
    },
  scales: {
    x: {
      type: 'time',
      time: {
        unit: 'day',
        tooltipFormat: 'yyyy-MM-dd',
        displayFormats: {
          day: 'yy-MM-dd'
        },
        adapters: { // date-fns 어댑터 locale 설정
          date: {
            locale: ko
          }
        }
      },
      title: {
        display: true,
        text: '날짜'
      },
      grid: {
        display: false // x축 그리드 숨김 (선택적)
      }
    },
    y: {
      title: {
        display: true,
        text: '가격'
      },
      ticks: {
        callback: function(value) {
          return value.toLocaleString(); 
        }
      }
    }
  },
  plugins: {
    legend: {
      display: true,
      position: 'top',
    },
    title: { // 차트 제목
        display: true,
        text: titleText,
        font: {
            size: 16
        }
    },
    tooltip: {
      callbacks: {
        title: function(tooltipItems) {
            // 툴팁 제목에 날짜 표시 (date-fns 형식)
            if (tooltipItems.length > 0) {
                const date = new Date(tooltipItems[0].parsed.x);
                return date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' });
            }
            return '';
        },
        label: function(context) {
          let label = context.dataset.label || '';
          if (label) {
            label += ': ';
          }
          if (context.parsed.y !== null) {
            label += context.parsed.y.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
          }
          return label;
        }
      }
    }
  }
})

// 금 차트 데이터 및 옵션
const chartDataGold = computed(() => createChartData(commodityStore.priceHistoryGold, '금 시세', '#FFD700')) // 금색
const chartOptionsGold = computed(() => createChartOptions(`${goldData.value?.name || '금'} 가격 변동`))

// 은 차트 데이터 및 옵션
const chartDataSilver = computed(() => createChartData(commodityStore.priceHistorySilver, '은 시세', '#C0C0C0')) // 은색
const chartOptionsSilver = computed(() => createChartOptions(`${silverData.value?.name || '은'} 가격 변동`))


// --- 데이터 로드 함수 ---
async function fetchAllChartData() {
  fetchedGoldHistory.value = false
  fetchedSilverHistory.value = false

  // commodityStore에 priceHistoryGold, priceHistorySilver 상태와
  // isLoadingHistoryGold, isLoadingHistorySilver 상태가 필요함.
  // fetchPriceHistory도 symbol별로 데이터를 저장하도록 수정 필요.
  // 아래는 commodityStore가 수정되었다고 가정한 호출
  if (goldData.value) {
    await commodityStore.fetchPriceHistoryForSymbol('GOLD', startDate.value || null, endDate.value || null)
    fetchedGoldHistory.value = true
  }
  if (silverData.value) {
    await commodityStore.fetchPriceHistoryForSymbol('SILVER', startDate.value || null, endDate.value || null)
    fetchedSilverHistory.value = true
  }
}

onMounted(async () => {
  console.log('CommoditiesView mounted')
  await commodityStore.fetchCommodityList() // 상품 목록 (GOLD, SILVER 정보) 먼저 로드
  // 페이지 로드 시 기본 전체 기간 데이터 로드 (선택적)
  // await fetchAllChartData(); 
})

// 기간 변경 시 자동 조회 (선택적)
// watch([startDate, endDate], () => {
//   fetchAllChartData();
// });

</script>

<style scoped>
.commodities-view {
  max-width: 1200px; /* 너비 확장 */
  margin: auto;
}
.controls {
  background-color: #f8f9fa;
}
.commodity-chart-card {
  background-color: #fff;
  min-height: 480px; /* 차트 카드 최소 높이 */
  display: flex;
  flex-direction: column;
}
.chart-container {
  position: relative;
  flex-grow: 1; /* 카드가 늘어날 때 차트 영역도 같이 늘어나도록 */
  min-height: 350px; /* 차트 최소 높이 */
}
/* 스피너를 위한 추가 스타일 */
.spinner-border-sm {
    width: 1rem;
    height: 1rem;
    border-width: .2em;
}
</style>