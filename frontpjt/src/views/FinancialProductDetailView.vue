<template>
    <div class="product-detail-container container mt-4">
      <div v-if="financeStore.loading && !product" class="text-center my-5">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else-if="financeStore.error && !product" class="alert alert-danger" role="alert">
        {{ financeStore.error }}
      </div>
      <div v-else-if="product" class="card shadow-sm">
        <div class="card-header bg-light">
          <h3 class="mb-0">{{ product.name }}</h3>
          <p class="mb-0 text-muted"><small>{{ product.bank.name }} (상품코드: {{ product.fin_prdt_cd }})</small></p>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <p><strong>공시월:</strong> {{ product.dcls_month }}</p>
              <p><strong>상품 유형:</strong> {{ product.product_type === 'deposit' ? '정기예금' : '적금' }}</p>
              <p><strong>가입 방법:</strong></p>
              <div v-html="formatMultiLine(product.join_way) || '-'"></div>
            </div>
            <div class="col-md-6">
              <p><strong>만기 후 이자율:</strong></p>
              <div v-html="formatMultiLine(product.mtrt_int) || '-'"></div>
              <p class="mt-2"><strong>가입 대상:</strong></p>
              <div v-html="formatMultiLine(product.join_member) || '-'"></div>
            </div>
          </div>
  
          <hr class="my-3">
          <p><strong>우대 조건:</strong></p>
          <div v-html="formatMultiLine(product.spcl_cnd) || '-'"></div>
  
          <p class="mt-3"><strong>최고 한도:</strong> {{ product.max_limit ? `${product.max_limit.toLocaleString()} 원` : '제한 없음 또는 정보 없음' }}</p>
  
          <p class="mt-3"><strong>기타 유의사항:</strong></p>
          <div v-html="formatMultiLine(product.etc_note) || '-'"></div>
  
          <hr class="my-4">
          <h4>금리 옵션 정보</h4>
          <div v-if="product.options && product.options.length > 0" class="table-responsive">
            <table class="table table-striped table-hover table-sm caption-top">
              <caption><small>아래 표에서 원하시는 옵션을 선택하여 가입할 수 있습니다.</small></caption>
              <thead class="table-light">
                <tr>
                  <th>저축 기간 (개월)</th>
                  <th>이자율 유형</th>
                  <th>기본 금리 (%)</th>
                  <th>최고 우대 금리 (%)</th>
                  <th v-if="product.product_type === 'saving'">적립 유형</th>
                  <th>가입 신청</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="option in product.options" :key="option.id">
                  <td>{{ option.save_trm }}</td>
                  <td>{{ option.intr_rate_type_nm }}</td>
                  <td>{{ option.intr_rate || '-' }}</td>
                  <td>{{ option.intr_rate2 || '-' }}</td>
                  <td v-if="product.product_type === 'saving'">{{ option.rsrv_type_nm || '-' }}</td>
                  <td>
                    <button 
                      class="btn btn-success btn-sm" 
                      @click="openJoinModal(option)" 
                      :disabled="!authStore.isAuthenticated"
                      title="로그인 후 가입 가능">
                      선택
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="text-muted">금리 옵션 정보가 없습니다.</p>
  
          <div class="text-center mt-3" v-if="!authStore.isAuthenticated">
            <p class="text-danger small">상품에 가입하려면 로그인이 필요합니다.</p>
            <router-link :to="{name: 'LoginView'}" class="btn btn-outline-primary btn-sm">로그인 페이지로</router-link>
          </div>
  
        </div>
        <div class="card-footer text-muted small">
          공시 시작일: {{ product.dcls_strt_day || '-' }} | 
          공시 종료일: {{ product.dcls_end_day || '-' }} |
          금융회사 제출일: {{ product.fin_co_subm_day || '-' }}
        </div>
      </div>
      <div v-else class="alert alert-warning mt-3">
        선택하신 상품 정보를 찾을 수 없습니다.
      </div>
  
      <div class="modal fade" id="joinProductModal" tabindex="-1" aria-labelledby="joinProductModalLabel" aria-hidden="true" ref="joinModalRef">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="joinProductModalLabel">상품 가입 신청</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <div v-if="selectedOptionForJoin">
                <p><strong>상품명:</strong> {{ product?.name }}</p>
                <p><strong>선택 옵션:</strong> {{ selectedOptionForJoin.save_trm }}개월, {{selectedOptionForJoin.intr_rate_type_nm}}, 기본 {{ selectedOptionForJoin.intr_rate }}% <span v-if="selectedOptionForJoin.intr_rate2">(최고 {{ selectedOptionForJoin.intr_rate2 }}%)</span></p>
                <div class="mb-3">
                  <label for="joinAmount" class="form-label">가입 금액 (원)</label>
                  <input type="number" class="form-control" id="joinAmount" v-model.number="joinAmount" min="1" placeholder="가입할 금액을 입력하세요">
                </div>
                <p v-if="joinError" class="text-danger small mt-2">{{ joinError }}</p>
                <p v-if="joinSuccessMessage" class="text-success small mt-2">{{ joinSuccessMessage }}</p>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">취소</button>
              <button type="button" class="btn btn-primary" @click="handleJoinProduct" :disabled="!selectedOptionForJoin || !joinAmount || joinLoading">
                <span v-if="joinLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                {{ joinLoading ? '가입 처리중...' : '가입 확정' }}
              </button>
            </div>
          </div>
        </div>
      </div>
  
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { useFinanceStore } from '@/stores/financeStore'
  import { useAuthStore } from '@/stores/authStore'
  import { Modal } from 'bootstrap' // Bootstrap Modal 사용
  import api from '@/utils/api' // API 호출용
  
  const route = useRoute()
  const router = useRouter()
  const financeStore = useFinanceStore()
  const authStore = useAuthStore()
  
  const product = computed(() => financeStore.productDetail)
  
  const joinModalRef = ref(null)
  let joinModalInstance = null 
  const selectedOptionForJoin = ref(null) // 가입 모달에 표시될 옵션 정보
  const joinAmount = ref(null) // 기본 가입 금액 null로 초기화
  const joinLoading = ref(false)
  const joinError = ref('')
  const joinSuccessMessage = ref('')
  
  // 여러 줄 텍스트를 HTML로 변환 (줄바꿈 등)
  const formatMultiLine = (text) => {
    if (!text) return null;
    return text.replace(/\n/g, '<br>');
  };
  
  const openJoinModal = (option) => {
    if (!authStore.isAuthenticated) {
      alert('로그인이 필요한 서비스입니다.');
      router.push({ name: 'LoginView' });
      return;
    }
    selectedOptionForJoin.value = option
    joinAmount.value = null // 모달 열 때 가입 금액 초기화
    joinError.value = ''
    joinSuccessMessage.value = ''
    if (joinModalInstance) {
      joinModalInstance.show()
    }
  }
  
  const handleJoinProduct = async () => {
    if (!selectedOptionForJoin.value || !joinAmount.value || joinAmount.value <= 0) {
      joinError.value = "가입할 옵션을 선택하고, 올바른 금액(1원 이상)을 입력해주세요."
      return
    }
    joinLoading.value = true
    joinError.value = ''
    joinSuccessMessage.value = ''
    try {
      const response = await api.post('products/join/', { // utils/api.js의 baseURL에 /api가 포함되어 있으므로 products/join/
        option_id: selectedOptionForJoin.value.id,
        amount: joinAmount.value,
      });
  
      joinSuccessMessage.value = `<span class="math-inline">\{product\.value\.name\} \(</span>{selectedOptionForJoin.value.save_trm}개월) 상품에 ${joinAmount.value.toLocaleString()}원 가입 신청이 완료되었습니다. (잔여 포인트: ${response.data.remaining_point_balance?.toLocaleString() || '정보 없음'})`;
      // 성공 후 2초 뒤 모달 닫기 (선택적)
      setTimeout(() => {
        if (joinModalInstance) joinModalInstance.hide()
      }, 2000);
  
      // TODO: SSAFY 요구사항 - 사용자의 "가입한 상품 목록" 필드 업데이트 관련 처리
      // 현재 JoinedProduct 모델에 저장되므로, 별도 User 모델 필드 업데이트는 필요 없을 수 있음.
      // 프로필 페이지에서 JoinedProduct 목록을 보여주면 됨.
  
    } catch (error) {
      console.error("상품 가입 오류:", error.response?.data || error.message);
      joinError.value = error.response?.data?.detail || error.response?.data?.error || error.response?.data?.message || '상품 가입 중 오류가 발생했습니다.';
      if (error.response?.status === 401) {
          joinError.value = '로그인이 필요하거나 세션이 만료되었습니다. 다시 로그인해주세요.';
      }
    } finally {
      joinLoading.value = false
    }
  }
  
  onMounted(() => {
    const finPrdtCd = route.params.fin_prdt_cd
    if (finPrdtCd) {
      financeStore.fetchProductDetail(finPrdtCd)
    }
    if (joinModalRef.value) {
      joinModalInstance = new Modal(joinModalRef.value)
    }
  })
  
  watch(() => route.params.fin_prdt_cd, (newFinPrdtCd, oldFinPrdtCd) => {
    if (newFinPrdtCd && newFinPrdtCd !== oldFinPrdtCd) {
      financeStore.fetchProductDetail(newFinPrdtCd)
    }
  })
  </script>
  
  <style scoped>
  .product-detail-container {
    max-width: 900px;
    margin: auto;
    padding-bottom: 50px; /* 푸터 공간 확보 */
  }
  .card-header h3 {
    font-size: 1.6rem;
  }
  .table-sm th, .table-sm td {
    padding: 0.5rem;
    vertical-align: middle;
  }
  /* v-html로 삽입된 P 태그 등의 기본 마진을 조절 */
  :deep(div[v-html] > *:first-child) {
    margin-top: 0;
  }
  :deep(div[v-html] > *:last-child) {
    margin-bottom: 0;
  }
  </style>