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
          <p class="rule-json-preview">
            <strong>규칙(JSON):</strong> <code>{{ truncateJson(strategy.rule_json) }}</code>
          </p>
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
  
  const strategies = ref([]);
  const loading = ref(true);
  const error = ref(null);
  
  const fetchStrategies = async () => {
    loading.value = true;
    error.value = null;
    try {
      // MarketplaceView에서 확인된 사용자 전략 목록 API 경로 사용
      const response = await api.get('/strategies/strategies/'); 
  
      if (response.data && Array.isArray(response.data)) {
          strategies.value = response.data;
      } else if (response.data && response.data.results && Array.isArray(response.data.results)) {
          strategies.value = response.data.results; // 페이지네이션된 경우
      } else {
          strategies.value = [];
          console.warn('Unexpected strategies API response structure:', response.data);
      }
    } catch (err) {
      console.error('나의 전략 목록 조회 실패:', err);
      if (err.response && err.response.status === 401) {
          error.value = '전략 목록을 보려면 로그인이 필요합니다.';
      } else {
          error.value = '전략 목록을 불러오는 데 실패했습니다.';
      }
    } finally {
      loading.value = false;
    }
  };
  
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString('ko-KR', options);
  };
  
  const truncateJson = (jsonObj) => {
      const jsonString = typeof jsonObj === 'string' ? jsonObj : JSON.stringify(jsonObj);
      return jsonString.length > 100 ? jsonString.substring(0, 97) + '...' : jsonString;
  };
  
  onMounted(() => {
    // 로그인 상태를 확인하고, 로그인 되어있으면 전략 목록을 가져옵니다.
    // 이 부분은 App.vue의 isLoggedIn과 유사하게 토큰 유무로 판단하거나 Pinia 스토어를 사용할 수 있습니다.
    const token = localStorage.getItem('token');
    if (token) {
      fetchStrategies();
    } else {
      error.value = '전략 목록을 보려면 로그인이 필요합니다.';
      loading.value = false;
      // router.push('/login'); // 로그인 페이지로 강제 이동시킬 수도 있습니다.
    }
  });
  </script>
  
  <style scoped>
  .strategy-list-view {
    padding: 20px;
  }
  .create-strategy-btn {
    display: inline-block;
    background-color: #007bff;
    color: white;
    padding: 10px 15px;
    margin-bottom: 20px;
    text-decoration: none;
    border-radius: 4px;
  }
  .create-strategy-btn:hover {
    background-color: #0056b3;
  }
  .strategies-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
  }
  .strategy-card {
    border: 1px solid #ddd;
    padding: 15px;
    border-radius: 8px;
    background-color: #f9f9f9;
  }
  .strategy-card h2 {
    margin-top: 0;
    font-size: 1.4em;
  }
  .strategy-card .description {
      color: #555;
      font-size: 0.9em;
      min-height: 3em; /* 설명이 짧더라도 일정한 높이 유지 */
      display: -webkit-box;
      -webkit-line-clamp: 3; /* 최대 3줄까지 보이고 나머지는 ... 처리 */
      -webkit-box-orient: vertical;
      overflow: hidden;
      text-overflow: ellipsis;
  }
  .strategy-card .rule-json-preview {
      font-size: 0.85em;
      background-color: #eee;
      padding: 5px;
      border-radius: 3px;
      word-break: break-all;
  }
  .details-btn {
    display: inline-block;
    margin-top: 10px;
    padding: 8px 12px;
    background-color: #5cb85c;
    color: white;
    text-decoration: none;
    border-radius: 4px;
  }
  .details-btn:hover {
    background-color: #4cae4c;
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