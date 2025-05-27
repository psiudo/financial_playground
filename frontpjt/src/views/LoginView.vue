<!-- frontpjt/src/views/LoginView.vue -->
<template>
  <div class="login-container">
    <h2>로그인</h2>
    <form @submit.prevent="performLogin">
      <div>
        <label for="username">아이디</label>
        <input id="username" v-model="credentials.username" required />
      </div>
      <div>
        <label for="password">비밀번호</label>
        <input id="password" v-model="credentials.password" type="password" required />
      </div>
      <button type="submit" :disabled="authStore.loading">
        {{ authStore.loading ? '로그인 중...' : '로그인' }}
      </button>
      <p v-if="authStore.loginError" class="error">{{ authStore.loginError }}</p>
    </form>
  </div>
</template>

<script setup> // ★ Composition API (script setup)으로 변경 권장
import { reactive } from 'vue';
import { useAuthStore } from '@/stores/authStore'; // ★ authStore 임포트
// import api from '@/utils/api'; // 더 이상 LoginView에서 직접 사용 안 함

const authStore = useAuthStore(); // ★ authStore 인스턴스 사용
const credentials = reactive({ // ★ username, password를 반응형 객체로 관리
  username: '',
  password: '',
});
// const error = ref(null); // authStore.loginError를 사용하므로 필요 없어짐

const performLogin = async () => { // ★ authStore.login 호출
  await authStore.login(credentials);
  // 로그인 성공/실패에 따른 페이지 이동 및 에러 표시는 authStore.login 내부에서 처리됩니다.
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.login-container h2 {
  text-align: center;
  margin-bottom: 20px;
}
.login-container div {
  margin-bottom: 15px;
}
.login-container label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}
.login-container input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.login-container button {
  width: 100%;
  padding: 10px;
  background-color: #5cb85c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}
.login-container button:disabled {
  background-color: #aaa;
}
.login-container button:hover:not(:disabled) {
  background-color: #4cae4c;
}
.error {
  color: red;
  margin-top: 10px;
  text-align: center;
}
</style>