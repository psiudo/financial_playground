// frontpjt/src/stores/stockInsightStore.js
import { defineStore } from 'pinia';
// ★★★ 직접 axios 대신 중앙 api 인스턴스 사용 ★★★
import api from '@/utils/api'; 
import { useAuthStore } from './authStore';

// API_BASE_URL 상수는 더 이상 직접 사용하지 않습니다. api 인스턴스의 baseURL을 따릅니다.
// const API_BASE_URL_INSIGHT = 'http://127.0.0.1:8000/api/v1/insight'; // 경로에 v1 포함

export const useStockInsightStore = defineStore('stockInsight', {
  state: () => ({
    myInterestStocks: [],
    currentSearchedStock: null,
    isLoadingList: false,
    listError: null,
    isLoadingAnalysis: false,
    analysisError: null,
    actionMessage: null,
  }),
  getters: {
    formattedCurrentSentiment: (state) => {
      if (!state.currentSearchedStock || !state.currentSearchedStock.sentiment_stats) {
        return null;
      }
      const stats = state.currentSearchedStock.sentiment_stats;
      const total_analyzed = (stats.positive || 0) + (stats.negative || 0) + (stats.neutral || 0);
      return {
        positive: stats.positive || 0,
        negative: stats.negative || 0,
        neutral: stats.neutral || 0,
        error: stats.error || 0,
        total_analyzed: total_analyzed,
        total_fetched: stats.total_comments_fetched || 0,
        positive_percent: total_analyzed > 0 ? (((stats.positive || 0) / total_analyzed) * 100).toFixed(1) : '0.0',
        negative_percent: total_analyzed > 0 ? (((stats.negative || 0) / total_analyzed) * 100).toFixed(1) : '0.0',
        neutral_percent: total_analyzed > 0 ? (((stats.neutral || 0) / total_analyzed) * 100).toFixed(1) : '0.0',
        overall_sentiment_display: state.currentSearchedStock.overall_sentiment_display || "정보 없음",
        updated_at: state.currentSearchedStock.updated_at,
        batch_ready: state.currentSearchedStock.batch_ready,
        task_status: state.currentSearchedStock.task_status,
        stock_name: state.currentSearchedStock.stock?.company_name,
        stock_code: state.currentSearchedStock.stock?.stock_code,
        summary: state.currentSearchedStock.summary,
      };
    },
  },
  actions: {
    // ★★★ App.vue에서 호출하는 함수 추가 (clearCurrentAnalysis 내용을 기반으로) ★★★
    clearSelectedStockAnalysis() {
      this.currentSearchedStock = null;
      this.isLoadingAnalysis = false;
      this.analysisError = null;
      this.actionMessage = null;
      console.log('stockInsightStore: clearSelectedStockAnalysis CALLED');
    },

    async analyzeStockOnTheFly(query, type = 'name') {
      if (!query) return;
      this.isLoadingAnalysis = true;
      this.analysisError = null;
      this.currentSearchedStock = null;
      this.actionMessage = null;
      
      const params = type === 'code' ? { code: query } : { name: query };

      try {
        // ★★★ 수정: 전역 api 인스턴스 사용 및 경로 수정 (baseURL: '/api' 기준) ★★★
        const response = await api.get('v1/insight/realtime-analysis/', { params });
        this.currentSearchedStock = response.data;
        if (response.data.stock) {
            this.currentSearchedStock.stock_code_display = response.data.stock.stock_code;
            this.currentSearchedStock.company_name_display = response.data.stock.company_name;
        } else {
            this.currentSearchedStock.stock_code_display = type === 'code' ? query : 'N/A';
            this.currentSearchedStock.company_name_display = type === 'name' ? query : ( type === 'code' ? query : 'N/A');
        }
      } catch (err) {
        console.error(`Error analyzing stock ${query}:`, err);
        this.analysisError = err.response?.data?.error || err.response?.data?.detail || `'${query}' 종목 분석 중 오류가 발생했습니다.`;
        this.currentSearchedStock = { 
            stock: { company_name: type === 'name' ? query : query, stock_code: type === 'code' ? query : 'N/A' },
            summary: this.analysisError,
            sentiment_stats: {},
            batch_ready: false,
            task_status: err.response?.data?.task_status || 'ERROR',
        };
      } finally {
        this.isLoadingAnalysis = false;
      }
    },

    async fetchMyInterestStocks() {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        this.myInterestStocks = [];
        return;
      }
      this.isLoadingList = true;
      this.listError = null;
      try {
        // ★★★ 수정: 전역 api 인스턴스 사용 및 경로 수정 ★★★
        // 헤더는 api 인스턴스 인터셉터에서 자동으로 처리됩니다.
        const response = await api.get('v1/insight/my-interest-stocks/');
        this.myInterestStocks = response.data.results ? response.data.results : response.data;
      } catch (err) {
        console.error('Error fetching my interest stocks:', err);
        this.listError = `관심 종목 목록을 가져오는데 실패했습니다: ${err.response?.data?.detail || err.message}`;
        this.myInterestStocks = [];
      } finally {
        this.isLoadingList = false;
      }
    },

    async fetchSavedAnalysis(interestStockId) {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated || !interestStockId) return;

      this.isLoadingAnalysis = true;
      this.analysisError = null;
      this.currentSearchedStock = null;
      this.actionMessage = null;

      const stockInfoFromList = this.myInterestStocks.find(s => s.id === interestStockId);
      
      try {
        // ★★★ 수정: 전역 api 인스턴스 사용 및 경로 수정 ★★★
        const response = await api.get(`v1/insight/my-interest-stock/${interestStockId}/sentiment/`);

        if (response.status === 204 || response.status === 202) { 
            this.actionMessage = response.data?.message || `${stockInfoFromList?.stock?.company_name || '선택 종목'}의 분석 결과가 없거나 진행 중입니다.`;
            this.currentSearchedStock = {
                stock: stockInfoFromList?.stock || { company_name: '알 수 없음', stock_code: 'N/A' },
                batch_ready: false,
                task_status: response.data?.task_status || StockAnalysis.WAITING, // StockAnalysis 모델 정의 필요
                updated_at: null,
                summary: response.data?.message,
                sentiment_stats: {},
                overall_sentiment_display: "정보 없음",
                stock_code_display: stockInfoFromList?.stock?.stock_code || 'N/A',
                company_name_display: stockInfoFromList?.stock?.company_name || '알 수 없음',
            };
        } else {
            this.currentSearchedStock = response.data;
            this.currentSearchedStock.stock_code_display = response.data.stock?.stock_code;
            this.currentSearchedStock.company_name_display = response.data.stock?.company_name;
        }
      } catch (err) {
        console.error(`Error fetching saved analysis for ${interestStockId}:`, err);
        const stockDisplayName = stockInfoFromList?.stock?.company_name || `ID ${interestStockId}`;
         if (err.response) {
            if (err.response.status === 204 || err.response.status === 202) {
                 this.actionMessage = err.response.data?.message || `${stockDisplayName} 분석 결과가 없거나 진행 중입니다.`;
                 this.currentSearchedStock = {
                     stock: stockInfoFromList?.stock || { company_name: '알 수 없음', stock_code: 'N/A' },
                     batch_ready: false, task_status: err.response.data?.task_status || 'waiting',
                     updated_at: null, summary: err.response.data?.message, sentiment_stats: {},
                     overall_sentiment_display: "정보 없음",
                     stock_code_display: stockInfoFromList?.stock?.stock_code || 'N/A',
                     company_name_display: stockInfoFromList?.stock?.company_name || '알 수 없음',
                 };
            } else {
                 this.analysisError = `'${stockDisplayName}' 저장된 분석 정보 로드 실패: ${err.response.data?.error || err.response.data?.detail || err.message}`;
            }
        } else {
            this.analysisError = `'${stockDisplayName}' 저장된 분석 정보 로드 중 네트워크 오류 또는 알 수 없는 오류 발생`;
        }
      } finally {
        this.isLoadingAnalysis = false;
      }
    },

    async addInterestAndRequestAnalysis(stockCode, companyName) {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        this.actionMessage = '관심 종목 추가 및 분석을 요청하려면 로그인이 필요합니다.';
        return;
      }
      if (!stockCode || !companyName) {
        this.actionMessage = '종목 코드와 회사명을 모두 입력해주세요.';
        return;
      }

      this.isLoadingAnalysis = true;
      this.actionMessage = null;
      this.analysisError = null;

      try {
        // ★★★ 수정: 전역 api 인스턴스 사용 및 경로 수정 ★★★
        const response = await api.post(`v1/insight/interest-stock/add-and-analyze/`, { stock_code: stockCode, company_name: companyName });
        
        this.actionMessage = response.data.message;
        this.fetchMyInterestStocks(); 
        
        const newInterestStock = response.data.interest_stock || response.data.stock_data || response.data.stock; // 백엔드 응답에 따라 유연하게 처리
        if (newInterestStock) {
            this.currentSearchedStock = {
                stock: newInterestStock, 
                batch_ready: false,
                task_status: response.data.task_status || 'WAITING', 
                updated_at: new Date().toISOString(), 
                summary: response.data.message || "백그라운드 분석 요청됨.",
                sentiment_stats: {},
                overall_sentiment_display: "분석 대기 중",
                stock_code_display: newInterestStock?.stock_code,
                company_name_display: newInterestStock?.company_name,
            };
        } else {
            this.actionMessage = response.data.message || "분석이 요청되었으나 상세 정보는 목록에서 확인해주세요.";
        }

      } catch (err) {
        console.error(`Error adding interest stock ${stockCode}:`, err);
        this.analysisError = err.response?.data?.error || err.response?.data?.detail || `관심 종목 '${companyName}' 추가 및 분석 요청에 실패했습니다.`;
      } finally {
        this.isLoadingAnalysis = false;
      }
    },
    // clearCurrentAnalysis는 clearSelectedStockAnalysis로 대체되었으므로 삭제하거나 그대로 둡니다.
    // clearSelectedStockAnalysis가 이미 동일/유사 기능을 하므로, 하나로 통일하는 것이 좋습니다.
  },
});