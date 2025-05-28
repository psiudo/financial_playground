import { defineStore } from 'pinia';
import axios from 'axios';

// 백엔드 API 기본 URL (Django 서버 주소에 맞게 수정)
const API_BASE_URL = 'http://127.0.0.1:8000'; 

export const useSentimentStore = defineStore('sentiment', {
  state: () => ({
    sentimentResult: null,    // API로부터 받은 감정 분석 결과 (예: "positive", "negative")
    isLoading: false,         // API 요청 중 로딩 상태
    error: null,              // API 요청 실패 시 에러 메시지
    analyzedText: '',         // 분석을 요청했던 원본 텍스트
  }),
  actions: {
    /**
     * 주어진 텍스트에 대한 감정 분석을 백엔드 API에 요청합니다.
     * @param {string} textToAnalyze - 분석할 텍스트
     */
    async analyzeText(textToAnalyze) {
      if (!textToAnalyze || textToAnalyze.trim() === '') {
        this.error = '분석할 텍스트를 입력해주세요.';
        this.sentimentResult = null;
        this.analyzedText = '';
        return;
      }

      this.isLoading = true;
      this.error = null;
      this.sentimentResult = null;
      this.analyzedText = textToAnalyze; // 분석 요청한 텍스트 저장

      try {
        // Django 백엔드의 감정 분석 API 엔드포인트
        const response = await axios.post(`${API_BASE_URL}/api/analysis/sentiment/`, {
          text: textToAnalyze,
        }
        // 만약 API가 인증 토큰을 요구한다면, 아래와 같이 헤더를 추가해야 합니다.
        // authStore 등에서 토큰을 관리하고 있다고 가정합니다.
        // , {
        //   headers: {
        //     'Authorization': `Token YOUR_AUTH_TOKEN_HERE` 
        //   }
        // }
        );
        
        // 백엔드 응답에서 'sentiment' 필드에 결과가 담겨 있다고 가정
        this.sentimentResult = response.data.sentiment; 

      } catch (err) {
        console.error('Error analyzing sentiment:', err.response ? err.response.data : err.message);
        this.error = err.response?.data?.error || '감정 분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
        this.sentimentResult = null;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * 분석 결과, 로딩 상태, 에러 메시지, 분석된 텍스트를 초기화합니다.
     */
    clearAnalysis() {
      this.sentimentResult = null;
      this.isLoading = false;
      this.error = null;
      this.analyzedText = '';
    }
  },
});