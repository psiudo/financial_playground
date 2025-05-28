<!-- frontpjt/src/views/StrategyListView.vue -->
<template>
  <div class="strategy-list-view">
    <h1>나의 투자 전략 목록</h1>
    <router-link to="/strategies/create" class="create-strategy-btn">새 전략 만들기</router-link>

    <div v-if="loading" class="loading-spinner">로딩 중...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div class="strategies-grid" v-if="!loading && !error && strategies.length > 0">
      <div v-for="strategy in strategies" :key="strategy.id" class="strategy-card">
        <h2>{{ strategy.name }}</h2>
        <p class="description">{{ strategy.description || '설명이 없습니다.' }}</p>
        
        <div class="rule-json-preview">
          <strong>규칙:</strong>
          <RuleDisplay :rules="strategy.rule_json" />
        </div>

        <p><small>공개: {{ strategy.is_public ? '예' : '아니오' }} | 유료: {{ strategy.is_paid ? '예 (' + strategy.price_point + 'P)' : '아니오' }}</small></p>
        <p><small>생성일: {{ formatDate(strategy.created_at) }}</small></p>
        <router-link :to="{ name: 'StrategyDetailView', params: { strategyId: strategy.id } }" class="details-btn">
          상세보기 및 수정
        </router-link>
      </div>
    </div>
    <p v-if="!loading && !error && strategies.length === 0">
      아직 생성한 투자 전략이 없습니다. 새 전략을 만들어보세요!
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { RouterLink } from 'vue-router';
import api from '@/utils/api';
import RuleDisplay from '@/components/RuleDisplay.vue';

const strategies = ref([]);
const loading = ref(true);
const error = ref(null);

const fetchStrategies = async () => {
  loading.value = true;
  error.value = null;
  try {
    // ★★★ API 경로 수정: 'v1/' 및 백엔드 urls.py에 정의된 'strategies/' 추가 ★★★
    const response = await api.get('v1/strategies/strategies/'); // 수정된 경로
    
    let strategiesData = [];
    if (response.data && Array.isArray(response.data.results)) { // 페이지네이션 응답 가정
        strategiesData = response.data.results;
    } else if (response.data && Array.isArray(response.data)) { // 직접 배열 응답 가정
        strategiesData = response.data;
    } else {
        console.warn('Unexpected strategies API response structure:', response.data);
    }
    strategies.value = strategiesData;

    // ... (데이터 로깅 부분은 필요시 유지) ...
  } catch (err) {
    console.error('나의 전략 목록 조회 실패:', err.response?.data || err.message);
    if (err.response && err.response.status === 401) {
        error.value = '전략 목록을 보려면 로그인이 필요합니다.';
    } else {
        error.value = `전략 목록을 불러오는 데 실패했습니다: ${err.response?.data?.detail || err.message}`;
    }
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateString) => {
  if (!dateString) return '날짜 정보 없음';
  const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return new Date(dateString).toLocaleDateString('ko-KR', options);
};

onMounted(() => {
  // authStore 등을 통해 로그인 여부 확인 후 호출하는 것이 더 좋습니다.
  // 여기서는 로컬 스토리지 토큰 유무로 간략히 확인합니다.
  const token = localStorage.getItem('token'); 
  if (token) {
    fetchStrategies();
  } else {
    error.value = '전략 목록을 보려면 로그인이 필요합니다. 먼저 로그인해주세요.';
    loading.value = false;
    // Optional: Redirect to login
    // import { useRouter } from 'vue-router';
    // const router = useRouter();
    // router.push({ name: 'LoginView' });
  }
});
</script>


<style scoped>
.strategy-list-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
.strategy-list-view h1 {
  color: var(--joomak-text-strong);
  margin-bottom: 1.5rem;
  text-align: center;
}
.create-strategy-btn {
  display: inline-block;
  background-color: var(--joomak-primary, #007bff);
  color: var(--joomak-text-on-primary, white);
  padding: 10px 15px;
  margin-bottom: 20px;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.3s;
}
.create-strategy-btn:hover {
  background-color: var(--joomak-primary-dark, #0056b3);
}
.strategies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}
.strategy-card {
  border: 1px solid var(--joomak-border-subtle, #ddd);
  padding: 20px;
  border-radius: 8px;
  background-color: var(--joomak-surface, #f9f9f9);
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
}
.strategy-card h2 {
  margin-top: 0;
  font-size: 1.4em;
  color: var(--joomak-text-strong);
}
.strategy-card .description {
    color: var(--joomak-text-body, #555);
    font-size: 0.9em;
    min-height: 3em; 
    line-height: 1.5;
    margin-bottom: 10px;
}
.strategy-card .rule-json-preview {
    font-size: 0.85em;
    background-color: var(--joomak-background-mute, #f0f2f5);
    padding: 10px;
    border-radius: 4px;
    margin-top: 10px;
    margin-bottom: 10px;
    flex-grow: 1; 
    border: 1px solid var(--joomak-border-subtle, #e0e0e0);
}
.strategy-card .rule-json-preview strong {
  display: block;
  margin-bottom: 5px;
  color: var(--joomak-text-strong);
}
.strategy-card p small {
  font-size: 0.8em;
  color: var(--joomak-text-muted);
}
.details-btn {
  display: inline-block;
  margin-top: 15px; 
  padding: 8px 12px;
  background-color: var(--joomak-accent, #5cb85c);
  color: var(--joomak-text-on-accent, white);
  text-decoration: none;
  border-radius: 4px;
  align-self: flex-start; 
  transition: background-color 0.3s;
}
.details-btn:hover {
  background-color: var(--joomak-accent-dark, #4cae4c);
}
.loading-spinner, .error-message {
  text-align: center;
  margin-top: 20px;
  font-size: 1.2em;
  padding: 20px;
}
.error-message {
  color: #dc3545;
}
</style>