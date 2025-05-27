<template>
    <div class="product-detail-container">
      <div v-if="financeStore.loading" class="text-center my-5">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else-if="financeStore.error" class="alert alert-danger" role="alert">
        {{ financeStore.error }}
      </div>
      <div v-else-if="product" class="card">
        <div class="card-header bg-primary text-white">
          <h4 class="mb-0">{{ product.name }}</h4>
          <p class="mb-0"><small>{{ product.bank.name }} (상품코드: {{ product.fin_prdt_cd }})</small></p>
        </div>
        <div class="card-body">
          <p><strong>공시월:</strong> {{ product.dcls_month }}</p>
          <p><strong>상품 유형:</strong> {{ product.product_type === 'deposit' ? '정기예금' : '적금' }}</p>
          <p><strong>가입 방법:</strong> {{ product.join_way || '-' }}</p>
          <p><strong>만기 후 이자율:</strong> {{ product.mtrt_int || '-' }}</p>
          <p><strong>우대 조건:</strong></p>
          <div v-html="product.spcl_cnd || '-'"></div>
          <p class="mt-2"><strong>가입 대상:</strong> {{ product.join_member || '-' }}</p>
          <p><strong>최고 한도:</strong> {{ product.max_limit ? `${product.max_limit.toLocaleString()} 원` : '-' }}</p>
          <p><strong>기타 유의사항:</strong></p>
          <div v-html="product.etc_note || '-'"></div>
  
          <hr class="my-4">
          <h5>금리 옵션 정보</h5>
          <div v-if="product.options && product.options.length > 0" class="table-responsive">
            <table class="table table-striped table-hover table-sm">
              <thead class="table-light">
                <tr>
                  <th>저축 기간 (개월)</th>
                  <th>이자율 유형</th>
                  <th>기본 금리 (%)</th>
                  <th>최고 우대 금리 (%)</th>
                  <th v-if="product.product_type === 'saving'">적립 유형</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="option in product.options" :key="option.id">
                  <td>{{ option.save_trm }}</td>
                  <td>{{ option.intr_rate_type_nm }}</td>
                  <td>{{ option.intr_rate || '-' }}</td>
                  <td>{{ option.intr_rate2 || '-' }}</td>
                  <td v-if="product.product_type === 'saving'">{{ option.rsrv_type_nm || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="text-muted">금리 옵션 정보가 없습니다.</p>
  
          <div class="text-center mt-4" v-if="isLoggedIn">
            <button class="btn btn-success btn-lg" @click="openJoinModal(product)">
              가입하기
            </button>
          </div>
          <div class="text-center mt-4" v-else>
            <p class="text-danger">상품에 가입하려면 로그인이 필요합니다.</p>
            <router-link to="/login" class="btn btn-primary">로그인 페이지로</router-link>
          </div>
  
        </div>
        <div class="card-footer text-muted">
          공시 시작일: {{ product.dcls_strt_day || '-' }} | 
          공시 종료일: {{ product.dcls_end_day || '-' }} |
          금융회사 제출일: {{ product.fin_co_subm_day || '-' }}
        </div>
      </div>
      <div v-else class="alert alert-warning">
        상품 정보를 찾을 수 없습니다.
      </div>
  
      <div class="modal fade" id="joinProductModal" tabindex="-1" aria-labelledby="joinProductModalLabel" aria-hidden="true" ref="joinModalRef">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="joinProductModalLabel">상품 가입: {{ selectedProductForJoin?.name }}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <div v-if="selectedOptionForJoin">
                <p><strong>선택 옵션:</strong> {{ selectedOptionForJoin.save_trm }}개월, 기본 {{ selectedOptionForJoin.intr_rate }}%</p>
                <div class="mb-3">
                  <label for="joinAmount" class="form-label">가입 금액 (원)</label>
                  <input type="number" class="form-control" id="joinAmount" v-model.number="joinAmount" min="1">
                </div>
                <p v-if="joinError" class="text-danger">{{ joinError }}</p>
              </div>
              <div v-else>
                <label for="optionSelect" class="form-label">가입할 옵션 선택:</label>
                <select id="optionSelect" class="form-select" v-model="selectedOptionIdForJoin">
                  <option disabled value="">옵션을 선택하세요</option>
                  <option v-for="opt in product?.options" :key="opt.id" :value="opt.id">
                     {{ opt.save_trm }}개월 | {{ opt.intr_rate_type_nm }} | 기본 {{ opt.intr_rate || '-' }}% <span v-if="opt.intr_rate2">(최고 {{ opt.intr_rate2 }}%)</span>
                  </option>
                </select>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">취소</button>
              <button type="button" class="btn btn-primary" @click="handleJoinProduct" :disabled="!selectedOptionIdForJoin || !joinAmount || joinLoading">
                <span v-if="joinLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                {{ joinLoading ? '처리중...' : '가입 확정' }}
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

  
  const route = useRoute()
  const router = useRouter()
  const financeStore = useFinanceStore()
  const authStore = useAuthStore() // 인증 스토어 인스턴스
  
  const product = computed(() => financeStore.productDetail)
  const isLoggedIn = computed(() => authStore.isAuthenticated) // 로그인 상태
  
  const joinModalRef = ref(null) // 모달 DOM 엘리먼트 참조
  let joinModalInstance = null 
  const selectedProductForJoin = ref(null)
  const selectedOptionIdForJoin = ref('')
  const selectedOptionForJoin = computed(() => {
    if (product.value && selectedOptionIdForJoin.value) {
      return product.value.options.find(opt => opt.id === selectedOptionIdForJoin.value)
    }
    return null
  })
  const joinAmount = ref(10000) // 기본 가입 금액 예시
  const joinLoading = ref(false)
  const joinError = ref('')
  
  
  const openJoinModal = (prod) => {
    selectedProductForJoin.value = prod
    selectedOptionIdForJoin.value = '' // 모달 열 때 옵션 선택 초기화
    joinAmount.value = 10000 // 기본값 설정
    joinError.value = ''
    if (joinModalInstance) {
      joinModalInstance.show()
    }
  }
  
  const handleJoinProduct = async () => {
    if (!selectedOptionIdForJoin.value || !joinAmount.value || joinAmount.value <= 0) {
      joinError.value = "가입할 옵션을 선택하고, 올바른 금액을 입력해주세요."
      return
    }
    joinLoading.value = true
    joinError.value = ''
    try {
      // 실제 가입 API 호출
      // const response = await api.post('/api/products/join/', {
      //   option_id: selectedOptionIdForJoin.value,
      //   amount: joinAmount.value,
      // });
      // console.log('가입 성공:', response.data);
      // alert(`<span class="math-inline">\{selectedProductForJoin\.value\.name\} \(</span>{selectedOptionForJoin.value.save_trm}개월) 상품에 ${joinAmount.value.toLocaleString()}원 가입 신청 완료! (실제 API 연동 필요)`);
  
      // 임시 성공 처리 (실제 API 연동 필요)
      alert(`[임시] <span class="math-inline">\{selectedProductForJoin\.value\.name\} \(</span>{selectedOptionForJoin.value.save_trm}개월) 상품에 ${joinAmount.value.toLocaleString()}원 가입 신청!`);
      if (joinModalInstance) joinModalInstance.hide()
      // TODO: 가입 성공 후 추가 작업 (예: 사용자 프로필 업데이트, 알림 등)
  
    } catch (error) {
      console.error("상품 가입 오류:", error.response?.data || error.message)
      joinError.value = error.response?.data?.error || error.response?.data?.message || '상품 가입 중 오류가 발생했습니다.'
    } finally {
      joinLoading.value = false
    }
  }
  
  onMounted(() => {
    const finPrdtCd = route.params.fin_prdt_cd
    if (finPrdtCd) {
      financeStore.fetchProductDetail(finPrdtCd)
    }
    // Bootstrap Modal 인스턴스 초기화
    if (joinModalRef.value) {
        joinModalInstance = new window.bootstrap.Modal(joinModalRef.value)
    }
  })
  
  // 경로 파라미터 변경 감지하여 데이터 다시 로드
  watch(() => route.params.fin_prdt_cd, (newFinPrdtCd) => {
    if (newFinPrdtCd) {
      financeStore.fetchProductDetail(newFinPrdtCd)
    }
  })
  </script>
  
  <style scoped>
  .product-detail-container {
    max-width: 900px;
    margin: auto;
    padding: 20px;
  }
  .card-header h4 {
    font-size: 1.5rem;
  }
  .table-sm th, .table-sm td {
    padding: 0.4rem;
    font-size: 0.9rem;
  }
  /* HTML 문자열 내부의 p 태그 마진 제거 */
  :deep(div[v-html] p) {
    margin-bottom: 0.5rem;
  }
  :deep(div[v-html] ul) {
    padding-left: 1.2rem;
    margin-bottom: 0.5rem;
  }
  </style>