<template>
  <div class="rule-display" v-if="formattedRuleBlocks.length > 0">
    <div v-for="(block, blockIndex) in formattedRuleBlocks" :key="blockIndex" class="rule-block">
      <strong class="rule-type">{{ block.type }}:</strong>
      <ul v-if="Array.isArray(block.details) && block.details.length > 0" class="condition-list">
        <li v-for="(detail, detailIndex) in block.details" :key="detailIndex" class="condition-item">
          {{ detail }}
        </li>
      </ul>
      <p v-else-if="!Array.isArray(block.details) && typeof block.details === 'string'" class="single-detail-text">
        {{ block.details }}
      </p>
      <p v-else class="no-details-message">
        <small>세부 조건이 정의되지 않았거나 표시할 수 없습니다.</small>
      </p>
    </div>
  </div>
  <div v-else-if="hasRulesButCouldNotFormat" class="rule-display-fallback">
    <small>규칙 요약 (상세 표시는 지원되지 않는 형식): <code>{{ truncateJson(rules) }}</code></small>
  </div>
  <div v-else class="rule-display-empty">
    <small>정의된 규칙이 없거나 표시할 규칙 내용이 없습니다.</small>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  rules: {
    type: Object,
    default: () => ({})
  }
});

const operatorMap = {
  '<': '보다 작을 때',
  '>': '보다 클 때',
  '<=': '보다 작거나 같을 때',
  '>=': '보다 크거나 같을 때',
  '==': '과(와) 같을 때',
  '!=': '과(와) 다를 때'
  // 필요한 다른 연산자들을 여기에 추가할 수 있습니다.
};

const formatSingleCondition = (condition, conditionIndex) => {
  if (condition && typeof condition === 'object') {
    // 로그에서 확인된 'name' 키를 'indicator'로 우선 사용
    const indicator = condition.name || condition.indicator; 
    const operator = condition.operator;
    const value = condition.value;
    const type = condition.type; // 조건 객체 내의 'type' (예: "indicator")

    if (typeof indicator === 'string' && typeof operator === 'string' && value !== undefined) {
      const operatorText = operatorMap[operator] || `(${operator})`; // 모르는 연산자는 괄호로 묶어 표시
      let valueText = value;
      let unit = '';

      // 특정 지표에 대한 단위 및 형식화
      if (typeof value === 'number') {
        if (String(indicator).includes('수익률') || String(indicator).includes('손실률') || String(indicator).includes('percentage')) {
          unit = '%';
        } else if (String(indicator).includes('balance') || String(indicator).includes('금액')) {
          valueText = value.toLocaleString('ko-KR');
          unit = '원';
        } else if (String(indicator).includes('거래량')) {
           valueText = value.toLocaleString('ko-KR');
        }
        // 다른 숫자 기반 지표에 대한 포맷팅 추가 가능
      }
      
      let typePrefix = '';
      if (type) {
        typePrefix = `[${type}] `;
      }

      return `${typePrefix}지표 '${indicator}' ${operatorText} ${valueText}${unit}`;
    } else {
      // 필수 키(name, operator, value) 중 하나라도 없거나 타입이 맞지 않는 경우
      return `조건 ${conditionIndex + 1} (형식 오류: 키 누락 또는 타입 불일치 - ${JSON.stringify(condition).substring(0, 40)}...)`;
    }
  }
  return `조건 ${conditionIndex + 1} (내용이 없거나 올바른 객체 형식이 아님)`;
};

const formattedRuleBlocks = computed(() => {
  const blocks = [];
  const sourceRules = props.rules;

  if (!sourceRules || typeof sourceRules !== 'object' || Object.keys(sourceRules).length === 0) {
    return blocks; // 규칙 데이터가 없으면 빈 배열 반환
  }

  let mainConditionsParsed = false;

  // 1. 최상위 'conditions' 배열 처리 (StrategyListView에서 주로 사용될 구조)
  if (sourceRules.conditions && Array.isArray(sourceRules.conditions)) {
    blocks.push({
      type: '전략 조건', // 또는 '주요 조건' 등
      details: sourceRules.conditions.length > 0 
                 ? sourceRules.conditions.map((cond, idx) => formatSingleCondition(cond, idx)) 
                 : ['정의된 조건 없음']
    });
    mainConditionsParsed = true; 
  }

  // 2. 'buy_conditions', 'sell_conditions' 처리 (MarketplaceDetailView에서 사용될 수 있는 상세 구조)
  // 'conditions'가 이미 파싱되었다면, 중복을 피하기 위해 이 블록은 건너뛸 수 있거나,
  // 혹은 백엔드 응답이 항상 둘 중 하나의 구조만 갖는다고 가정할 수 있습니다.
  // 여기서는 'conditions'가 없을 때만 'buy_conditions' 등을 시도하도록 변경합니다.
  if (!mainConditionsParsed) {
    if (sourceRules.buy_conditions && Array.isArray(sourceRules.buy_conditions)) {
      blocks.push({
        type: '매수 조건',
        details: sourceRules.buy_conditions.length > 0 ? sourceRules.buy_conditions.map((cond, idx) => formatSingleCondition(cond, idx)) : ['정의된 매수 조건 없음']
      });
    }
    if (sourceRules.sell_conditions && Array.isArray(sourceRules.sell_conditions)) {
      blocks.push({
        type: '매도 조건',
        details: sourceRules.sell_conditions.length > 0 ? sourceRules.sell_conditions.map((cond, idx) => formatSingleCondition(cond, idx)) : ['정의된 매도 조건 없음']
      });
    }
  }
  
  // 3. 'actions' 객체 처리 (로그에서 확인된 구조)
  if (sourceRules.actions && typeof sourceRules.actions === 'object') {
    const actionDetails = [];
    if (sourceRules.actions.buy_signal_strength !== undefined) {
      actionDetails.push(`매수 신호 강도: ${sourceRules.actions.buy_signal_strength}`);
    }
    if (sourceRules.actions.sell_signal_strength !== undefined) {
      actionDetails.push(`매도 신호 강도: ${sourceRules.actions.sell_signal_strength}`);
    }
    if (actionDetails.length > 0) {
      blocks.push({ type: '실행 규칙 (Actions)', details: actionDetails });
    }
  }

  // 4. 'portfolio_rules' 객체 처리 (로그에서 확인된 구조)
  if (sourceRules.portfolio_rules && typeof sourceRules.portfolio_rules === 'object') {
    const portfolioDetails = [];
    if (sourceRules.portfolio_rules.max_stocks !== undefined) {
      portfolioDetails.push(`최대 보유 종목 수: ${sourceRules.portfolio_rules.max_stocks}`);
    }
    if (sourceRules.portfolio_rules.rebalance_period_days !== undefined) {
      portfolioDetails.push(`리밸런싱 주기: ${sourceRules.portfolio_rules.rebalance_period_days}일`);
    }
    if (portfolioDetails.length > 0) {
      blocks.push({ type: '포트폴리오 규칙', details: portfolioDetails });
    }
  }

  return blocks;
});

const hasRulesButCouldNotFormat = computed(() => {
  // props.rules에 내용이 있지만, formattedRuleBlocks가 비었다면 (파싱 실패) true
  return Object.keys(props.rules || {}).length > 0 && formattedRuleBlocks.value.length === 0;
});

const truncateJson = (jsonObj, maxLength = 60) => {
  if (!jsonObj || Object.keys(jsonObj).length === 0) return '내용 없음';
  try {
    const jsonString = JSON.stringify(jsonObj);
    return jsonString.length > maxLength ? jsonString.substring(0, maxLength - 3) + '...' : jsonString;
  } catch (e) {
    // stringify 할 수 없는 값 (예: 순환 참조)이 props.rules로 들어올 경우 대비
    return '규칙 표시 오류 (내용 확인 불가)';
  }
};
</script>

<style scoped>
.rule-display {
  font-size: 0.9em;
  text-align: left;
}
.rule-block {
  margin-bottom: 12px;
  padding: 10px;
  background-color: var(--joomak-background-mute, #f8f9fa); /* 테마 변수 사용 */
  border: 1px solid var(--joomak-border-subtle, #e9ecef); /* 테마 변수 사용 */
  border-radius: 4px;
}
.rule-block:last-child {
  margin-bottom: 0;
}
.rule-type {
  font-weight: bold;
  color: var(--joomak-text-strong, #212529); /* 테마 변수 사용 */
  display: block;
  margin-bottom: 6px;
}
.condition-list {
  list-style-type: disc; /* 점으로 표시 */
  padding-left: 20px; /* 들여쓰기 */
  margin-top: 0;
  margin-bottom: 0;
}
.condition-item {
  padding: 3px 0;
  color: var(--joomak-text-body, #495057); /* 테마 변수 사용 */
  line-height: 1.5;
}
.single-detail-text { /* details가 단일 문자열일 때 (거의 사용 안 될 수 있음) */
  color: var(--joomak-text-body, #495057);
  margin:0;
}
.no-details-message small {
  color: var(--joomak-text-muted, #6c757d); /* 테마 변수 사용 */
  font-style: italic;
}
.rule-display-fallback code,
.rule-display-empty small {
  color: var(--joomak-text-muted, #6c757d); /* 테마 변수 사용 */
}
.rule-display-fallback code {
  background-color: var(--joomak-background-mute, #f1f1f1); /* 테마 변수 사용 */
  padding: 2px 4px;
  border-radius: 3px;
  font-family: monospace; /* 코드 폰트 */
}
</style>