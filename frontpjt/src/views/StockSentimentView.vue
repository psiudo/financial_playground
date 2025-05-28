<template>
  <div class="stock-sentiment-view view-container">
    <h2 class="view-title">종목별 투자 심리 분석 (토스 댓글 기반)</h2>
    
    <div class="section-box">
      <h3 class="section-title">실시간 종목 분석 요청</h3>
      <p class="section-description">종목명 또는 코드를 입력하여 토스 커뮤니티 반응을 바로 확인하세요. (DB 저장 없이 실시간 크롤링 및 분석)</p>
      <div class="input-group-row">
        <div class="input-group">
          <label for="realtime-stock-query" class="form-label">종목명 또는 코드:</label>
          <input type="text" id="realtime-stock-query" v-model.trim="realtimeQuery" placeholder="예: 삼성전자 또는 005930" class="form-input large-input">
        </div>
        <button @click="handleRealtimeAnalysis" class="action-button primary-button" :disabled="stockInsightStore.isLoadingAnalysis || !realtimeQuery">
          <span v-if="stockInsightStore.isLoadingAnalysis && stockInsightStore.currentSearchedStock?.stock?.company_name === realtimeQuery">분석 중...</span>
          <span v-else>실시간 분석 실행</span>
        </button>
      </div>
    </div>

    <div class="section-box" v-if="authStore.isAuthenticated">
      <h3 class="section-title">나의 관심 종목 분석</h3>
      <p class="section-description">관심 종목을 추가하고 저장된 분석 결과를 확인하거나, 백그라운드 분석을 요청할 수 있습니다.</p>
      
      <div class="interest-stock-controls">
        <div class="input-group-row">
          <div class="input-group">
            <label for="interest-stock-code" class="form-label">종목 코드:</label>
            <input type="text" id="interest-stock-code" v-model.trim="interestStockCodeToAdd" placeholder="005930" class="form-input">
          </div>
          <div class="input-group">
            <label for="interest-stock-name" class="form-label">종목명:</label>
            <input type="text" id="interest-stock-name" v-model.trim="interestStockNameToAdd" placeholder="삼성전자" class="form-input">
          </div>
          <button @click="addAndAnalyzeInterestStock" class="action-button success-button" :disabled="stockInsightStore.isLoadingAnalysis || !interestStockCodeToAdd || !interestStockNameToAdd">
            관심 종목 추가 & 분석 요청
          </button>
        </div>
      </div>

      <div class="interest-stock-list">
        <h4>나의 관심 종목 목록</h4>
        <div v-if="stockInsightStore.isLoadingList" class="message-box loading-box small-spinner">목록 로딩 중...</div>
        <ul v-else-if="stockInsightStore.myInterestStocks.length > 0">
          <li v-for="stock in stockInsightStore.myInterestStocks" :key="stock.id" 
              @click="loadSavedAnalysis(stock.id)" 
              :class="{ 'active-stock': stockInsightStore.currentSearchedStock?.stock?.id === stock.id }">
            <span>{{ stock.company_name }} ({{ stock.stock_code }}) - 상태: {{ stock.analysis_status }} ({{ stock.batch_ready ? '완료' : '처리중/미완료' }})</span>
            <span v-if="stock.last_analyzed_at" class="small-text"> (최근 분석: {{ formatDateTime(stock.last_analyzed_at) }})</span>
          </li>
        </ul>
        <p v-else>아직 등록된 관심 종목이 없습니다. 위에서 추가해주세요.</p>
        <p v-if="stockInsightStore.listError" class="error-text">{{ stockInsightStore.listError }}</p>
      </div>
    </div>
     <div v-else class="section-box">
        <p>로그인하시면 관심 종목을 등록하고 분석 결과를 저장할 수 있습니다.</p>
    </div>


    <div v-if="stockInsightStore.currentSearchedStock" class="sentiment-display-section">
      <hr class="section-divider">
      <h3 class="stock-name-title">
        {{ stockInsightStore.currentSearchedStock.company_name_display || '종목 정보' }} 
        <span v-if="stockInsightStore.currentSearchedStock.stock_code_display && stockInsightStore.currentSearchedStock.stock_code_display !== 'N/A'">({{ stockInsightStore.currentSearchedStock.stock_code_display }})</span>
         투자 심리
      </h3>

      <div v-if="stockInsightStore.isLoadingAnalysis && !stockInsightStore.currentSearchedStock.batch_ready" class="message-box loading-box">
        <span class="spinner-animation"></span> 정보를 가져오거나 분석을 요청하는 중입니다...
      </div>
      <div v-else-if="stockInsightStore.analysisError" class="message-box error-box">
        <p>{{ stockInsightStore.analysisError }}</p>
      </div>
      <div v-else-if="stockInsightStore.currentSearchedStock.batch_ready">
        <div class="overall-sentiment-box">
          <strong>종합 투자 심리:</strong> 
          <span :class="overallSentimentClass(stockInsightStore.currentSearchedStock.overall_sentiment_display)">
            {{ stockInsightStore.currentSearchedStock.overall_sentiment_display }}
          </span>
          <p v-if="stockInsightStore.currentSearchedStock.updated_at" class="last-analyzed-text">
             (분석 시각: {{ formatDateTime(stockInsightStore.currentSearchedStock.updated_at) }})
          </p>
        </div>
        
        <div v-if="stockInsightStore.formattedCurrentSentiment" class="sentiment-summary-chart">
          <h4>
            댓글 감정 분포 (성공: {{ stockInsightStore.formattedCurrentSentiment.total_analyzed }} / 수집: {{ stockInsightStore.formattedCurrentSentiment.total_fetched }})
          </h4>
          <div class="sentiment-bars" v-if="stockInsightStore.formattedCurrentSentiment.total_analyzed > 0">
            <div class="sentiment-bar positive-bar" :style="{ width: stockInsightStore.formattedCurrentSentiment.positive_percent + '%' }" :title="`긍정: ${stockInsightStore.formattedCurrentSentiment.positive}건`">
              😊 {{ stockInsightStore.formattedCurrentSentiment.positive_percent }}%
            </div>
            <div class="sentiment-bar neutral-bar" :style="{ width: stockInsightStore.formattedCurrentSentiment.neutral_percent + '%' }" :title="`중립: ${stockInsightStore.formattedCurrentSentiment.neutral}건`">
              😐 {{ stockInsightStore.formattedCurrentSentiment.neutral_percent }}%
            </div>
            <div class="sentiment-bar negative-bar" :style="{ width: stockInsightStore.formattedCurrentSentiment.negative_percent + '%' }" :title="`부정: ${stockInsightStore.formattedCurrentSentiment.negative}건`">
              😠 {{ stockInsightStore.formattedCurrentSentiment.negative_percent }}%
            </div>
          </div>
           <p v-else class="total-comments-text">분석 가능한 댓글이 없거나 분석에 실패했습니다.</p>
           <p v-if="stockInsightStore.formattedCurrentSentiment.error > 0" class="error-text small-text">분석 중 오류 발생 댓글: {{ stockInsightStore.formattedCurrentSentiment.error }}건</p>
        </div>
         <p v-if="stockInsightStore.currentSearchedStock.summary" class="summary-text">요약: {{ stockInsightStore.currentSearchedStock.summary }}</p>
      </div>
      <div v-else-if="stockInsightStore.actionMessage" class="message-box info-box">
          <p>{{ stockInsightStore.actionMessage }}</p>
      </div>
       <div v-else-if="!stockInsightStore.currentSearchedStock.batch_ready && stockInsightStore.currentSearchedStock.task_status" class="message-box info-box">
        <p>현재 이 종목의 분석 상태는 '{{ stockInsightStore.currentSearchedStock.task_status }}' 입니다. 잠시 후 다시 시도해주세요.</p>
      </div>
    </div>
     <div v-else-if="!stockInsightStore.currentSearchedStock && !stockInsightStore.isLoadingAnalysis && !stockInsightStore.actionMessage" class="message-box placeholder-box">
        <p>종목명을 입력하여 실시간 분석을 요청하거나, 관심 종목을 선택하여 저장된 분석 결과를 확인하세요.</p>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useStockInsightStore } from '@/stores/stockInsightStore';
import { useAuthStore } from '@/stores/authStore';

const stockInsightStore = useStockInsightStore();
const authStore = useAuthStore();

const realtimeQuery = ref(''); // 실시간 분석용 입력 (종목명 또는 코드)
const interestStockCodeToAdd = ref('');
const interestStockNameToAdd = ref('');
const selectedInterestStockId = ref(null); // 드롭다운 대신 리스트 클릭으로 ID 저장


onMounted(() => {
  if (authStore.isAuthenticated) {
    stockInsightStore.fetchMyInterestStocks();
  }
  stockInsightStore.clearCurrentAnalysis(); // 페이지 진입 시 이전 결과 초기화
});

onUnmounted(() => {
  // currentSearchedStock은 페이지 벗어날 때 초기화하는 것이 좋음
  stockInsightStore.clearCurrentAnalysis();
});

const handleRealtimeAnalysis = () => {
  if (!realtimeQuery.value.trim()) {
    alert('분석할 종목명 또는 코드를 입력해주세요.');
    return;
  }
  // 입력값이 숫자로만 이루어졌는지 등으로 코드/이름 구분 가능 (간단한 예시)
  const queryType = /^\d+$/.test(realtimeQuery.value) ? 'code' : 'name';
  stockInsightStore.analyzeStockOnTheFly(realtimeQuery.value, queryType);
  selectedInterestStockId.value = null; // 관심종목 선택 해제
};

const addAndAnalyzeInterestStock = () => {
  if (!interestStockCodeToAdd.value.trim() || !interestStockNameToAdd.value.trim()) {
    alert('관심 종목으로 추가할 종목 코드와 종목명을 모두 입력해주세요.');
    return;
  }
  stockInsightStore.addInterestAndRequestAnalysis(interestStockCodeToAdd.value, interestStockNameToAdd.value);
  interestStockCodeToAdd.value = ''; // 입력 필드 초기화
  interestStockNameToAdd.value = '';
};

const loadSavedAnalysis = (interestStockPk) => {
  realtimeQuery.value = ''; // 실시간 검색어 초기화
  selectedInterestStockId.value = interestStockPk;
  stockInsightStore.fetchSavedAnalysis(interestStockPk);
};


const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return 'N/A';
  try {
    const date = new Date(dateTimeString);
    if (isNaN(date.getTime())) { 
      return dateTimeString; 
    }
    return date.toLocaleString('ko-KR', {
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', hour12: false
    });
  } catch (e) {
    return dateTimeString;
  }
};

const overallSentimentClass = (sentimentDisplay) => {
  if (!sentimentDisplay || typeof sentimentDisplay !== 'string') return 'sentiment-unknown';
  const sLower = sentimentDisplay.toLowerCase();
  if (sLower.includes('긍정')) return 'sentiment-positive-text';
  if (sLower.includes('부정')) return 'sentiment-negative-text';
  if (sLower.includes('중립') || sLower.includes('혼재')) return 'sentiment-neutral-text';
  return 'sentiment-unknown';
};

</script>

<style scoped>
.view-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: var(--color-background, #fff);
  border-radius: var(--joomak-border-radius, 8px);
  box-shadow: var(--joomak-shadow-lg, 0 8px 24px rgba(0,0,0,0.1));
}

.view-title {
  font-size: 2.2rem;
  font-weight: 600;
  color: var(--color-heading);
  text-align: center;
  margin-bottom: 0.5rem;
}

.view-description {
  text-align: center;
  color: var(--color-text-mute, #6c757d);
  margin-bottom: 2rem;
  font-size: 1.1rem;
}

.section-box {
  margin-bottom: 2.5rem;
  padding: 1.5rem;
  border: 1px solid var(--color-border-hover, #e0e0e0);
  border-radius: var(--joomak-border-radius, 8px);
  background-color: var(--color-background-soft, #f8f9fa);
}

.section-title {
  font-size: 1.5rem;
  color: var(--color-heading);
  margin-bottom: 0.5rem;
}
.section-description {
  font-size: 0.95rem;
  color: var(--color-text-mute);
  margin-bottom: 1.5rem;
}

.input-group-row {
  display: flex;
  gap: 1rem;
  align-items: flex-end; /* 버튼과 입력창 하단 정렬 */
  margin-bottom: 1rem;
}
.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  flex-grow: 1;
}
.form-label {
  font-weight: 500;
  color: var(--color-text);
  font-size: 0.9rem;
}
.form-input {
  padding: 0.6rem 0.8rem;
  font-size: 1rem;
  border: 1px solid var(--color-border, #ced4da);
  border-radius: var(--joomak-border-radius-sm, 4px);
  background-color: var(--color-background, #fff);
  color: var(--color-text);
  width: 100%; /* 부모 flex-grow에 맞춰 채움 */
}
.form-input.large-input {
  padding: 0.75rem 1rem;
  font-size: 1.1rem;
}
.form-input:focus {
  border-color: var(--joomak-primary, #3a5fcd);
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(var(--joomak-primary-rgb, 58, 95, 205), 0.25);
}

.action-button {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: var(--joomak-border-radius-sm, 4px);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s, opacity 0.2s;
  white-space: nowrap;
}
.action-button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
.primary-button {
  background-color: var(--joomak-primary, #3a5fcd);
  color: white;
  padding: 0.75rem 1.5rem; /* 큰 버튼 */
  font-size: 1.05rem;
}
.primary-button:hover:not(:disabled) {
  background-color: var(--joomak-primary-dark, #2c4aa0);
}
.success-button {
  background-color: var(--joomak-success, #28a745);
  color: white;
}
.success-button:hover:not(:disabled) {
  background-color: var(--joomak-success-dark, #1e7e34);
}

.interest-stock-controls {
  margin-bottom: 1.5rem;
}
.interest-stock-list {
  margin-top: 1rem;
}
.interest-stock-list h4 {
  font-size: 1.1rem;
  color: var(--color-text);
  margin-bottom: 0.75rem;
}
.interest-stock-list ul {
  list-style: none;
  padding: 0;
  max-height: 200px; /* 스크롤 생성을 위한 높이 제한 */
  overflow-y: auto; /* 스크롤바 */
  border: 1px solid var(--color-border, #dee2e6);
  border-radius: var(--joomak-border-radius-sm, 4px);
}
.interest-stock-list li {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border-hover, #e9ecef);
  cursor: pointer;
  transition: background-color 0.15s;
}
.interest-stock-list li:last-child {
  border-bottom: none;
}
.interest-stock-list li:hover {
  background-color: var(--color-background-mute, #f1f3f5);
}
.interest-stock-list li.active-stock {
  background-color: var(--joomak-primary-light, #dce4f9); /* Joomak 테마에 맞는 연한 파란색 */
  font-weight: 500;
  color: var(--joomak-primary-dark, #2c4aa0);
}
.interest-stock-list .small-text {
  font-size: 0.8em;
  color: var(--color-text-mute);
  display: block;
  margin-top: 0.2em;
}


.section-divider {
  margin-top: 2.5rem;
  margin-bottom: 2rem;
  border-color: var(--color-border-hover, #e0e0e0);
}

.stock-name-title {
  font-size: 1.75rem;
  color: var(--color-heading);
  margin-bottom: 1.5rem;
  text-align: center;
}

.message-box {
  padding: 1rem 1.5rem;
  margin-bottom: 1.5rem;
  border-radius: var(--joomak-border-radius-sm, 4px);
  text-align: center;
  font-size: 1rem;
}
.loading-box {
  background-color: var(--color-background-mute, #e9ecef);
  color: var(--color-text);
  border: 1px solid var(--color-border, #dee2e6);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}
.loading-box.small-spinner .spinner-animation {
  width: 0.8em;
  height: 0.8em;
  border-width: 2px;
}
.error-box {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
.info-box {
  background-color: #e2e3e5; 
  color: #052c65; 
  border: 1px solid #c6d0dc;
}
.placeholder-box {
  color: var(--color-text-mute);
  padding: 3rem 1rem;
  border: 2px dashed var(--color-border, #ced4da);
  border-radius: var(--joomak-border-radius, 8px);
  margin-top: 1rem;
}


.overall-sentiment-box {
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: var(--color-background-soft, #f8f9fa);
  border-radius: var(--joomak-border-radius-sm, 4px);
  text-align: center;
}
.overall-sentiment-box strong {
  color: var(--color-text);
}
.last-analyzed-text {
  font-size: 0.85rem;
  color: var(--color-text-mute);
  margin-top: 0.25rem;
}

.sentiment-summary-chart h4 {
  font-size: 1.25rem;
  color: var(--color-heading);
  margin-bottom: 1rem;
  text-align: center;
}
.sentiment-bars {
  display: flex;
  height: 30px;
  border-radius: var(--joomak-border-radius-sm, 4px);
  overflow: hidden;
  margin-bottom: 0.5rem;
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.075);
  background-color: var(--color-border-hover, #e9ecef);
}
.sentiment-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.8rem;
  font-weight: 500;
  padding: 0 0.5em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: width 0.5s ease-in-out;
}
.positive-bar { background-color: var(--joomak-positive, #28a745); }
.neutral-bar { background-color: var(--joomak-neutral, #ffc107); color: #333; }
.negative-bar { background-color: var(--joomak-negative, #dc3545); }

.total-comments-text {
  text-align: right;
  font-size: 0.9rem;
  color: var(--color-text-mute);
  margin-bottom: 1rem;
}
.summary-text {
  margin-top: 1rem;
  padding: 1rem;
  background-color: var(--color-background-soft);
  border-left: 3px solid var(--joomak-primary-light);
  font-style: italic;
  color: var(--color-text);
}

.refresh-button, .analyze-request-button {
    margin-left: 0; /* 위에서 group으로 묶었으므로 개별 마진 조정 */
}
.refresh-button {
  background-color: var(--joomak-info, #0dcaf0); 
  color: black;
}
.refresh-button:hover:not(:disabled) {
  background-color: var(--joomak-info-dark, #0a9cb5);
}
.analyze-request-button {
  background-color: var(--joomak-secondary, #6c757d); 
  color: white;
}
.analyze-request-button:hover:not(:disabled) {
  background-color: var(--joomak-secondary-dark, #545b62);
}


.sentiment-positive-text { color: var(--joomak-positive, #198754); font-weight: bold; }
.sentiment-negative-text { color: var(--joomak-negative, #dc3545); font-weight: bold; }
.sentiment-neutral-text { color: var(--joomak-neutral, #ffc107); font-weight: bold; } /* '혼재됨'도 이 색상 사용 */
.sentiment-unknown {color: var(--color-text-mute, #6c757d); }


.spinner-animation {
  display: inline-block;
  width: 1em;
  height: 1em;
  border: 2px solid currentColor; 
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin-animation 0.75s linear infinite;
  margin-right: 0.5em;
  vertical-align: middle;
}
.action-button .spinner-animation {
   border-color: white; /* 버튼 내 스피너 색상 */
   border-right-color: transparent;
}
</style>