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
    loading.value = true
    loginError.value = null
    try {
      const response = await api.post('/api/accounts/login/', credentials) // DRF Simple JWT 기본 로그인 URL
      // 또는 accounts.api.urls.py 에 정의된 /api/token/ 사용 시
      // const response = await api.post('/api/token/', credentials) 

      // Simple JWT 사용 시 응답에 access 토큰이 있음
      const accessToken = response.data.access || response.data.token 
      if (!accessToken) {
        throw new Error('Access token not found in login response')
      }

      localStorage.setItem('token', accessToken)
      token.value = accessToken
      api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`

      // (선택사항) 로그인 후 사용자 정보 가져오기
      // await fetchUser(); 

      router.push({ name: 'home' }) // 로그인 성공 후 홈으로 이동
    } catch (error) {
      console.error('Login failed:', error.response?.data || error.message)
      loginError.value = error.response?.data?.detail || '로그인에 실패했습니다. 아이디 또는 비밀번호를 확인하세요.'
      localStorage.removeItem('token')
      token.value = null
      delete api.defaults.headers.common['Authorization']
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    // (선택사항) '/api/accounts/me/' 같은 엔드포인트에서 사용자 정보 가져오기
    // if (token.value) {
    //   try {
    //     const response = await api.get('/api/accounts/me/');
    //     user.value = response.data;
    //   } catch (error) {
    //     console.error('Failed to fetch user:', error);
    //     // 토큰이 유효하지 않을 수 있으므로 로그아웃 처리
    //     logout();
    //   }
    // }
  }

  function logout() {
    localStorage.removeItem('token')
    token.value = null
    user.value = null
    delete api.defaults.headers.common['Authorization']
    router.push({ name: 'LoginView' }) // 로그아웃 후 로그인 페이지로 이동
  }

  // 앱 시작 시 토큰이 있다면 사용자 정보 가져오기 시도 (선택적)
  // if (token.value) {
  //   fetchUser();
  // }

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