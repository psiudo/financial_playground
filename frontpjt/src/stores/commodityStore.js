// frontpjt/src/stores/commodityStore.js
import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '@/utils/api' // baseURL: 'http://127.0.0.1:8000/api'

export const useCommodityStore = defineStore('commodity', () => {
  // --- 상태 (State) ---
  const commodityList = ref([]) // { symbol: 'GOLD', name: 'Gold', latest_price: '2071.80' }
  
  const priceHistoryGold = ref([])
  const priceHistorySilver = ref([])
  // 다른 상품이 추가될 경우를 대비하여 좀 더 일반적인 구조를 고려할 수 있습니다.
  // 예: const priceHistories = ref({}); // { GOLD: [], SILVER: [] }

  const isLoadingList = ref(false)
  const isLoadingHistoryGold = ref(false)
  const isLoadingHistorySilver = ref(false)
  
  const errorList = ref(null)
  const errorHistoryGold = ref(null)
  const errorHistorySilver = ref(null)

  // --- 액션 (Actions) ---
  async function fetchCommodityList() {
    isLoadingList.value = true
    errorList.value = null
    try {
      // ★★★ API 경로 수정: 'v1/' 추가 ★★★
      const response = await api.get('v1/commodities/list/') // 수정된 경로
      commodityList.value = response.data.results ? response.data.results : response.data; // 페이지네이션 고려
      console.log('Commodity list fetched:', commodityList.value)
    } catch (err) {
      console.error('Error fetching commodity list:', err.response?.data || err.message, err)
      errorList.value = `현물 상품 목록을 불러오는 중 오류가 발생했습니다: ${err.response?.data?.detail || err.message}`
      commodityList.value = []
    } finally {
      isLoadingList.value = false
    }
  }

  async function fetchPriceHistoryForSymbol(symbol, startDate = null, endDate = null) {
    if (!symbol) return;

    const upperSymbol = symbol.toUpperCase();
    let isLoadingRef, priceHistoryRef, errorRef;

    if (upperSymbol === 'GOLD') {
      isLoadingRef = isLoadingHistoryGold;
      priceHistoryRef = priceHistoryGold;
      errorRef = errorHistoryGold;
    } else if (upperSymbol === 'SILVER') {
      isLoadingRef = isLoadingHistorySilver;
      priceHistoryRef = priceHistorySilver;
      errorRef = errorHistorySilver;
    } else {
      console.error(`Unsupported commodity symbol for dedicated state: ${symbol}`);
      // 필요하다면 일반적인 priceHistories[symbol] 같은 곳에 저장할 수 있습니다.
      return;
    }

    isLoadingRef.value = true;
    errorRef.value = null;
    
    // ★★★ API 경로 수정: 'v1/' 추가 ★★★
    let url = `v1/commodities/${upperSymbol}/history/`; // 수정된 경로
    const params = {};
    if (startDate) params.from = startDate;
    if (endDate) params.to = endDate;

    try {
      const response = await api.get(url, { params });
      // 페이지네이션 응답을 사용하는 경우 response.data.results를 사용해야 할 수 있습니다.
      priceHistoryRef.value = response.data.results ? response.data.results : response.data;
      console.log(`Price history for ${upperSymbol} fetched:`, priceHistoryRef.value);
    } catch (err) {
      console.error(`Error fetching price history for ${upperSymbol}:`, err.response?.data || err.message, err);
      errorRef.value = `${upperSymbol} 가격 정보를 불러오는 중 오류가 발생했습니다: ${err.response?.data?.detail || err.message}`;
      priceHistoryRef.value = [];
    } finally {
      isLoadingRef.value = false;
    }
  }
  
  function clearAllPriceHistories() {
    priceHistoryGold.value = []
    priceHistorySilver.value = []
    errorHistoryGold.value = null
    errorHistorySilver.value = null
  }

  return {
    commodityList,
    priceHistoryGold,
    priceHistorySilver,
    isLoadingList,
    isLoadingHistoryGold,
    isLoadingHistorySilver,
    errorList,
    errorHistoryGold,
    errorHistorySilver,
    fetchCommodityList,
    fetchPriceHistoryForSymbol,
    clearAllPriceHistories,
  }
})