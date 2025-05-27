<template>
  <main class="home-view container py-4">
    <h1>주막에 오신 것을 환영합니다!</h1>
    <p class="lead">
      다양한 금융 정보와 투자 전략을 탐색하고, 맞춤형 금융 상품을 찾아보세요.
    </p>
    <div v-if="!authStore.isAuthenticated" class="mt-4">
      <RouterLink :to="{ name: 'LoginView' }" class="btn btn-primary btn-lg me-2">로그인</RouterLink>
      </div>
    <div v-else class="mt-4">
      <p>오늘도 성공적인 투자를 기원합니다, {{ authStore.user?.username }}님!</p>
      <RouterLink :to="{ name: 'DashBoardView' }" class="btn btn-info">대시보드로 이동</RouterLink>
    </div>
  </main>
</template>

<script setup> // ✅ 이 블록 하나만 사용합니다.
import { RouterLink } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';

const authStore = useAuthStore();

// 이전에 TheWelcome 임포트 관련 코드는 완전히 제거되어야 합니다.
// import TheWelcome from '../components/TheWelcome.vue' // <--- 이 줄은 없어야 합니다.
</script>

<style scoped>
.home-view {
  text-align: center;
}
.home-view h1 {
  color: var(--joomak-text-strong);
  margin-bottom: 1rem;
}
.home-view .lead {
  color: var(--joomak-text-body);
  margin-bottom: 2rem;
}
/* .btn-primary { background-color: var(--joomak-primary); border-color: var(--joomak-primary); }
.btn-primary:hover { background-color: var(--joomak-primary-dark); border-color: var(--joomak-primary-dark); }
.btn-info { background-color: var(--joomak-accent); border-color: var(--joomak-accent); }
.btn-info:hover { background-color: var(--joomak-accent-dark); border-color: var(--joomak-accent-dark); }
*/
</style>