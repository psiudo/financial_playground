// frontpjt/src/stores/financeStore.js
import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '@/utils/api' // 백엔드 API 호출용 (baseURL: 'http://127.0.0.1:8000/api')

export const useFinanceStore = defineStore('finance', () => {
  const products = ref([])
  const banks = ref([]) // 상품 목록에서 동적으로 은행 목록을 추출하여 저장할 수 있습니다.
  const productTypes = ref([ // 예시, 실제로는 고정값 또는 API로부터 받을 수 있습니다.
    { code: 'deposit', name: '정기예금' },
    { code: 'saving', name: '적금' },
  ])

  const loading = ref(false) // 목록 로딩 상태
  const error = ref(null)    // 목록 에러 상태

  async function fetchProducts(filters = {}) {
    loading.value = true
    error.value = null
    products.value = [] // 새 검색 시 초기화
    try {
      // ★★★ API 경로 수정: 'v1/' 추가 ★★★
      // baseURL('http://127.0.0.1:8000/api') + 'v1/products/list/'
      const response = await api.get('v1/products/list/', { params: filters })
      // 페이지네이션 응답을 사용하는 경우 response.data.results를 사용해야 할 수 있습니다.
      // 여기서는 백엔드가 직접 배열을 반환하거나, 페이지네이션 결과가 .results에 있다고 가정합니다.
      products.value = response.data.results ? response.data.results : response.data;

      // 은행 목록 추출 로직 (필터가 없을 때만 전체 은행 목록 업데이트)
      if (Object.keys(filters).length === 0 || (!filters.bank_code && !filters.bank_name)) {
        const uniqueBanks = new Map()
        // products.value가 항상 배열임을 보장
        if (Array.isArray(products.value)) {
            products.value.forEach(p => {
              if (p.bank && p.bank.code && !uniqueBanks.has(p.bank.code)) { // p.bank.code 존재 여부도 확인
                uniqueBanks.set(p.bank.code, { code: p.bank.code, name: p.bank.name })
              }
            })
            banks.value = Array.from(uniqueBanks.values()).sort((a, b) => a.name.localeCompare(b.name));
        } else {
            console.warn('Products data is not an array:', products.value);
            banks.value = []; // 데이터가 배열이 아니면 은행 목록도 비움
        }
      }
    } catch (err) {
      error.value = `상품 목록 조회에 실패했습니다: ${err.response?.data?.detail || err.message}`;
      console.error("Error fetching products:", err.response?.data || err.message, err);
      products.value = []; // 오류 발생 시 상품 목록 비움
      banks.value = [];    // 오류 발생 시 은행 목록도 비움
    } finally {
      loading.value = false
    }
  }

  const productDetail = ref(null)
  const isLoadingDetail = ref(false); // 상세 정보 로딩 상태 추가
  const detailError = ref(null);    // 상세 정보 에러 상태 추가

  async function fetchProductDetail(finPrdtCd) {
    isLoadingDetail.value = true; // 상세 로딩 시작
    detailError.value = null;
    productDetail.value = null; // 이전 상세 정보 초기화
    try {
      // ★★★ API 경로 수정: 'v1/' 추가 ★★★
      // baseURL('http://127.0.0.1:8000/api') + `v1/products/${finPrdtCd}/`
      const response = await api.get(`v1/products/${finPrdtCd}/`); // 수정된 경로
      productDetail.value = response.data;
      console.log('financeStore: Product detail fetched for', finPrdtCd, productDetail.value);
    } catch (err) {
      detailError.value = `상품 상세 정보(${finPrdtCd})를 불러오는 데 실패했습니다: ${err.response?.data?.detail || err.message}`;
      console.error(`Error fetching product detail for ${finPrdtCd}:`, err.response?.data || err.message, err);
      productDetail.value = null; // 오류 시 초기화
    } finally {
      isLoadingDetail.value = false; // 상세 로딩 종료
    }
  }

  return {
    products,
    banks,
    productTypes,
    loading, // 목록 로딩
    error,   // 목록 에러
    fetchProducts,
    productDetail,
    isLoadingDetail, // 상세 로딩
    detailError,     // 상세 에러
    fetchProductDetail,
  }
})