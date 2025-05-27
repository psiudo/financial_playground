<template>
  <div class="login-container">
    <h2>로그인</h2>
    <form @submit.prevent="handleLogin">
      <div>
        <label for="username">아이디</label>
        <input id="username" v-model="username" required />
      </div>
      <div>
        <label for="password">비밀번호</label>
        <input id="password" v-model="password" type="password" required />
      </div>
      <button type="submit" :disabled="authStore.loading">
        {{ authStore.loading ? '로그인 중...' : '로그인' }}
      </button>
      <p v-if="authStore.loginError" class="error">{{ authStore.loginError }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/authStore'; // authStore 가져오기
// import { useRouter } from 'vue-router'; // 라우터 이동은 authStore에서 처리하므로 여기서는 필요 없을 수 있습니다.

const username = ref('');
const password = ref('');

const authStore = useAuthStore();
// const router = useRouter(); // authStore에서 라우터 이동을 담당

const handleLogin = async () => {
  // authStore의 loginError를 초기화해주는 것이 좋습니다 (선택 사항).
  // authStore.loginError = null; // authStore 내 login 함수 시작 시 이미 처리하고 있음

  // 이제 authStore의 login 함수를 호출합니다.
  // authStore.login 함수는 내부적으로 API 호출, 토큰 저장, 상태 업데이트, 라우터 이동까지 처리합니다.
  await authStore.login({
    username: username.value,
    password: password.value,
  });

  // 로그인 성공/실패에 따른 추가적인 처리가 필요하다면 여기서 할 수 있지만,
  // 대부분은 authStore 내부에서 처리하는 것이 좋습니다.
  // 예를 들어, 로그인 성공 시 authStore.isAuthenticated를 확인하거나,
  // 실패 시 authStore.loginError를 확인하여 UI에 반영할 수 있습니다.
  // (이미 템플릿에서 authStore.loginError를 사용하고 있습니다.)
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}
.error {
  color: red;
  margin-top: 10px;
}
</style>