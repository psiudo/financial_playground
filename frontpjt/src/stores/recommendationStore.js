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
  const isFallbackResult = ref(false) // 추천 로직이 실패했을 때 일반 인기 상품 등을 보여줬는지 여부
  const needsProfileUpdate = ref(false) // 프로필 업데이트가 필요한지 여부

  const authStore = useAuthStore()
  const hasRecommendations = computed(() => recommendedProducts.value.length > 0)

  async function fetchRecommendations(forceRefresh = false) {
    // 캐시된 데이터 사용 로직 (옵션)
    if (recommendedProducts.value.length > 0 && !forceRefresh && !needsProfileUpdate.value && !isFallbackResult.value) {
      console.log('recommendationStore: Using cached recommendations.')
      return
    }

    console.log('recommendationStore: Attempting to fetch recommendations...')
    isLoading.value = true
    error.value = null
    needsProfileUpdate.value = false // API 호출 전 초기화
    isFallbackResult.value = false   // API 호출 전 초기화
    recommendationMessage.value = '' // 메시지 초기화

    if (!authStore.isAuthenticated) {
      error.value = '추천을 받으려면 로그인이 필요합니다.'
      isLoading.value = false
      clearRecommendations() // 추천 목록 및 관련 상태 초기화
      console.warn('recommendationStore: User not authenticated.')
      return
    }

    // authStore.user가 로드될 때까지 기다리거나, fetchUser를 호출합니다.
    if (!authStore.user) {
      console.log('recommendationStore: User data not in authStore, fetching user...')
      await authStore.fetchUser() // authStore의 fetchUser는 내부적으로 user를 설정해야 합니다.
      if (!authStore.user) {
        error.value = '사용자 정보를 가져올 수 없어 추천을 진행할 수 없습니다.'
        isLoading.value = false
        console.error('recommendationStore: Failed to fetch user data from authStore.')
        return
      }
    }
    
    // 사용자 프로필 정보 확인 (예: 투자 성향, 생년월일)
    if (!authStore.user.risk_grade || !authStore.user.birth_date) {
      console.warn('recommendationStore: User profile data (risk_grade or birth_date) is insufficient for personalized recommendations.')
      // 이 경우, 백엔드에서 is_fallback=true와 함께 일반 추천을 제공하거나,
      // 프론트에서 프로필 업데이트를 유도하는 메시지를 설정할 수 있습니다.
      recommendationMessage.value = '맞춤 추천을 받으려면 프로필에서 투자 성향과 생년월일을 먼저 입력해주세요.'
      recommendedProducts.value = [] // 이전에 있던 추천은 초기화
      needsProfileUpdate.value = true // 프로필 업데이트 필요 상태로 설정
      isLoading.value = false
      return // 추천 API 호출 중단
    }

    try {
      // ★★★ API 호출 경로 수정: 'v1/' 추가 ★★★
      // utils/api.js의 baseURL이 'http://127.0.0.1:8000/api' 이므로,
      // 전체 경로는 'http://127.0.0.1:8000/api/v1/products/recommendations/'가 됩니다.
      const response = await api.get('v1/products/recommendations/') // 수정된 경로

      console.log('recommendationStore: API response received:', response.data)

      // API 응답 구조에 따라 유연하게 처리
      if (response.data && response.data.recommended_products) {
        recommendedProducts.value = response.data.recommended_products
        recommendationMessage.value = response.data.message || '추천 상품 목록입니다.'
        isFallbackResult.value = response.data.is_fallback || false // 백엔드가 이 값을 제공한다고 가정

        if (recommendedProducts.value.length === 0 && !response.data.is_fallback) {
          // 맞춤 추천 결과가 없는 경우
          recommendationMessage.value = response.data.message || '현재 조건에 맞는 추천 상품을 찾지 못했습니다.'
        } else if (response.data.is_fallback && recommendedProducts.value.length === 0) {
          // 폴백 결과조차 없는 경우 (예: DB에 상품이 아예 없는 극단적 상황)
           recommendationMessage.value = response.data.message || '추천 상품을 준비 중입니다. 프로필을 업데이트하거나 잠시 후 다시 시도해주세요.'
        }
      } else {
        // 예상치 못한 응답 구조
        throw new Error('API 응답 형식이 올바르지 않습니다 (recommended_products 키 부재).')
      }

    } catch (err) {
      console.error('recommendationStore: Error fetching recommendations:', err.response?.data || err.message, err)
      // 에러 처리 로직 세분화
      if (err.response) {
        if (err.response.status === 401) {
          error.value = '인증 오류가 발생했습니다. 다시 로그인해주세요.'
          // authStore.logout(); // 필요시 자동 로그아웃
        } else if (err.response.status === 404) {
          error.value = '추천 API 경로를 찾을 수 없습니다. (404 Not Found)'
        } else if (err.response.data && err.response.data.message) {
          // 백엔드에서 is_fallback과 함께 message를 보내는 경우 (예: 프로필 부족으로 인한 폴백 안내)
          error.value = err.response.data.message;
          if (err.response.data.is_fallback) { // 이 키가 백엔드 응답에 있다면
             needsProfileUpdate.value = true; // 프로필 업데이트 유도
             recommendationMessage.value = err.response.data.message; // 에러 대신 안내 메시지로 표시
          }
        } else {
          error.value = `추천 상품을 불러오는 중 오류가 발생했습니다. (상태: ${err.response.status})`
        }
      } else {
        error.value = '추천 상품을 불러오는 중 네트워크 오류 또는 알 수 없는 문제가 발생했습니다.'
      }
      recommendedProducts.value = [] // 오류 시 기존 추천 목록은 비움
      // needsProfileUpdate가 true가 아닌 경우에만 error.value를 recommendationMessage로 설정
      if (!needsProfileUpdate.value) {
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

  // 프로필이 업데이트 되었을 때 호출될 수 있는 함수
  function refreshRecommendationsOnProfileUpdate() {
    console.log('recommendationStore: Profile updated, forcing refresh of recommendations.');
    // 캐시된 데이터 무시하고 강제 새로고침
    // 상태 초기화는 fetchRecommendations 시작 시 이루어지므로 중복 호출 피할 수 있음
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