<template>
  <header>
    <img
      alt="Vue logo"
      class="logo"
      src="@/assets/logo.svg"
      width="125"
      height="125"
    />

    <div class="wrapper">
      <HelloWorld msg="금융 놀이터에 오신 것을 환영합니다!" />

      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink :to="{ name: 'DashBoardView' }">대시보드</RouterLink>
        <RouterLink :to="{ name: 'MarketplaceView' }">마켓플레이스</RouterLink>
        <RouterLink :to="{ name: 'Commodities' }">기초자산</RouterLink>
        <RouterLink :to="{ name: 'StrategyListView' }">나의 전략</RouterLink>
        
        <RouterLink :to="{ name: 'FinancialProductListView' }">예적금 비교</RouterLink>

        <template v-if="authStore.isAuthenticated">
          <a href="#" @click.prevent="handleLogout" class="ms-2 nav-link-button">로그아웃</a>
        </template>
        <template v-else>
          <RouterLink :to="{ name: 'LoginView' }" class="ms-2 nav-link-button">로그인</RouterLink>
        </template>
      </nav>
    </div>
  </header>

  <RouterView />
</template>

<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router';
import HelloWorld from './components/HelloWorld.vue'; // HelloWorld 컴포넌트 경로
import { useAuthStore } from '@/stores/authStore';   // authStore 사용

const authStore = useAuthStore();
const router = useRouter(); // useRouter는 페이지 이동 등에 사용될 수 있습니다.

const handleLogout = () => {
  authStore.logout(); 
  // authStore.logout() 내부에서 router.push('/login') 등으로 페이지 이동 처리가 되어있을 것입니다.
};

// App.vue가 마운트될 때 또는 authStore의 특정 상태를 감시(watch)하여
// 초기 사용자 정보를 가져오거나 토큰 유효성을 검사하는 로직을 추가할 수 있습니다.
// 예: onMounted(() => { if (authStore.token) authStore.fetchUser(); });
</script>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
  color: var(--color-text); /* 기본 링크 색상 */
  text-decoration: none; /* 밑줄 제거 */
}

nav a.router-link-exact-active {
  color: hsla(160, 100%, 37%, 1); /* 활성 링크 색상 (기존 Vue green) */
}

nav a:hover {
  background-color: hsla(160, 100%, 37%, 0.2); /* 호버 시 배경색 */
}

nav a:first-of-type {
  border: 0;
}

/* 로그아웃 링크 및 로그인 링크에 버튼 스타일을 좀 더 명확히 적용하기 위한 클래스 */
.nav-link-button {
  padding: 0.375rem 0.75rem; /* Bootstrap 버튼 패딩과 유사하게 */
  border-radius: 0.25rem;    /* 버튼 모서리 둥글게 */
  text-decoration: none;
  color: #0d6efd; /* Bootstrap primary 색상 예시 */
  border: 1px solid #0d6efd;
  margin-left: 0.5rem; /* 다른 링크와의 간격 */
  transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out;
}
.nav-link-button:hover {
  color: #fff;
  background-color: #0d6efd;
  border-color: #0d6efd;
}
/* 로그아웃 버튼에 대한 특별 스타일 (예: 빨간색 계열) */
nav a[href="#"].nav-link-button { /* 로그아웃 버튼 */
  color: #dc3545; /* Bootstrap danger 색상 예시 */
  border-color: #dc3545;
}
nav a[href="#"].nav-link-button:hover {
  color: #fff;
  background-color: #dc3545;
  border-color: #dc3545;
}


@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;
    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style>