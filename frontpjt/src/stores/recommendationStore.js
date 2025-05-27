// frontpjt/src/stores/recommendationStore.js
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '@/utils/api' // Axios 인스턴스
import { useAuthStore } from './authStore' // 인증 스토어

export const useRecommendationStore = defineStore('recommendation', () => {
  // --- 상태 (State) ---
  const recommendedProducts = ref([])
  const recommendationMessage = ref('')
  const isLoading = ref(false)
  const error = ref(null)
  const isFallbackResult = ref(false)
  const needsProfileUpdate = ref(false)

  const authStore = useAuthStore()
  const hasRecommendations = computed(() => recommendedProducts.value.length > 0)

  async function fetchRecommendations(forceRefresh = false) {
    if (recommendedProducts.value.length > 0 && !forceRefresh && !needsProfileUpdate.value && !isFallbackResult.value) {
      console.log('recommendationStore: Using cached recommendations.')
      return
    }

    console.log('recommendationStore: Attempting to fetch recommendations...')
    isLoading.value = true
    error.value = null
    needsProfileUpdate.value = false
    isFallbackResult.value = false
    recommendationMessage.value = ''

    if (!authStore.isAuthenticated) {
      error.value = '추천을 받으려면 로그인이 필요합니다.'
      isLoading.value = false
      clearRecommendations()
      console.warn('recommendationStore: User not authenticated.')
      return
    }

    if (!authStore.user) {
      console.log('recommendationStore: User data not in authStore, fetching user...')
      await authStore.fetchUser()
      if (!authStore.user) {
        error.value = '사용자 정보를 가져올 수 없어 추천을 진행할 수 없습니다.'
        isLoading.value = false
        console.error('recommendationStore: Failed to fetch user data from authStore.')
        return
      }
    }
    
    if (!authStore.user.risk_grade || !authStore.user.birth_date) {
      console.warn('recommendationStore: User profile data (risk_grade or birth_date) is insufficient.')
      recommendationMessage.value = '맞춤 추천을 받으려면 프로필에서 투자 성향과 생년월일을 먼저 입력해주세요.'
      recommendedProducts.value = []
      needsProfileUpdate.value = true
      isLoading.value = false
      return
    }

    try {
      // ★★★ API 호출 경로 수정 ★★★
      // 백엔드의 Back/financial/urls.py 에 정의된 'api/products/' 와
      // Back/financial_products/api/urls.py 에 정의된 'recommendations/' 를 조합합니다.
      // api.js의 baseURL이 'http://127.0.0.1:8000/api/' 로 설정되어 있다고 가정합니다.
      const response = await api.get('products/recommendations/') // '/api/' 다음 부분만 적습니다.
      // 만약 api.js의 baseURL이 'http://127.0.0.1:8000/' 이라면, '/api/products/recommendations/' 로 해야 합니다.
      // 현재 utils/api.js 파일 내용을 모르므로, baseURL 설정에 따라 위 경로를 조정해야 할 수 있습니다.
      // 가장 일반적인 경우는 baseURL이 /api/로 끝나므로, 'products/recommendations/'가 맞을 것입니다.

      console.log('recommendationStore: API response received:', response.data)

      if (response.data && response.data.recommended_products) {
        recommendedProducts.value = response.data.recommended_products
        recommendationMessage.value = response.data.message || '추천 상품 목록입니다.'
        isFallbackResult.value = response.data.is_fallback || false

        if (recommendedProducts.value.length === 0 && !response.data.is_fallback) {
          recommendationMessage.value = response.data.message || '현재 조건에 맞는 추천 상품을 찾지 못했습니다.'
        } else if (response.data.is_fallback && recommendedProducts.value.length === 0) {
          recommendationMessage.value = response.data.message || '추천 상품을 준비 중입니다. 프로필을 업데이트하거나 잠시 후 다시 시도해주세요.'
        }
      } else {
        throw new Error('API 응답 형식이 올바르지 않습니다.')
      }

    } catch (err) {
      console.error('recommendationStore: Error fetching recommendations:', err.response?.data || err.message, err)
      if (err.response && err.response.status === 401) {
        error.value = '인증 오류가 발생했습니다. 다시 로그인해주세요.'
      } else if (err.response && err.response.data && err.response.data.message) {
        error.value = err.response.data.message
        if (err.response.data.is_fallback) {
            needsProfileUpdate.value = true;
            recommendationMessage.value = err.response.data.message;
        }
      } else if (err.response && err.response.status === 404) { // 404 에러 명시적 처리
        error.value = '추천 API 경로를 찾을 수 없습니다. (404 Not Found)'
        recommendationMessage.value = error.value;
      }
      else {
        error.value = '추천 상품을 불러오는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
      }
      recommendedProducts.value = []
      if(!needsProfileUpdate.value) { // 프로필 업데이트 필요 메시지가 아닐 경우에만 에러 메시지로 덮어쓰기
        recommendationMessage.value = error.value;
      }
    } finally {
      isLoading.value = false
      console.log('recommendationStore: Fetching finished. isLoading:', isLoading.value)
    }
  }

  function clearRecommendations() {
    recommendedProducts.value = []
    recommendationMessage.value = ''
    error.value = null
    isLoading.value = false
    isFallbackResult.value = false
    needsProfileUpdate.value = false
    console.log('recommendationStore: Recommendations and states cleared.')
  }

  function refreshRecommendationsOnProfileUpdate() {
    console.log('recommendationStore: Profile updated, forcing refresh of recommendations.');
    clearRecommendations();
    fetchRecommendations(true);
    
  }

  return {
    recommendedProducts,
    recommendationMessage,
    isLoading,
    error,
    isFallbackResult,
    needsProfileUpdate,
    hasRecommendations,
    fetchRecommendations,
    clearRecommendations,
    refreshRecommendationsOnProfileUpdate,
  }
})