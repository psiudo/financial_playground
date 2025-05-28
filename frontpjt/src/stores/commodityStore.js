// frontpjt/src/stores/commodityStore.js
import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '@/utils/api'

export const useCommodityStore = defineStore('commodity', () => {
  // --- 상태 (State) ---
  const commodityList = ref([]) // { symbol: 'GOLD', name: 'Gold', latest_price: '2071.80' }
  
  const priceHistoryGold = ref([])
  const priceHistorySilver = ref([])
  
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
      const response = await api.get('commodities/list/') // 백엔드 API 경로 확인!
      commodityList.value = response.data
      console.log('Commodity list fetched:', commodityList.value)
    } catch (err) {
      console.error('Error fetching commodity list:', err)
      errorList.value = '현물 상품 목록을 불러오는 중 오류가 발생했습니다.'
      commodityList.value = []
    } finally {
      isLoadingList.value = false
    }
  }

  // symbol별로 가격 이력을 가져오고 상태를 업데이트하는 함수
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
      console.error(`Unsupported commodity symbol: ${symbol}`);
      return;
    }

    isLoadingRef.value = true;
    errorRef.value = null;
    
    let url = `commodities/${upperSymbol}/history/`;
    const params = {};
    if (startDate) params.from = startDate;
    if (endDate) params.to = endDate;

    try {
      const response = await api.get(url, { params });
      priceHistoryRef.value = response.data;
      console.log(`Price history for ${upperSymbol} fetched:`, priceHistoryRef.value);
    } catch (err) {
      console.error(`Error fetching price history for ${upperSymbol}:`, err);
      errorRef.value = `${upperSymbol} 가격 정보를 불러오는 중 오류가 발생했습니다.`;
      priceHistoryRef.value = [];
    } finally {
      isLoadingRef.value = false;
    }
  }
  
  // 선택적으로, 모든 상품의 가격 이력을 한 번에 초기화하는 함수
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
    fetchPriceHistoryForSymbol, // 이름 변경 및 로직 수정
    clearAllPriceHistories,
  }
})