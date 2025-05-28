// frontpjt/src/stores/financeStore.js
import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '@/utils/api' // 백엔드 API 호출용 (baseURL: 'http://127.0.0.1:8000/api')
import { useAuthStore } from './authStore'; // authStore 사용 (사용자 인증 정보 필요시)

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
      const response = await api.get('v1/products/list/', { params: filters }) // 'v1/' 추가됨
      products.value = response.data.results ? response.data.results : response.data;

      if (Object.keys(filters).length === 0 || (!filters.bank_code && !filters.bank_name)) {
        const uniqueBanks = new Map()
        if (Array.isArray(products.value)) {
            products.value.forEach(p => {
              if (p.bank && p.bank.code && !uniqueBanks.has(p.bank.code)) { 
                uniqueBanks.set(p.bank.code, { code: p.bank.code, name: p.bank.name })
              }
            })
            banks.value = Array.from(uniqueBanks.values()).sort((a, b) => a.name.localeCompare(b.name));
        } else {
            console.warn('Products data is not an array:', products.value);
            banks.value = []; 
        }
      }
    } catch (err) {
      error.value = `상품 목록 조회에 실패했습니다: ${err.response?.data?.detail || err.message}`;
      console.error("Error fetching products:", err.response?.data || err.message, err);
      products.value = []; 
      banks.value = [];    
    } finally {
      loading.value = false
    }
  }

  const productDetail = ref(null)
  const isLoadingDetail = ref(false); 
  const detailError = ref(null);    

  async function fetchProductDetail(finPrdtCd) {
    isLoadingDetail.value = true; 
    detailError.value = null;
    productDetail.value = null; 
    try {
      const response = await api.get(`v1/products/${finPrdtCd}/`); // 'v1/' 추가됨
      productDetail.value = response.data;
      console.log('financeStore: Product detail fetched for', finPrdtCd, productDetail.value);
    } catch (err) {
      detailError.value = `상품 상세 정보(${finPrdtCd})를 불러오는 데 실패했습니다: ${err.response?.data?.detail || err.message}`;
      console.error(`Error fetching product detail for ${finPrdtCd}:`, err.response?.data || err.message, err);
      productDetail.value = null; 
    } finally {
      isLoadingDetail.value = false; 
    }
  }

  // --- 상품 가입 관련 상태 및 액션 추가 ---
  const isJoining = ref(false);
  const joinError = ref(null);
  const joinSuccessMessage = ref('');

  async function joinProduct(payload) { // payload 예시: { product_code: '...', fin_prdt_cd: '...', options_id: 123, join_amount: 50000 }
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) {
      joinError.value = '상품에 가입하려면 로그인이 필요합니다.';
      return false;
    }

    isJoining.value = true;
    joinError.value = null;
    joinSuccessMessage.value = '';
    try {
      // ★★★ API 호출 경로 수정: 'v1/' 추가 ★★★
      // baseURL('http://127.0.0.1:8000/api') + 'v1/products/join/'
      const response = await api.post('v1/products/join/', payload); // 수정된 경로
      joinSuccessMessage.value = response.data.message || '상품에 성공적으로 가입되었습니다.';
      console.log('financeStore: Product joined successfully', response.data);
      // 필요하다면 사용자의 가입 상품 목록 등을 새로고침하는 로직 추가
      return true;
    } catch (err) {
      joinError.value = `상품 가입에 실패했습니다: ${err.response?.data?.detail || err.response?.data?.message || err.message}`;
      console.error('Error joining product:', err.response?.data || err.message, err);
      return false;
    } finally {
      isJoining.value = false;
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
    isLoadingDetail, 
    detailError,     
    fetchProductDetail,

    // 상품 가입 관련 반환
    isJoining,
    joinError,
    joinSuccessMessage,
    joinProduct,
  }
})