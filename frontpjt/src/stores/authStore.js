// front/src/stores/authStore.js
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '@/utils/api' // 백엔드 API 호출용
import router from '@/router' // 라우터 사용 (로그아웃 후 이동 등)

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token'))
  const user = ref(null) // 사용자 정보 (필요시 상세 정보 저장)
  const loginError = ref(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  async function login(credentials) {
    // --- 함수 호출 확인용 로그 ---
    console.log('authStore: login function CALLED with credentials:', credentials);
    // --- 함수 호출 확인용 로그 끝 ---

    loading.value = true
    loginError.value = null
    try {
      const response = await api.post('token/', credentials)

      const accessToken = response.data.access || response.data.token
      if (!accessToken) {
        throw new Error('Access token not found in login response')
      }

      localStorage.setItem('token', accessToken)
      token.value = accessToken
      console.log('authStore: token.value set to:', token.value)
      console.log('authStore: isAuthenticated is now:', isAuthenticated.value)
      api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`

      router.push({ name: 'home' })
    } catch (error) {
      // --- 에러 블록 진입 확인용 로그 ---
      console.error('authStore: ERROR in login function:', error.response?.data || error.message, error);
      // --- 에러 블록 진입 확인용 로그 끝 ---
      loginError.value = error.response?.data?.detail || '로그인에 실패했습니다. 아이디 또는 비밀번호를 확인하세요.'
      localStorage.removeItem('token')
      token.value = null
      delete api.defaults.headers.common['Authorization']
    } finally {
      // --- finally 블록 진입 확인용 로그 ---
      console.log('authStore: login function FINALLY block reached');
      // --- finally 블록 진입 확인용 로그 끝 ---
      loading.value = false
    }
  }

  // ... (logout, fetchUser 함수 등은 동일) ...
  function logout() {
    localStorage.removeItem('token')
    token.value = null
    user.value = null
    delete api.defaults.headers.common['Authorization']
    router.push({ name: 'LoginView' }) // 로그아웃 후 로그인 페이지로 이동
  }

  async function fetchUser() {
    // (선택사항) '/api/accounts/me/' 같은 엔드포인트에서 사용자 정보 가져오기
  }

  return {
    token,
    user,
    isAuthenticated,
    loginError,
    loading,
    login,
    logout,
    fetchUser,
  }
})