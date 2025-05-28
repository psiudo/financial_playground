// frontpjt/src/stores/authStore.js
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '@/utils/api' // 백엔드 API 호출용
import router from '@/router' // 라우터 사용 (로그아웃 후 이동 등)

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token'))
  const user = ref(null) // 사용자 정보 (프로필 정보 등 저장)
  const loginError = ref(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  async function login(credentials) {
    console.log('authStore: login function CALLED with credentials:', credentials);
    loading.value = true
    loginError.value = null
    try {
      // ★★★ 수정된 부분: 로그인(토큰 발급) API 경로 변경 ★★★
      const response = await api.post('v1/accounts/login/', credentials) // Django Simple JWT의 TokenObtainPairView 경로

      const accessToken = response.data.access // Simple JWT는 access token을 'access' 키로 반환합니다.
      if (!accessToken) {
        throw new Error('Access token not found in login response')
      }

      localStorage.setItem('token', accessToken)
      token.value = accessToken
      console.log('authStore: token.value set to:', token.value)
      console.log('authStore: isAuthenticated is now:', isAuthenticated.value)
      api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`

      await fetchUser(); 

      router.push({ name: 'home' })
    } catch (error) {
      console.error('authStore: ERROR in login function:', error.response?.data || error.message, error);
      loginError.value = error.response?.data?.detail || '로그인에 실패했습니다. 아이디 또는 비밀번호를 확인하세요.'
      localStorage.removeItem('token')
      token.value = null
      user.value = null
      delete api.defaults.headers.common['Authorization']
    } finally {
      console.log('authStore: login function FINALLY block reached');
      loading.value = false
    }
  }

  function logout() {
    localStorage.removeItem('token')
    token.value = null
    user.value = null
    delete api.defaults.headers.common['Authorization']
    router.push({ name: 'LoginView' })
  }

  async function fetchUser() {
    if (token.value) {
      try {
        // ★★★ 수정된 부분: 사용자 정보 조회 API 경로 변경 ★★★
        const response = await api.get('v1/accounts/me/') // 사용자 정보 API 엔드포인트

        user.value = response.data
        console.log('authStore: User info fetched:', user.value)
      } catch (error) {
        console.error('authStore: Failed to fetch user info:', error.response?.data || error.message)
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          logout();
        }
      }
    }
  }

  function setUser(userData) {
    user.value = userData
    console.log('authStore: User info updated by setUser:', user.value)
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
    setUser
  }
})