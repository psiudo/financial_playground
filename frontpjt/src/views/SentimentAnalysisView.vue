<!-- frontpjt/src/views/SentimentAnalysisView.vue -->
<template>
  <div class="sentiment-analysis-container view-container">
    <h2 class="view-title">텍스트 감정 분석</h2>
    <p class="view-description">분석하고 싶은 문장을 입력하고 결과를 확인해보세요.</p>

    <form @submit.prevent="handleAnalysisSubmit" class="analysis-form">
      <textarea
        v-model="textToAnalyze"
        placeholder="여기에 분석할 텍스트를 입력하세요..."
        rows="6"
        class="form-textarea"
        :disabled="sentimentStore.isLoading"
      ></textarea>
      <button type="submit" class="submit-button" :disabled="sentimentStore.isLoading || !textToAnalyze.trim()">
        <span v-if="sentimentStore.isLoading" class="spinner-animation"></span>
        <span v-else>분석하기</span>
      </button>
    </form>

    <div v-if="sentimentStore.isLoading" class="message-box loading-box">
      <p>텍스트를 분석하고 있습니다. 잠시만 기다려 주세요...</p>
    </div>

    <div v-if="sentimentStore.error" class="message-box error-box">
      <p><strong>오류:</strong> {{ sentimentStore.error }}</p>
    </div>

    <div v-if="sentimentStore.sentimentResult && !sentimentStore.isLoading" class="result-display-section">
      <h3 class="result-title">분석 결과</h3>
      <div class="result-card">
        <p class="analyzed-text-label"><strong>입력 내용:</strong></p>
        <blockquote class="analyzed-text-content">"{{ sentimentStore.analyzedText }}"</blockquote>
        
        <p class="sentiment-label"><strong>분석된 감정:</strong></p>
        <p class="sentiment-value" :class="sentimentVisualClass(sentimentStore.sentimentResult)">
          {{ translateSentiment(sentimentStore.sentimentResult) }}
          <span class="sentiment-emoji">{{ getSentimentEmoji(sentimentStore.sentimentResult) }}</span>
        </p>
      </div>
      <button @click="resetAnalysis" class="reset-button">새로운 분석하기</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue';
import { useSentimentStore } from '@/stores/sentimentStore';

const sentimentStore = useSentimentStore();
const textToAnalyze = ref(''); // 사용자가 입력할 텍스트

// 분석 요청 핸들러
const handleAnalysisSubmit = () => {
  if (textToAnalyze.value.trim()) {
    sentimentStore.analyzeText(textToAnalyze.value);
  }
};

// 결과 및 입력 초기화 핸들러
const resetAnalysis = () => {
  sentimentStore.clearAnalysis();
  textToAnalyze.value = '';
};

// 감정 결과 영문 -> 한글 번역
const translateSentiment = (sentiment) => {
  if (!sentiment) return '';
  const sentimentLower = sentiment.toLowerCase();
  switch (sentimentLower) {
    case 'positive':
      return '긍정적';
    case 'negative':
      return '부정적';
    case 'neutral':
      return '중립적';
    default:
      return sentiment; // 알 수 없는 경우 원본 반환
  }
};

// 감정 결과에 따른 이모지 반환
const getSentimentEmoji = (sentiment) => {
  if (!sentiment) return '🤔';
  const sentimentLower = sentiment.toLowerCase();
  switch (sentimentLower) {
    case 'positive':
      return '😊';
    case 'negative':
      return '😠';
    case 'neutral':
      return '😐';
    default:
      return '💬';
  }
};

// 감정 결과에 따른 시각적 스타일 클래스 반환
const sentimentVisualClass = (sentiment) => {
  if (!sentiment) return '';
  const sentimentLower = sentiment.toLowerCase();
  return {
    'sentiment-positive-text': sentimentLower === 'positive',
    'sentiment-negative-text': sentimentLower === 'negative',
    'sentiment-neutral-text': sentimentLower === 'neutral',
  };
};

// 컴포넌트가 화면에서 사라질 때 스토어 상태 초기화 (다른 페이지 이동 시 영향 없도록)
onUnmounted(() => {
  sentimentStore.clearAnalysis();
});
</script>

<style scoped>
/* Joomak 테마의 CSS 변수를 사용하도록 스타일을 구성합니다. 
   실제 변수명은 프로젝트의 main.css 또는 base.css 등을 참고해야 합니다.
   여기서는 예상되는 변수명을 사용합니다. */

.view-container { /* 전체 뷰 컨테이너 스타일 */
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: var(--color-background, #fff); /* Joomak 배경색 */
  border-radius: var(--joomak-border-radius, 8px); /* Joomak 테두리 둥글기 */
  box-shadow: var(--joomak-shadow-md, 0 4px 12px rgba(0,0,0,0.1));
}

.view-title {
  font-size: 2rem; /* App.vue의 .site-title 크기와 유사하게 */
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

.analysis-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2.5rem;
}

.form-textarea {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1px solid var(--color-border, #ced4da);
  border-radius: var(--joomak-border-radius-sm, 4px);
  font-size: 1rem;
  line-height: 1.6;
  resize: vertical;
  min-height: 120px;
  background-color: var(--color-background-soft, #f8f9fa);
  color: var(--color-text);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-textarea:focus {
  outline: none;
  border-color: var(--joomak-primary, #3a5fcd);
  box-shadow: 0 0 0 0.2rem rgba(var(--joomak-primary-rgb, 58, 95, 205), 0.25);
}

.submit-button {
  padding: 0.8rem 1.5rem;
  background-color: var(--joomak-primary, #3a5fcd);
  color: white;
  border: none;
  border-radius: var(--joomak-border-radius-sm, 4px);
  font-size: 1.1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease-in-out;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 46px; /* 로딩 스피너 공간 확보 */
}

.submit-button:hover:not(:disabled) {
  background-color: var(--joomak-primary-dark, #2c4aa0);
}

.submit-button:disabled {
  background-color: var(--color-border-hover, #e9ecef);
  color: var(--color-text-mute, #6c757d);
  cursor: not-allowed;
}

.spinner-animation {
  display: inline-block;
  width: 1.2em;
  height: 1.2em;
  border: 3px solid rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin-animation 0.8s ease-in-out infinite;
}

@keyframes spin-animation {
  to { transform: rotate(360deg); }
}

.message-box {
  text-align: center;
  padding: 1.25rem;
  border-radius: var(--joomak-border-radius-sm, 4px);
  margin-bottom: 2rem;
  font-size: 1rem;
}

.loading-box {
  background-color: var(--color-background-mute, #e9ecef);
  color: var(--color-text);
  border: 1px solid var(--color-border, #dee2e6);
}

.error-box {
  background-color: #f8d7da; /* Bootstrap danger background */
  color: #721c24; /* Bootstrap danger text */
  border: 1px solid #f5c6cb; /* Bootstrap danger border */
}

.result-display-section {
  margin-top: 2.5rem;
  border-top: 1px solid var(--color-border, #dee2e6);
  padding-top: 2.5rem;
}

.result-title {
  font-size: 1.5rem;
  color: var(--color-heading);
  text-align: center;
  margin-bottom: 1.5rem;
}

.result-card {
  background-color: var(--color-background-soft, #f8f9fa);
  padding: 2rem;
  border-radius: var(--joomak-border-radius, 8px);
  margin-bottom: 2rem;
  box-shadow: var(--joomak-shadow-sm, 0 2px 6px rgba(0,0,0,0.05));
}

.analyzed-text-label {
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.analyzed-text-content {
  font-style: italic;
  color: var(--color-text-mute, #495057);
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: var(--color-background, #fff);
  border-left: 4px solid var(--color-border, #ced4da);
  border-radius: 0 var(--joomak-border-radius-sm, 4px) var(--joomak-border-radius-sm, 4px) 0;
  word-break: break-word;
}

.sentiment-label {
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.sentiment-value {
  font-size: 1.4rem;
  font-weight: bold;
  padding: 0.5rem 0;
}

.sentiment-positive-text { color: var(--joomak-positive, #28a745); }
.sentiment-negative-text { color: var(--joomak-negative, #dc3545); }
.sentiment-neutral-text { color: var(--joomak-neutral, #ffc107); }
.sentiment-emoji { margin-left: 0.5em; font-size: 1.2em; vertical-align: middle;}

.reset-button {
  display: block;
  margin: 2rem auto 0;
  padding: 0.75rem 1.5rem;
  background-color: var(--color-border-hover, #6c757d);
  color: var(--color-background, #fff);
  border: none;
  border-radius: var(--joomak-border-radius-sm, 4px);
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}
.reset-button:hover {
  background-color: var(--color-text-mute, #5a6268);
}
</style>