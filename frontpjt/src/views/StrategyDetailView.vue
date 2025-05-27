<template>
    <div class="strategy-detail-view">
      <div v-if="loading" class="loading-spinner">로딩 중...</div>
      <div v-if="fetchError" class="error-message">{{ fetchError }}</div>
  
      <form v-if="strategy && !loading" @submit.prevent="handleUpdateStrategy">
        <h1>전략 상세 및 수정</h1>
        <div class="form-group">
          <label for="name">전략 이름 (필수):</label>
          <input type="text" id="name" v-model="editableStrategy.name" required />
        </div>
        <div class="form-group">
          <label for="description">설명:</label>
          <textarea id="description" v-model="editableStrategy.description" rows="3"></textarea>
        </div>
        <div class="form-group">
          <label for="rule_json">규칙 (JSON 형식, 필수):</label>
          <textarea id="rule_json" v-model="editableStrategy.rule_json_text" rows="10" required></textarea>
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
          <input type="number" id="price_point_edit" v-model.number="editableStrategy.price_point" min="0" :required="editableStrategy.is_paid" />
        </div>
  
        <div class="actions">
          <button type="submit" :disabled="updating">수정 완료</button>
          <button type="button" @click="handleDeleteStrategy" :disabled="deleting" class="delete-btn">전략 삭제</button>
          </div>
        <p v-if="updateError" class="error-message">{{ updateError }}</p>
      </form>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, watch } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import api from '@/utils/api';
  
  const route = useRoute();
  const router = useRouter();
  const strategyId = ref(route.params.strategyId);
  const strategy = ref(null); // 원본 데이터
  const editableStrategy = ref({ // 수정을 위한 복사본
      name: '',
      description: '',
      rule_json_text: '',
      rule_json: {},
      is_public: false,
      is_paid: false,
      price_point: 0,
  }); 
  
  const loading = ref(true);
  const fetchError = ref(null);
  const updating = ref(false);
  const updateError = ref(null);
  const deleting = ref(false);
  const running = ref(false); // 시뮬레이션 실행 로딩 상태
  const jsonError = ref(null);
  
  
  const fetchStrategyDetail = async () => {
    loading.value = true;
    fetchError.value = null;
    try {
      const response = await api.get(`/strategies/strategies/${strategyId.value}/`);
      strategy.value = response.data;
      // 수정용 데이터 복사
      editableStrategy.value.name = strategy.value.name;
      editableStrategy.value.description = strategy.value.description;
      editableStrategy.value.rule_json_text = JSON.stringify(strategy.value.rule_json, null, 2); // JSON을 문자열로 변환하여 textarea에 표시
      editableStrategy.value.rule_json = strategy.value.rule_json; // 원본 JSON 객체도 유지
      editableStrategy.value.is_public = strategy.value.is_public;
      editableStrategy.value.is_paid = strategy.value.is_paid;
      editableStrategy.value.price_point = strategy.value.price_point;
  
    } catch (err) {
      console.error('전략 상세 정보 조회 실패:', err);
      if (err.response && err.response.status === 404) {
          fetchError.value = '해당 전략을 찾을 수 없습니다.';
      } else if (err.response && err.response.status === 401) {
          fetchError.value = '전략 정보를 보려면 로그인이 필요합니다.';
      }
      else {
          fetchError.value = '전략 상세 정보를 불러오는 데 실패했습니다.';
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
      editableStrategy.value.rule_json = JSON.parse(editableStrategy.value.rule_json_text);
    } catch (e) {
      jsonError.value = '규칙(JSON) 형식이 올바르지 않습니다.';
      updating.value = false;
      return;
    }
  
    if (editableStrategy.value.is_paid && (!editableStrategy.value.price_point || editableStrategy.value.price_point <= 0)) {
        updateError.value = '유료 전략은 판매 가격(포인트)을 0보다 큰 값으로 설정해야 합니다.';
        updating.value = false;
        return;
    }
     if (!editableStrategy.value.is_paid) {
        editableStrategy.value.price_point = 0;
    }
  
    const payload = {
        name: editableStrategy.value.name,
        description: editableStrategy.value.description,
        rule_json: editableStrategy.value.rule_json,
        is_public: editableStrategy.value.is_public,
        is_paid: editableStrategy.value.is_paid,
        price_point: editableStrategy.value.price_point,
    };
  
    try {
      await api.put(`/strategies/strategies/${strategyId.value}/`, payload); // 또는 PATCH
      alert('전략이 성공적으로 수정되었습니다!');
      router.push({ name: 'StrategyListView' }); // 목록 페이지로 이동
    } catch (err) {
      console.error('전략 수정 실패:', err);
       if (err.response && err.response.data) {
          let errorMessage = '전략 수정에 실패했습니다. 입력 내용을 확인해주세요.';
          const errors = err.response.data;
          const errorKeys = Object.keys(errors);
          if (errorKeys.length > 0) {
              const firstErrorField = errorKeys[0];
              errorMessage = `${firstErrorField}: ${errors[firstErrorField][0]}`;
          }
          updateError.value = errorMessage;
      } else {
          updateError.value = '전략 수정 중 오류가 발생했습니다.';
      }
    } finally {
      updating.value = false;
    }
  };
  
  const handleDeleteStrategy = async () => {
    if (confirm('정말로 이 전략을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
      deleting.value = true;
      updateError.value = null; // 이전 에러 메시지 초기화
      try {
        await api.delete(`/strategies/strategies/${strategyId.value}/`);
        alert('전략이 성공적으로 삭제되었습니다.');
        router.push({ name: 'StrategyListView' });
      } catch (err) {
        console.error('전략 삭제 실패:', err);
         if (err.response && err.response.status === 403) { // 본인 전략만 삭제 가능 (백엔드 권한 확인 필요)
          updateError.value = '본인 전략만 삭제할 수 있습니다.';
        } else {
          updateError.value = '전략 삭제 중 오류가 발생했습니다.';
        }
      } finally {
        deleting.value = false;
      }
    }
  };
  
  // const handleRunStrategy = async () => {
  //   running.value = true;
  //   updateError.value = null; // 이전 에러 메시지 초기화
  //   try {
  //     // 백엔드에 /api/strategies/strategies/{strategyId}/run/ API 구현 필요
  //     const response = await api.post(`/strategies/strategies/${strategyId.value}/run/`);
  //     alert('전략 시뮬레이션 실행을 요청했습니다. 완료되면 알림이 전송됩니다.'); // 또는 결과 페이지로 이동
  //     // console.log('Run strategy response:', response.data);
  //   } catch (err) {
  //     console.error('전략 실행 실패:', err);
  //     updateError.value = '전략 시뮬레이션 실행 중 오류가 발생했습니다.';
  //   } finally {
  //     running.value = false;
  //   }
  // };
  
  onMounted(() => {
    fetchStrategyDetail();
  });
  
  // strategyId가 변경될 때 다시 데이터를 가져오도록 설정 (선택 사항)
  watch(() => route.params.strategyId, (newId) => {
      if (newId && newId !== strategyId.value) {
          strategyId.value = newId;
          fetchStrategyDetail();
      }
  });
  </script>
  
  <style scoped>
  /* StrategyCreateView와 유사한 스타일 적용 가능 */
  .strategy-detail-view {
    max-width: 700px;
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
    box-sizing: border-box; /* padding과 border가 width에 포함되도록 */
  }
   .form-group textarea {
      font-family: monospace;
  }
  .checkbox-group label {
      font-weight: normal;
      margin-left: 5px;
  }
  .checkbox-group input[type="checkbox"] {
      vertical-align: middle;
  }
  .actions button {
    margin-right: 10px;
    padding: 10px 15px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  .actions button[type="submit"] {
    background-color: #28a745;
    color: white;
  }
  .actions .delete-btn {
    background-color: #dc3545;
    color: white;
  }
  .actions .run-btn {
    background-color: #17a2b8;
    color: white;
  }
  .actions button:disabled {
    background-color: #aaa;
  }
  .error-message {
    color: red;
    margin-top: 10px;
  }
   .json-error {
      margin-top: 2px;
      font-size: 0.8em;
  }
  </style>