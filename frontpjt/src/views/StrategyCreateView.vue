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
        <textarea id="rule_json" v-model="strategy.rule_json_text" rows="10" placeholder='예시: {"buy_conditions": [{"indicator": "PER", "value": 10, "operator": "<="}]}' required></textarea>
        <small v-if="jsonError" class="error-message json-error">{{ jsonError }}</small>
        <small class="form-text">매수/매도 조건을 JSON 형식으로 입력합니다. 복잡한 규칙도 정의할 수 있습니다.</small>
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
        <input type="number" id="price_point" v-model.number="strategy.price_point" min="1" :required="strategy.is_paid" />
         <small class="form-text">유료 전략으로 설정 시, 1 이상의 판매 가격을 입력해야 합니다.</small>
      </div>

      <button type="submit" :disabled="creating" class="submit-btn">
        <span v-if="creating" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        {{ creating ? '생성 중...' : '전략 생성' }}
      </button>
      <p v-if="createError" class="error-message api-error">{{ createError }}</p>
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
  rule_json_text: '', 
  rule_json: {},     
  is_public: false,
  is_paid: false,
  price_point: 0, // 유료 선택 시 1 이상이어야 함
});
const creating = ref(false);
const createError = ref(null);
const jsonError = ref(null);

const handleCreateStrategy = async () => {
  creating.value = true;
  createError.value = null;
  jsonError.value = null;

  try {
    strategy.value.rule_json = JSON.parse(strategy.value.rule_json_text);
  } catch (e) {
    jsonError.value = '규칙(JSON) 형식이 올바르지 않습니다. JSON 문법을 확인해주세요.';
    creating.value = false;
    return;
  }

  if (strategy.value.is_paid && (!strategy.value.price_point || strategy.value.price_point <= 0)) {
      createError.value = '유료 전략은 판매 가격(포인트)을 1 이상의 값으로 설정해야 합니다.';
      creating.value = false;
      return;
  }
  if (!strategy.value.is_paid) {
      strategy.value.price_point = 0;
  }

  const payload = {
      name: strategy.value.name,
      description: strategy.value.description,
      rule_json: strategy.value.rule_json,
      is_public: strategy.value.is_public,
      is_paid: strategy.value.is_paid,
      price_point: strategy.value.price_point,
  };

  try {
    const response = await api.post('/strategies/strategies/', payload);
    alert('새로운 투자 전략이 성공적으로 생성되었습니다!');
    // 생성된 전략의 상세 페이지로 이동하거나, 목록 페이지로 이동
    if (response.data && response.data.id) {
        router.push({ name: 'StrategyDetailView', params: { strategyId: response.data.id } });
    } else {
        router.push({ name: 'StrategyListView' });
    }
  } catch (err) {
    console.error('전략 생성 실패:', err.response?.data || err.message);
    if (err.response && err.response.data) {
        let errorMessage = '전략 생성에 실패했습니다. 입력 내용을 확인해주세요.';
        const errors = err.response.data;
        const errorMessages = [];
        for (const key in errors) {
            if (Array.isArray(errors[key])) {
                errorMessages.push(`${key}: ${errors[key].join(', ')}`);
            } else {
                errorMessages.push(`${key}: ${errors[key]}`);
            }
        }
        if (errorMessages.length > 0) {
            errorMessage = errorMessages.join(' | ');
        }
        createError.value = errorMessage;
    } else {
        createError.value = '전략 생성 중 알 수 없는 오류가 발생했습니다.';
    }
  } finally {
    creating.value = false;
  }
};
</script>

<style scoped>
.strategy-create-view {
  max-width: 700px;
  margin: 30px auto;
  padding: 25px;
  border: 1px solid var(--joomak-border-subtle, #ccc);
  border-radius: 8px;
  background-color: var(--joomak-surface, #fff);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.strategy-create-view h1 {
  text-align: center;
  color: var(--joomak-text-strong);
  margin-bottom: 25px;
}
.form-group {
  margin-bottom: 20px;
}
.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: var(--joomak-text-body);
}
.form-group input[type="text"],
.form-group input[type="number"],
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--joomak-border-subtle, #ddd);
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 1rem;
  color: var(--joomak-text-body);
  background-color: var(--joomak-background-main); /* 입력 필드 배경 */
}
.form-group input[type="text"]:focus,
.form-group input[type="number"]:focus,
.form-group textarea:focus {
  border-color: var(--joomak-primary);
  box-shadow: 0 0 0 0.2rem rgba(var(--joomak-primary-rgb, 58, 95, 205), 0.25); /* Joomak RGB 변수 필요 */
  outline: none;
}
.form-group textarea {
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
    min-height: 120px;
}
.checkbox-group {
    display: flex;
    align-items: center;
}
.checkbox-group input[type="checkbox"] {
    margin-right: 8px;
    width: auto; /* 기본 너비로 */
    vertical-align: middle;
    transform: scale(1.1); /* 체크박스 크기 약간 키움 */
}
.checkbox-group label {
    font-weight: normal;
    margin-bottom: 0; /* display:flex로 인해 불필요 */
}
.submit-btn {
  background-color: var(--joomak-primary, #28a745);
  color: var(--joomak-text-on-primary, white);
  padding: 12px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.1rem;
  width: 100%;
  transition: background-color 0.3s;
}
.submit-btn:disabled {
  background-color: #aaa;
  cursor: not-allowed;
}
.submit-btn:hover:not(:disabled) {
  background-color: var(--joomak-primary-dark);
}
.error-message {
  color: #dc3545; /* Bootstrap danger color */
  margin-top: 8px;
  font-size: 0.9em;
}
.json-error {
  margin-top: 4px;
  font-size: 0.85em;
}
.api-error {
    margin-top: 15px;
    padding: 10px;
    background-color: rgba(220, 53, 69, 0.1); /* 에러 배경 */
    border: 1px solid rgba(220, 53, 69, 0.2);
    border-radius: 4px;
}
.form-text {
    font-size: 0.85em;
    color: var(--joomak-text-muted);
    display: block;
    margin-top: 5px;
}
</style>