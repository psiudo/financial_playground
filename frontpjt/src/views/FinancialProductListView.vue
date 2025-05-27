<template>
    <div class="container mt-4">
      <h2>예금 & 적금 비교</h2>
      <hr>
  
      <div class="row g-3 mb-4 align-items-end">
        <div class="col-md-4">
          <label for="bank-filter" class="form-label">은행 선택</label>
          <select id="bank-filter" class="form-select" v-model="selectedBank" @change="applyFilters">
            <option value="">전체 은행</option>
            <option v-for="bank in financeStore.banks" :key="bank.code" :value="bank.code">
              {{ bank.name }}
            </option>
          </select>
        </div>
        <div class="col-md-4">
          <label for="product-type-filter" class="form-label">상품 유형</label>
          <select id="product-type-filter" class="form-select" v-model="selectedProductType" @change="applyFilters">
            <option value="">전체 유형</option>
            <option v-for="pType in financeStore.productTypes" :key="pType.code" :value="pType.code">
              {{ pType.name }}
            </option>
          </select>
        </div>
        <div class="col-md-4">
          <button class="btn btn-outline-secondary w-100" @click="resetFilters">필터 초기화</button>
        </div>
      </div>
  
      <div v-if="financeStore.loading" class="text-center my-5">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else-if="financeStore.error" class="alert alert-danger" role="alert">
        {{ financeStore.error }}
      </div>
      <div v-else-if="financeStore.products.length === 0" class="alert alert-info" role="alert">
        선택하신 조건에 맞는 금융상품이 없습니다.
      </div>
  
      <div v-else class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
        <div class="col" v-for="product in financeStore.products" :key="product.fin_prdt_cd">
          <div class="card h-100 shadow-sm">
            <div class="card-header bg-light">
              <h5 class="card-title mb-0">{{ product.name }}</h5>
              <small class="text-muted">{{ product.bank.name }}</small>
            </div>
            <div class="card-body">
              <p class="mb-1"><strong>유형:</strong> {{ product.product_type === 'deposit' ? '정기예금' : '적금' }}</p>
              <p class="mb-1"><strong>가입방법:</strong> {{ product.join_way || '정보 없음' }}</p>
  
              <div v-if="product.options && product.options.length > 0">
                <p class="mb-1 mt-2"><strong>주요 금리 옵션:</strong></p>
                <ul class="list-group list-group-flush small">
                  <li class="list-group-item px-0" v-for="opt in product.options.slice(0,3)" :key="opt.id">
                    {{ opt.save_trm }}개월 | 기본 {{ opt.intr_rate || '-' }}% 
                    <span v-if="opt.intr_rate2">(최고 {{ opt.intr_rate2 }}%)</span>
                    [{{ opt.intr_rate_type_nm }}]
                  </li>
                </ul>
              </div>
              <div v-else>
                <p class="text-muted small">금리 정보 없음</p>
              </div>
            </div>
            <div class="card-footer text-center">
              <router-link :to="{ name: 'FinancialProductDetailView', params: { fin_prdt_cd: product.fin_prdt_cd }}" class="btn btn-primary btn-sm">
                자세히 보기
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useFinanceStore } from '@/stores/financeStore'
  
  const financeStore = useFinanceStore()
  const selectedBank = ref('')
  const selectedProductType = ref('')
  
  const applyFilters = () => {
    const filters = {}
    if (selectedBank.value) filters.bank_code = selectedBank.value
    if (selectedProductType.value) filters.product_type = selectedProductType.value
    financeStore.fetchProducts(filters)
  }
  
  const resetFilters = () => {
    selectedBank.value = ''
    selectedProductType.value = ''
    financeStore.fetchProducts()
  }
  
  onMounted(() => {
    financeStore.fetchProducts() // 컴포넌트 마운트 시 전체 상품 목록 로드
  })
  </script>
  
  <style scoped>
  .card-title {
    font-size: 1.1rem;
    font-weight: 600;
  }
  .card-header {
    min-height: 60px; /* 은행명과 상품명이 길어도 높이 유지 */
  }
  .card-body p {
    margin-bottom: 0.25rem;
  }
  </style>