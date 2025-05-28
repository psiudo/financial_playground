import { defineStore } from 'pinia';
import axios from 'axios';
import { useAuthStore } from './authStore';
// import router from '@/router'; // 필요시 라우터 사용

const API_BASE_URL = 'http://127.0.0.1:8000/api/insight';

export const useStockInsightStore = defineStore('stockInsight', {
  state: () => ({
    myInterestStocks: [],      // 사용자의 관심 종목 목록 (분석 상태 포함)
    currentSearchedStock: null, // 사용자가 직접 검색/분석 요청한 종목의 정보 및 분석 결과 (DB 저장과 무관)
    isLoadingList: false,      // 관심 종목 목록 로딩
    listError: null,           // 관심 종목 목록 에러
    isLoadingAnalysis: false,  // 개별 종목 분석 데이터 로딩 (실시간 또는 저장된 결과)
    analysisError: null,       // 개별 종목 분석 데이터 에러
    actionMessage: null,       // 분석 요청, 관심종목 추가 등의 결과 메시지
  }),
  getters: {
    formattedCurrentSentiment: (state) => {
      if (!state.currentSearchedStock || !state.currentSearchedStock.sentiment_stats) {
        return null;
      }
      const stats = state.currentSearchedStock.sentiment_stats;
      const total_analyzed = stats.positive + stats.negative + stats.neutral;
      return {
        positive: stats.positive || 0,
        negative: stats.negative || 0,
        neutral: stats.neutral || 0,
        error: stats.error || 0,
        total_analyzed: total_analyzed,
        total_fetched: stats.total_comments_fetched || 0,
        positive_percent: total_analyzed > 0 ? ((stats.positive || 0) / total_analyzed * 100).toFixed(1) : 0,
        negative_percent: total_analyzed > 0 ? ((stats.negative || 0) / total_analyzed * 100).toFixed(1) : 0,
        neutral_percent: total_analyzed > 0 ? ((stats.neutral || 0) / total_analyzed * 100).toFixed(1) : 0,
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
    // 실시간 종목 분석 (이름 또는 코드 기반)
    async analyzeStockOnTheFly(query, type = 'name') { // type: 'name' or 'code'
      if (!query) return;
      this.isLoadingAnalysis = true;
      this.analysisError = null;
      this.currentSearchedStock = null;
      this.actionMessage = null;
      
      const params = type === 'code' ? { code: query } : { name: query };

      try {
        const response = await axios.get(`${API_BASE_URL}/realtime-analysis/`, { params });
        this.currentSearchedStock = response.data; // API 응답 구조에 맞춰 저장
        if (response.data.stock) { // API 응답에 stock 정보가 있다면
            this.currentSearchedStock.stock_code_display = response.data.stock.stock_code;
            this.currentSearchedStock.company_name_display = response.data.stock.company_name;
        } else { // API 응답에 stock 정보가 없다면 (예: 크롤러에서 못찾은 경우)
            this.currentSearchedStock.stock_code_display = type === 'code' ? query : 'N/A';
            this.currentSearchedStock.company_name_display = type === 'name' ? query : ( type === 'code' ? query : 'N/A');
        }

      } catch (err) {
        console.error(`Error analyzing stock ${query}:`, err);
        this.analysisError = err.response?.data?.error || `'${query}' 종목 분석 중 오류가 발생했습니다.`;
        this.currentSearchedStock = { // 오류 시에도 기본 구조 유지
            stock: { company_name: type === 'name' ? query : query, stock_code: type === 'code' ? query : 'N/A' },
            summary: this.analysisError,
            sentiment_stats: {},
            batch_ready: false,
        };
      } finally {
        this.isLoadingAnalysis = false;
      }
    },

    // 사용자의 관심 종목 목록 가져오기 (분석 상태 포함)
    async fetchMyInterestStocks() {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        this.myInterestStocks = [];
        return;
      }
      this.isLoadingList = true;
      this.listError = null;
      try {
        const response = await axios.get(`${API_BASE_URL}/my-interest-stocks/`, {
          headers: { Authorization: `Token ${authStore.token}` }
        });
        this.myInterestStocks = response.data;
      } catch (err) {
        console.error('Error fetching my interest stocks:', err);
        this.listError = '관심 종목 목록을 가져오는데 실패했습니다.';
        this.myInterestStocks = [];
      } finally {
        this.isLoadingList = false;
      }
    },

    // 특정 관심 종목의 저장된 분석 결과 가져오기 (pk 기반)
    async fetchSavedAnalysis(interestStockId) {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated || !interestStockId) return;

      this.isLoadingAnalysis = true;
      this.analysisError = null;
      this.currentSearchedStock = null; // 이전 실시간 검색 결과 초기화
      this.actionMessage = null;

      // 선택된 관심 종목 정보 찾기
      const stockInfo = this.myInterestStocks.find(s => s.id === interestStockId);
      
      try {
        const response = await axios.get(`${API_BASE_URL}/my-interest-stock/${interestStockId}/sentiment/`, {
          headers: { Authorization: `Token ${authStore.token}` }
        });

        if (response.status === 204 || response.status === 202) { // 분석 결과 없거나 진행 중
            this.actionMessage = response.data?.message || `${stockInfo?.company_name || '선택 종목'}의 분석 결과가 없거나 진행 중입니다.`;
            // currentSearchedStock에 기본 정보와 task_status 등을 채워넣어 UI에서 활용
            this.currentSearchedStock = {
                stock: stockInfo || { company_name: '알 수 없음', stock_code: 'N/A' },
                batch_ready: false,
                task_status: response.data?.task_status || StockAnalysis.WAITING, // WAITING은 모델에 정의된 값
                updated_at: null,
                summary: response.data?.message,
                sentiment_stats: {},
                overall_sentiment_display: "정보 없음",
                stock_code_display: stockInfo?.stock_code || 'N/A',
                company_name_display: stockInfo?.company_name || '알 수 없음',
            };
        } else {
            this.currentSearchedStock = response.data;
            this.currentSearchedStock.stock_code_display = response.data.stock?.stock_code;
            this.currentSearchedStock.company_name_display = response.data.stock?.company_name;
        }
      } catch (err) {
        console.error(`Error fetching saved analysis for ${interestStockId}:`, err);
        const stockDisplayName = stockInfo?.company_name || `ID ${interestStockId}`;
         if (err.response) {
            if (err.response.status === 204 || err.response.status === 202) {
                 this.actionMessage = err.response.data?.message || `${stockDisplayName} 분석 결과가 없거나 진행 중입니다.`;
                 this.currentSearchedStock = {
                    stock: stockInfo || { company_name: '알 수 없음', stock_code: 'N/A' },
                    batch_ready: false, task_status: err.response.data?.task_status || 'waiting',
                    updated_at: null, summary: err.response.data?.message, sentiment_stats: {},
                    overall_sentiment_display: "정보 없음",
                    stock_code_display: stockInfo?.stock_code || 'N/A',
                    company_name_display: stockInfo?.company_name || '알 수 없음',
                };
            } else {
                this.analysisError = `'${stockDisplayName}' 저장된 분석 정보 로드 실패: ${err.response.data?.error || err.message}`;
            }
        } else {
            this.analysisError = `'${stockDisplayName}' 저장된 분석 정보 로드 중 네트워크 오류 또는 알 수 없는 오류 발생`;
        }
      } finally {
        this.isLoadingAnalysis = false;
      }
    },

    // 관심 종목 추가 및 분석 요청
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

      this.isLoadingAnalysis = true; // 버튼 로딩 상태 공유
      this.actionMessage = null;
      this.analysisError = null;

      try {
        const response = await axios.post(
          `${API_BASE_URL}/interest-stock/add-and-analyze/`,
          { stock_code: stockCode, company_name: companyName },
          { headers: { Authorization: `Token ${authStore.token}` } }
        );
        this.actionMessage = response.data.message;
        // 성공 시 관심 종목 목록 새로고침
        this.fetchMyInterestStocks(); 
        // 새로 추가된 종목을 currentSearchedStock으로 설정하고, 분석 대기 상태로 표시
        this.currentSearchedStock = {
            stock: response.data.interest_stock, // API가 생성된 interest_stock 정보 반환 가정
            batch_ready: false,
            task_status: 'waiting', // 또는 API 응답에서 받은 상태
            updated_at: new Date().toISOString(), // 임시로 현재 시간
            summary: "백그라운드 분석 요청됨.",
            sentiment_stats: {},
            overall_sentiment_display: "분석 대기 중",
            stock_code_display: response.data.interest_stock?.stock_code,
            company_name_display: response.data.interest_stock?.company_name,
        };

      } catch (err) {
        console.error(`Error adding interest stock ${stockCode}:`, err);
        this.analysisError = err.response?.data?.error || `관심 종목 '${companyName}' 추가 및 분석 요청에 실패했습니다.`;
      } finally {
        this.isLoadingAnalysis = false;
      }
    },

    clearCurrentAnalysis() {
      this.currentSearchedStock = null;
      this.isLoadingAnalysis = false;
      this.analysisError = null;
      this.actionMessage = null;
    }
  },
});