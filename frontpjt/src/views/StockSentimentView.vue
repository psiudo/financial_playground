<template>
  <div class="realtime-stock-analysis-container view-container">
    <h2 class="view-title">실시간 종목 분석</h2>
    <p class="view-description">분석하고 싶은 종목명을 입력하고 시장 반응을 확인해보세요.</p>

    <div class="search-form">
      <input
        type="text"
        v-model="searchQuery"
        placeholder="종목명 또는 종목코드를 입력하세요 (예: 삼성전자)"
        @keyup.enter="searchStock"
        :disabled="insightStore.isLoadingAnalysis"
        class="form-input"
      />
      <button @click="searchStock" :disabled="insightStore.isLoadingAnalysis || !searchQuery.trim()" class="submit-button">
        <span v-if="insightStore.isLoadingAnalysis" class="spinner-animation"></span>
        <span v-else>분석하기</span>
      </button>
    </div>

    <div v-if="insightStore.isLoadingAnalysis" class="message-box loading-box">
      <p>{{ searchQuery }} 종목의 댓글을 분석하고 있습니다. 잠시만 기다려 주세요...</p>
    </div>

    <div v-if="insightStore.analysisError" class="message-box error-box">
      <p><strong>오류:</strong> {{ insightStore.analysisError }}</p>
    </div>
    
    <div v-if="insightStore.actionMessage && !insightStore.currentSearchedStock?.batch_ready" class="message-box info-box">
        <p>{{ insightStore.actionMessage }}</p>
    </div>

    <div v-if="analysisData && analysisData.batch_ready" class="result-display-section">
      <h3 class="result-title">'{{ analysisData.stock_name || searchQuery }}' ({{ analysisData.stock_code || 'N/A' }}) 분석 결과</h3>
      
      <div class="result-card">
        <p><strong>종합 시장 반응:</strong> <span :class="overallSentimentClass(analysisData.overall_sentiment_display)">{{ analysisData.overall_sentiment_display }}</span></p>
        <p><strong>분석 업데이트 시각:</strong> {{ formatDateTime(analysisData.updated_at) }}</p>
        <p><strong>요약:</strong> {{ analysisData.summary || '제공된 요약 정보가 없습니다.' }}</p>

        <div v-if="analysisData.sentiment_stats && analysisData.total_analyzed > 0">
          <h4>감정 통계 (총 {{ analysisData.total_fetched }}개 댓글 중 {{ analysisData.total_analyzed }}개 분석됨)</h4>
          <ul>
            <li>긍정적 (Positive): {{ analysisData.positive }}건 ({{ analysisData.positive_percent }}%)</li>
            <li>부정적 (Negative): {{ analysisData.negative }}건 ({{ analysisData.negative_percent }}%)</li>
            <li>중립적 (Neutral): {{ analysisData.neutral }}건 ({{ analysisData.neutral_percent }}%)</li>
            <li v-if="analysisData.error > 0">분석 오류: {{ analysisData.error }}건</li>
          </ul>
          <div class="sentiment-chart-container" v-if="analysisData.total_analyzed > 0">
            <div class="sentiment-bar positive-bar" :style="{ width: analysisData.positive_percent + '%' }">
              <span v-if="parseFloat(analysisData.positive_percent) > 5">{{ analysisData.positive_percent }}%</span>
            </div>
            <div class="sentiment-bar negative-bar" :style="{ width: analysisData.negative_percent + '%' }">
              <span v-if="parseFloat(analysisData.negative_percent) > 5">{{ analysisData.negative_percent }}%</span>
            </div>
            <div class="sentiment-bar neutral-bar" :style="{ width: analysisData.neutral_percent + '%' }">
              <span v-if="parseFloat(analysisData.neutral_percent) > 5">{{ analysisData.neutral_percent }}%</span>
            </div>
          </div>
        </div>
        <p v-else-if="analysisData.sentiment_stats">분석된 댓글 감정 통계가 없습니다.</p>

        <div v-if="analysisData.keywords && analysisData.keywords.length > 0">
          <h4>주요 키워드</h4>
          <ul class="keyword-list">
            <li v-for="keyword in analysisData.keywords" :key="keyword" class="keyword-item">{{ keyword }}</li>
          </ul>
        </div>
        <p v-else-if="analysisData.keywords">추출된 키워드가 없습니다.</p>

         <button 
            v-if="authStore.isAuthenticated && analysisData.stock_code && !isAlreadyInterestStock(analysisData.stock_code)" 
            @click="addCurrentStockToInterests" 
            :disabled="insightStore.isLoadingAnalysis"
            class="action-button add-interest-button">
            관심 종목으로 추가 및 상세 분석 요청
        </button>
         <p v-if="authStore.isAuthenticated && isAlreadyInterestStock(analysisData.stock_code)" class="info-message">
            이미 관심 종목으로 등록되어 있습니다.
        </p>
      </div>
       <button @click="clearResults" class="reset-button">새로운 분석하기</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, watch } from 'vue';
import { useStockInsightStore } from '@/stores/stockInsightStore';
import { useAuthStore } from '@/stores/authStore'; // 인증 스토어 추가

const insightStore = useStockInsightStore();
const authStore = useAuthStore(); // 인증 스토어 사용
const searchQuery = ref('');

const analysisData = computed(() => insightStore.formattedCurrentSentiment);

const searchStock = () => {
  if (searchQuery.value.trim()) {
    // 종목 코드인지 이름인지 간단히 구분 (실제로는 더 정교한 로직 필요 가능성)
    const searchType = /^\d{6}$/.test(searchQuery.value.trim()) ? 'code' : 'name';
    insightStore.analyzeStockOnTheFly(searchQuery.value.trim(), searchType);
  }
};

const clearResults = () => {
  insightStore.clearSelectedStockAnalysis();
  searchQuery.value = '';
};

const formatDateTime = (isoString) => {
  if (!isoString) return 'N/A';
  try {
    const date = new Date(isoString);
    return date.toLocaleString('ko-KR');
  } catch (e) {
    return isoString; // 파싱 실패 시 원본 반환
  }
};

const overallSentimentClass = (sentiment) => {
  if (!sentiment) return '';
  const sentimentLower = sentiment.toLowerCase();
  return {
    'sentiment-positive-text': sentimentLower === '긍정적',
    'sentiment-negative-text': sentimentLower === '부정적',
    'sentiment-neutral-text': sentimentLower === '중립적' || sentimentLower === '혼재됨' || sentimentLower === '정보 없음',
  };
};

// 관심 종목 추가 함수
const addCurrentStockToInterests = async () => {
    if (analysisData.value && analysisData.value.stock_code && analysisData.value.stock_name) {
        await insightStore.addInterestAndRequestAnalysis(analysisData.value.stock_code, analysisData.value.stock_name);
        // 필요하다면, 사용자에게 메시지를 보여주거나 상태를 업데이트 할 수 있습니다.
        // 예: insightStore.actionMessage를 확인하여 성공/실패 메시지 표시
        if (insightStore.actionMessage) {
            alert(insightStore.actionMessage); // 간단한 alert, 실제로는 더 나은 UI 피드백 권장
        }
    } else {
        alert('종목 정보가 충분하지 않아 관심 종목에 추가할 수 없습니다.');
    }
};

// 이미 관심 종목인지 확인하는 함수
const isAlreadyInterestStock = (stockCode) => {
    if (!stockCode || !insightStore.myInterestStocks) return false;
    return insightStore.myInterestStocks.some(stock => stock.stock_code === stockCode);
};


// 컴포넌트 unmount 시 데이터 초기화
onUnmounted(() => {
  insightStore.clearSelectedStockAnalysis();
});

// 로그인 상태 변경 시 관심종목 목록 다시 불러오기 (선택적)
watch(() => authStore.isAuthenticated, (newAuthStatus) => {
    if (newAuthStatus) {
        insightStore.fetchMyInterestStocks();
    } else {
        insightStore.myInterestStocks = []; // 로그아웃 시 목록 초기화
    }
}, { immediate: true });


</script>

<style scoped>
/* 기존 SentimentAnalysisView.vue의 스타일과 유사하게 또는 프로젝트 테마에 맞게 적용 */
.view-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: var(--color-background, #fff);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.view-title {
  font-size: 2rem;
  font-weight: 500;
  color: var(--color-heading);
  text-align: center;
  margin-bottom: 0.75rem;
}

.view-description {
  text-align: center;
  color: var(--color-text-mute, #6c757d);
  margin-bottom: 2.5rem;
  font-size: 1rem;
}

.search-form {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.form-input {
  flex-grow: 1;
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-border, #ced4da);
  border-radius: 4px;
  font-size: 1rem;
}
.form-input:focus {
  outline: none;
  border-color: var(--joomak-primary, #3a5fcd);
  box-shadow: 0 0 0 0.2rem rgba(var(--joomak-primary-rgb, 58, 95, 205), 0.25);
}

.submit-button {
  padding: 0.75rem 1.5rem;
  background-color: var(--joomak-primary, #3a5fcd);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
}
.submit-button:hover:not(:disabled) {
  background-color: var(--joomak-primary-dark, #2c4aa0);
}
.submit-button:disabled {
  background-color: var(--color-border-hover, #e9ecef);
  color: var(--color-text-mute, #6c757d);
  cursor: not-allowed;
}

.spinner-animation { /* submit-button 내부 스피너 */
  width: 1.2em;
  height: 1.2em;
  border: 3px solid rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  border-top-color: #fff; /* 어두운 배경에서는 흰색, 밝은 배경에서는 primary 색상 등 조정 */
  animation: spin-animation 0.8s linear infinite;
}
.submit-button:disabled .spinner-animation {
  border-top-color: var(--color-text-mute, #6c757d); /* 비활성화 시 스피너 색상 */
}


@keyframes spin-animation {
  to { transform: rotate(360deg); }
}

.message-box {
  text-align: center;
  padding: 1.25rem;
  border-radius: 4px;
  margin-bottom: 2rem;
  font-size: 1rem;
}

.loading-box {
  background-color: #e9ecef; /* Light gray */
  color: #495057; /* Dark gray text */
  border: 1px solid #dee2e6;
}

.error-box {
  background-color: #f8d7da; /* Bootstrap danger background */
  color: #721c24; /* Bootstrap danger text */
  border: 1px solid #f5c6cb; /* Bootstrap danger border */
}
.info-box {
  background-color: #cce5ff; /* Bootstrap info background */
  color: #004085; /* Bootstrap info text */
  border: 1px solid #b8daff;
}

.result-display-section {
  margin-top: 2rem;
  border-top: 1px solid #dee2e6;
  padding-top: 2rem;
}

.result-title {
  font-size: 1.5rem;
  color: var(--color-heading);
  margin-bottom: 1.5rem;
  text-align: center;
}

.result-card {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.result-card p, .result-card h4, .result-card ul {
  margin-bottom: 0.75rem;
}
.result-card h4 {
  margin-top: 1.25rem;
  font-size: 1.1rem;
  color: var(--color-text);
}
.result-card ul {
  list-style-type: disc;
  padding-left: 20px;
}
.result-card li {
  margin-bottom: 0.3rem;
}

.sentiment-positive-text { color: var(--joomak-positive, #28a745); font-weight: bold; }
.sentiment-negative-text { color: var(--joomak-negative, #dc3545); font-weight: bold; }
.sentiment-neutral-text { color: var(--joomak-neutral, #6c757d); font-weight: bold; } /* 중립/혼재/정보없음 */

.keyword-list {
  list-style: none;
  padding-left: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.keyword-item {
  background-color: var(--joomak-primary-light, #e7eefa);
  color: var(--joomak-primary-dark, #3a5fcd);
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.9rem;
}

.sentiment-chart-container {
  display: flex;
  height: 20px;
  border-radius: 4px;
  overflow: hidden;
  margin: 10px 0;
  background-color: #e9ecef; /* 배경색 추가하여 빈 공간도 보이도록 */
}
.sentiment-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.75rem;
  font-weight: bold;
  transition: width 0.5s ease-in-out;
  text-shadow: 1px 1px 1px rgba(0,0,0,0.2);
}
.sentiment-bar span {
    padding: 0 5px;
}
.positive-bar { background-color: var(--joomak-positive, #28a745); }
.negative-bar { background-color: var(--joomak-negative, #dc3545); }
.neutral-bar { background-color: var(--joomak-neutral-light, #ffc107); color: #333; /* 밝은 노란색에 어두운 글씨 */}


.reset-button {
  display: block;
  margin: 1.5rem auto 0;
  padding: 0.7rem 1.2rem;
  background-color: #6c757d; /* Secondary button color */
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background-color 0.2s;
}
.reset-button:hover {
  background-color: #5a6268;
}

.action-button {
    margin-top: 1rem;
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
}
.add-interest-button {
    background-color: var(--joomak-success, #198754); /* 성공/추가 계열 색상 */
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
}
.add-interest-button:hover:not(:disabled) {
    background-color: var(--joomak-success-dark, #157347);
}
.add-interest-button:disabled {
    background-color: #e9ecef;
    color: #6c757d;
    cursor: not-allowed;
}
.info-message {
    font-size: 0.9rem;
    color: var(--color-text-mute);
    margin-top: 0.5rem;
}

</style>