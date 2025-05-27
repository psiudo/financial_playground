<template>
  <div class="strategy-detail-view">
    <div v-if="loading" class="loading-spinner">로딩 중...</div>
    <div v-else-if="fetchError" class="error-message fetch-error-section">
      <p>{{ fetchError }}</p>
      <RouterLink :to="{ name: 'StrategyListView' }" class="btn btn-secondary btn-sm">나의 전략 목록으로</RouterLink>
    </div>

    <form v-else-if="editableStrategy && !loading" @submit.prevent="handleUpdateStrategy">
      <h1>전략 상세 및 수정</h1>
      <div class="form-group">
        <label for="name_edit">전략 이름 (필수):</label>
        <input type="text" id="name_edit" v-model="editableStrategy.name" required />
      </div>
      <div class="form-group">
        <label for="description_edit">설명:</label>
        <textarea id="description_edit" v-model="editableStrategy.description" rows="3"></textarea>
      </div>
      <div class="form-group">
        <label for="rule_json_edit">규칙 (JSON 형식, 필수):</label>
        <textarea id="rule_json_edit" v-model="editableStrategy.rule_json_text" rows="10" required></textarea>
          <small v-if="jsonError" class="error-message json-error">{{ jsonError }}</small>
      </div>
        <div class="form-group checkbox-group">
        <input type="checkbox" id="is_public_edit" v-model="editableStrategy.is_public" />
        <label for="is_public_edit">공개 전략</label>
      </div>
      <div class="form-group checkbox-group">
        <input type="checkbox" id="is_paid_edit" v-model="editableStrategy.is_paid" />
        <label for="is_paid_edit">유료 전략</label>
      </div>
      <div class="form-group" v-if="editableStrategy.is_paid">
        <label for="price_point_edit">판매 가격 (포인트, 필수):</label>
        <input type="number" id="price_point_edit" v-model.number="editableStrategy.price_point" min="1" :required="editableStrategy.is_paid" />
      </div>

      <div class="actions">
        <button type="submit" :disabled="updating || deleting" class="submit-btn">
          <span v-if="updating" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          {{ updating ? '수정 중...' : '수정 완료' }}
        </button>
        <button type="button" @click="handleDeleteStrategy" :disabled="deleting || updating" class="delete-btn">
          <span v-if="deleting" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          {{ deleting ? '삭제 중...' : '전략 삭제' }}
        </button>
        </div>
      <p v-if="updateError" class="error-message api-error">{{ updateError }}</p>
    </form>
     <div v-else-if="!loading && !strategy" class="error-message fetch-error-section">
      <p>전략 정보를 찾을 수 없습니다.</p>
       <RouterLink :to="{ name: 'StrategyListView' }" class="btn btn-secondary btn-sm">나의 전략 목록으로</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, reactive } from 'vue'; // reactive 추가
import { useRoute, useRouter, RouterLink } from 'vue-router';
import api from '@/utils/api';
// RuleDisplay는 이 뷰에서 직접 사용하지 않음 (수정 폼이므로)

const route = useRoute();
const router = useRouter();
const strategyId = ref(route.params.strategyId);

// editableStrategy를 reactive 객체로 변경
const editableStrategy = reactive({ 
    name: '',
    description: '',
    rule_json_text: '', // 사용자가 편집하는 JSON 문자열
    rule_json: {},      // API로 보낼 파싱된 JSON 객체
    is_public: false,
    is_paid: false,
    price_point: 0,
}); 
const originalStrategy = ref(null); // API로부터 받은 원본 데이터 저장용

const loading = ref(true);
const fetchError = ref(null);
const updating = ref(false);
const updateError = ref(null);
const deleting = ref(false);
const jsonError = ref(null);

const populateEditableStrategy = (sourceStrategy) => {
    if (!sourceStrategy) return;
    editableStrategy.name = sourceStrategy.name || '';
    editableStrategy.description = sourceStrategy.description || '';
    // rule_json을 문자열로 변환하여 textarea에 표시하고, 객체도 내부적으로 유지
    editableStrategy.rule_json = sourceStrategy.rule_json || {};
    editableStrategy.rule_json_text = JSON.stringify(sourceStrategy.rule_json || {}, null, 2);
    editableStrategy.is_public = sourceStrategy.is_public || false;
    editableStrategy.is_paid = sourceStrategy.is_paid || false;
    editableStrategy.price_point = sourceStrategy.price_point || 0;
};

const fetchStrategyDetail = async () => {
  loading.value = true;
  fetchError.value = null;
  try {
    const response = await api.get(`/strategies/strategies/${strategyId.value}/`);
    originalStrategy.value = response.data; // 원본 저장
    populateEditableStrategy(response.data); // 수정용 데이터에 복사
  } catch (err) {
    console.error('전략 상세 정보 조회 실패:', err);
    if (err.response) {
        if (err.response.status === 404) {
            fetchError.value = '해당 전략을 찾을 수 없습니다.';
        } else if (err.response.status === 401 || err.response.status === 403) {
            fetchError.value = '이 전략을 보거나 수정할 권한이 없습니다.';
        } else {
            fetchError.value = `전략 상세 정보를 불러오는 데 실패했습니다. (상태: ${err.response.status})`;
        }
    } else {
        fetchError.value = '전략 상세 정보를 불러오는 중 네트워크 오류가 발생했습니다.';
    }
  } finally {
    loading.value = false;
  }
};

const handleUpdateStrategy = async () => {
  updating.value = true;
  updateError.value = null;
  jsonError.value = null;

  try {
    // textarea의 문자열을 JSON 객체로 파싱하여 rule_json에 저장
    editableStrategy.rule_json = JSON.parse(editableStrategy.rule_json_text);
  } catch (e) {
    jsonError.value = '규칙(JSON) 형식이 올바르지 않습니다. JSON 문법을 확인해주세요.';
    updating.value = false;
    return;
  }

  if (editableStrategy.is_paid && (!editableStrategy.price_point || editableStrategy.price_point <= 0)) {
      updateError.value = '유료 전략은 판매 가격(포인트)을 1 이상의 값으로 설정해야 합니다.';
      updating.value = false;
      return;
  }
  if (!editableStrategy.is_paid) {
      editableStrategy.price_point = 0; // 유료가 아니면 가격 0으로 설정
  }

  // API로 전송할 payload (reactive 객체의 현재 값을 사용)
  const payload = {
      name: editableStrategy.name,
      description: editableStrategy.description,
      rule_json: editableStrategy.rule_json, // 파싱된 JSON 객체
      is_public: editableStrategy.is_public,
      is_paid: editableStrategy.is_paid,
      price_point: editableStrategy.price_point,
  };

  try {
    await api.put(`/strategies/strategies/${strategyId.value}/`, payload);
    alert('전략이 성공적으로 수정되었습니다!');
    // 수정 후, 다시 상세 정보를 불러오거나 목록으로 이동할 수 있음
    fetchStrategyDetail(); // 최신 정보로 폼 다시 채우기
    // router.push({ name: 'StrategyListView' }); 
  } catch (err) {
    console.error('전략 수정 실패:', err.response?.data || err.message);
    if (err.response && err.response.data) {
        let errorMessage = '전략 수정에 실패했습니다. 입력 내용을 확인해주세요.';
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
        updateError.value = errorMessage;
    } else {
        updateError.value = '전략 수정 중 알 수 없는 오류가 발생했습니다.';
    }
  } finally {
    updating.value = false;
  }
};

const handleDeleteStrategy = async () => {
  if (confirm('정말로 이 전략을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
    deleting.value = true;
    updateError.value = null; 
    try {
      await api.delete(`/strategies/strategies/${strategyId.value}/`);
      alert('전략이 성공적으로 삭제되었습니다.');
      router.push({ name: 'StrategyListView' });
    } catch (err) {
      console.error('전략 삭제 실패:', err.response?.data || err.message);
      if (err.response && (err.response.status === 401 || err.response.status === 403)) {
        updateError.value = '이 전략을 삭제할 권한이 없습니다.';
      } else {
        updateError.value = '전략 삭제 중 오류가 발생했습니다.';
      }
    } finally {
      deleting.value = false;
    }
  }
};

onMounted(() => {
  fetchStrategyDetail();
});

watch(() => route.params.strategyId, (newId) => {
    if (newId && newId !== strategyId.value) {
        strategyId.value = newId;
        fetchStrategyDetail();
    }
});
</script>

<style scoped>
/* StrategyCreateView와 유사한 스타일 적용 */
.strategy-detail-view {
  max-width: 700px;
  margin: 30px auto;
  padding: 25px;
  border: 1px solid var(--joomak-border-subtle, #ccc);
  border-radius: 8px;
  background-color: var(--joomak-surface, #fff);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.strategy-detail-view h1 {
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
  background-color: var(--joomak-background-main);
}
.form-group input[type="text"]:focus,
.form-group input[type="number"]:focus,
.form-group textarea:focus {
  border-color: var(--joomak-primary);
  box-shadow: 0 0 0 0.2rem rgba(var(--joomak-primary-rgb, 58, 95, 205), 0.25);
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
    width: auto;
    vertical-align: middle;
    transform: scale(1.1);
}
.checkbox-group label {
    font-weight: normal;
    margin-bottom: 0;
}
.actions {
  display: flex;
  gap: 10px; /* 버튼 사이 간격 */
  margin-top: 25px;
}
.actions button {
  flex-grow: 1; /* 버튼들이 공간을 균등하게 차지하도록 */
  padding: 12px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.05rem;
  transition: background-color 0.3s, opacity 0.3s;
}
.actions .submit-btn {
  background-color: var(--joomak-primary, #28a745);
  color: var(--joomak-text-on-primary, white);
}
.actions .submit-btn:hover:not(:disabled) {
  background-color: var(--joomak-primary-dark);
}
.actions .delete-btn {
  background-color: #dc3545; /* Bootstrap danger color */
  color: white;
}
.actions .delete-btn:hover:not(:disabled) {
  background-color: #c82333; /* Darker danger */
}
.actions button:disabled {
  background-color: #aaa;
  opacity: 0.7;
  cursor: not-allowed;
}
.error-message {
  color: #dc3545;
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
    background-color: rgba(220, 53, 69, 0.1);
    border: 1px solid rgba(220, 53, 69, 0.2);
    border-radius: 4px;
}
.fetch-error-section {
  padding: 20px;
  text-align: center;
  background-color: var(--joomak-background-mute, #f8f9fa);
  border-radius: 8px;
}
.fetch-error-section p {
  margin-bottom: 15px;
}
.loading-spinner {
  text-align: center;
  padding: 30px;
  font-size: 1.2em;
}
</style>