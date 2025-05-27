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
      const response = await api.post('token/', credentials) // Django Simple JWT 기본 엔드포인트

      const accessToken = response.data.access || response.data.token // 응답 형식에 따라 access 또는 token 사용
      if (!accessToken) {
        throw new Error('Access token not found in login response')
      }

      localStorage.setItem('token', accessToken)
      token.value = accessToken
      console.log('authStore: token.value set to:', token.value)
      console.log('authStore: isAuthenticated is now:', isAuthenticated.value)
      api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`

      // 로그인 성공 후 사용자 정보 가져오기 (선택적)
      await fetchUser(); // 로그인 성공 시 사용자 정보를 바로 가져옵니다.

      router.push({ name: 'home' }) // 로그인 성공 후 홈으로 이동
    } catch (error) {
      console.error('authStore: ERROR in login function:', error.response?.data || error.message, error);
      loginError.value = error.response?.data?.detail || '로그인에 실패했습니다. 아이디 또는 비밀번호를 확인하세요.'
      localStorage.removeItem('token')
      token.value = null
      user.value = null // 사용자 정보도 초기화
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
    router.push({ name: 'LoginView' }) // 로그아웃 후 로그인 페이지로 이동
  }

  async function fetchUser() {
    if (token.value) { // 토큰이 있을 때만 사용자 정보 요청
      try {
        const response = await api.get('/accounts/me/') // 사용자 정보 API 엔드포인트
        user.value = response.data
        console.log('authStore: User info fetched:', user.value)
      } catch (error) {
        console.error('authStore: Failed to fetch user info:', error.response?.data || error.message)
        // 토큰이 유효하지 않은 경우 (예: 만료) 로그아웃 처리 등을 고려할 수 있습니다.
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          logout(); // 인증 오류 시 강제 로그아웃
        }
      }
    }
  }

  // 프로필 업데이트 등 사용자 정보가 변경되었을 때 스토어의 user 상태를 직접 업데이트하기 위한 함수
  function setUser(userData) {
    user.value = userData
    console.log('authStore: User info updated by setUser:', user.value)
  }

  // 페이지 로드 시 토큰이 있으면 사용자 정보 가져오기
  // 이 부분은 main.js나 App.vue의 onMounted에서 한 번 호출하는 것이 더 적절할 수 있습니다.
  // 여기서는 login 성공 시 fetchUser를 호출하는 것으로 변경했습니다.
  // if (token.value) {
  //   fetchUser()
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
    setUser // setUser 반환
  }
})