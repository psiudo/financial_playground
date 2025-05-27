<!-- frontpjt/src/views/StrategyCreateView.vue -->
<template>
  <div class="strategy-create-view">
    <h1>새 투자 전략 만들기</h1>
    <form @submit.prevent="handleCreateStrategy">
      <div class="form-group">
        <label for="name">전략 이름 (필수):</label>
        <input type="text" id="name" v-model="strategy.name" required />
      </div>
      <div class="form-group">
        <label for="description">설명:</label>
        <textarea id="description" v-model="strategy.description" rows="3"></textarea>
      </div>
      <div class="form-group">
        <label for="rule_json">규칙 (JSON 형식, 필수):</label>
        <textarea id="rule_json" v-model="strategy.rule_json_text" rows="10" placeholder='예시: {"buy_conditions": [{"indicator": "PER", "value": 10, "operator": "<"}]}' required></textarea>
        <small v-if="jsonError" class="error-message json-error">{{ jsonError }}</small>
      </div>
      <div class="form-group checkbox-group">
        <input type="checkbox" id="is_public" v-model="strategy.is_public" />
        <label for="is_public">공개 전략 (다른 사용자에게 보임)</label>
      </div>
      <div class="form-group checkbox-group">
        <input type="checkbox" id="is_paid" v-model="strategy.is_paid" />
        <label for="is_paid">유료 전략 (마켓플레이스 판매용)</label>
      </div>
      <div class="form-group" v-if="strategy.is_paid">
        <label for="price_point">판매 가격 (포인트, 필수):</label>
        <input type="number" id="price_point" v-model.number="strategy.price_point" min="0" :required="strategy.is_paid" />
      </div>

      <button type="submit" :disabled="creating">전략 생성</button>
      <p v-if="createError" class="error-message">{{ createError }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/utils/api';

const router = useRouter();
const strategy = ref({
  name: '',
  description: '',
  rule_json_text: '', // 사용자가 입력할 JSON 문자열
  rule_json: {},      // 실제 API로 보낼 파싱된 JSON 객체
  is_public: false,
  is_paid: false,
  price_point: 0,
});
const creating = ref(false);
const createError = ref(null);
const jsonError = ref(null);

const handleCreateStrategy = async () => {
  creating.value = true;
  createError.value = null;
  jsonError.value = null;

  // Rule JSON 파싱 및 유효성 검사
  try {
    strategy.value.rule_json = JSON.parse(strategy.value.rule_json_text);
  } catch (e) {
    jsonError.value = '규칙(JSON) 형식이 올바르지 않습니다. JSON 문법을 확인해주세요.';
    creating.value = false;
    return;
  }

  // 유료 전략인데 가격이 0이거나 설정 안 된 경우 방지 (모델 기본값이 0이므로, is_paid 체크 시에는 0 초과여야 함)
  if (strategy.value.is_paid && (!strategy.value.price_point || strategy.value.price_point <= 0)) {
      createError.value = '유료 전략은 판매 가격(포인트)을 0보다 큰 값으로 설정해야 합니다.';
      creating.value = false;
      return;
  }
  if (!strategy.value.is_paid) { // 유료가 아니면 가격은 0
      strategy.value.price_point = 0;
  }


  // API로 전송할 데이터 준비 (rule_json_text 대신 rule_json 사용)
  const payload = {
      name: strategy.value.name,
      description: strategy.value.description,
      rule_json: strategy.value.rule_json,
      is_public: strategy.value.is_public,
      is_paid: strategy.value.is_paid,
      price_point: strategy.value.price_point,
  };

  try {
    const response = await api.post('/strategies/strategies/', payload); // 백엔드 API 경로 확인
    alert('새로운 투자 전략이 성공적으로 생성되었습니다!');
    router.push({ name: 'StrategyListView' }); // 나의 전략 목록 페이지로 이동 (라우터 이름 확인 필요)
  } catch (err) {
    console.error('전략 생성 실패:', err);
    if (err.response && err.response.data) {
        // DRF 유효성 검사 오류 처리
        let errorMessage = '전략 생성에 실패했습니다. 입력 내용을 확인해주세요.';
        const errors = err.response.data;
        const errorKeys = Object.keys(errors);
        if (errorKeys.length > 0) {
            const firstErrorField = errorKeys[0];
            errorMessage = `${firstErrorField}: ${errors[firstErrorField][0]}`;
        }
        createError.value = errorMessage;
    } else {
        createError.value = '전략 생성 중 오류가 발생했습니다.';
    }
  } finally {
    creating.value = false;
  }
};
</script>

<style scoped>
.strategy-create-view {
  max-width: 600px;
  margin: 20px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
}
.form-group {
  margin-bottom: 15px;
}
.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}
.form-group input[type="text"],
.form-group input[type="number"],
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}
.form-group textarea {
    font-family: monospace; /* JSON 가독성을 위해 */
}
.checkbox-group label {
    font-weight: normal;
    margin-left: 5px;
}
.checkbox-group input[type="checkbox"] {
    vertical-align: middle;
}
button[type="submit"] {
  background-color: #28a745;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button[type="submit"]:disabled {
  background-color: #aaa;
}
.error-message {
  color: red;
  margin-top: 5px;
  font-size: 0.9em;
}
.json-error {
    margin-top: 2px;
    font-size: 0.8em;
}
</style>