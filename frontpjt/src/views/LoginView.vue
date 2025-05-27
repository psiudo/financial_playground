<!-- front/src/views/LoginView.vue -->
<template>
  <div class="login-container">
    <h2>로그인</h2>
    <form @submit.prevent="login">
      <div>
        <label for="username">아이디</label>
        <input id="username" v-model="username" required />
      </div>
      <div>
        <label for="password">비밀번호</label>
        <input id="password" v-model="password" type="password" required />
      </div>
      <button type="submit">로그인</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script>
import api from '@/utils/api'

export default {
  name: 'LoginView',
  data() {
    return {
      username: '',
      password: '',
      error: null,
    }
  },
  methods: {
    async login() {
      try {
        const res = await api.post('/accounts/login/', {
          username: this.username,
          password: this.password,
        })
        localStorage.setItem('token', res.data.access)
        this.$router.push({ name: 'DashBoardView' })
      } catch (err) {
        this.error = '로그인 실패'
      }
    },
  },
}
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
