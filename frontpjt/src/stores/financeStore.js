// frontpjt/src/stores/financeStore.js
import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '@/utils/api' // 백엔드 API 호출용

export const useFinanceStore = defineStore('finance', () => {
  const products = ref([])
  const banks = ref([])
  const productTypes = ref([
    { code: 'deposit', name: '정기예금' },
    { code: 'saving', name: '적금' },
  ])

  const loading = ref(false)
  const error = ref(null)

  async function fetchProducts(filters = {}) {
    loading.value = true
    error.value = null
    products.value = []
    try {
      // ★★★ 수정된 부분 ★★★
      const response = await api.get('products/list/', { params: filters })
      products.value = response.data

      if (Object.keys(filters).length === 0 || (!filters.bank_code && !filters.bank_name)) {
        const uniqueBanks = new Map()
        response.data.forEach(p => {
          if (p.bank && !uniqueBanks.has(p.bank.code)) {
            uniqueBanks.set(p.bank.code, { code: p.bank.code, name: p.bank.name })
          }
        })
        banks.value = Array.from(uniqueBanks.values()).sort((a, b) => a.name.localeCompare(b.name));
      }
    } catch (err) {
      error.value = '상품 목록 조회에 실패했습니다.'
      console.error("Error fetching products:", err)
    } finally {
      loading.value = false
    }
  }

  const productDetail = ref(null)
  async function fetchProductDetail(finPrdtCd) {
    loading.value = true
    error.value = null
    productDetail.value = null
    try {
      // ★★★ 수정된 부분 ★★★
      const response = await api.get(`products/${finPrdtCd}/`)
      productDetail.value = response.data
    } catch (err) {
      error.value = '상품 상세 정보를 불러오는 데 실패했습니다.'
      console.error("Error fetching product detail:", err)
    } finally {
      loading.value = false
    }
  }

  return {
    products,
    banks,
    productTypes,
    loading,
    error,
    fetchProducts,
    productDetail,
    fetchProductDetail,
  }
})