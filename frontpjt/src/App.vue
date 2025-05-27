<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router';
import HelloWorld from './components/HelloWorld.vue'; // 기존 HelloWorld 컴포넌트는 유지하거나 필요에 따라 제거하셔도 됩니다.
import { computed, onMounted, ref } from 'vue'; // onMounted, ref 추가

// Pinia 스토어를 사용한다면 여기서 import 합니다.
// 예: import { useAuthStore } from '@/stores/auth';
// const authStore = useAuthStore();

const router = useRouter();

// Pinia 스토어를 사용하지 않고 localStorage의 토큰 유무로 로그인 상태를 판단하는 예시
const isLoggedIn = ref(false); // 로그인 상태를 반응형 변수로 선언

// 컴포넌트가 마운트될 때 로그인 상태를 확인하는 함수
const checkLoginStatus = () => {
  const token = localStorage.getItem('token');
  isLoggedIn.value = !!token; // 토큰이 있으면 true, 없으면 false
};

// 컴포넌트 마운트 시 로그인 상태 확인
onMounted(() => {
  checkLoginStatus();
  // 라우터 변경 시에도 로그인 상태를 다시 확인할 수 있도록 이벤트를 감지할 수 있습니다.
  // 또는 Pinia 스토어의 상태를 구독하여 자동으로 업데이트되도록 할 수 있습니다.
});

const logout = () => {
  localStorage.removeItem('token'); // 로컬 스토리지에서 토큰 제거
  isLoggedIn.value = false; // 로그인 상태 업데이트
  // authStore.logout(); // Pinia 스토어 사용 시
  alert('로그아웃 되었습니다.');
  router.push('/login'); // 로그아웃 후 로그인 페이지로 이동
};
</script>

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
        <RouterLink to="/dashboard">대시보드</RouterLink>
        <RouterLink to="/marketplace">마켓플레이스</RouterLink>
        <RouterLink to="/commodities">기초자산</RouterLink>
        <RouterLink to="/strategies">나의 전략</RouterLink>
        <template v-if="isLoggedIn">
          <a href="#" @click.prevent="logout">로그아웃</a>
        </template>
        <template v-else>
          <RouterLink to="/login">로그인</RouterLink>
          </template>
      </nav>
    </div>
  </header>

  <RouterView />
</template>

<style scoped>
/* 기존 스타일은 대부분 유지하되, 필요시 수정합니다. */
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
}

nav a:first-of-type {
  border: 0;
}

/* 로그아웃 링크를 버튼처럼 보이게 하기 위한 예시 스타일 */
nav a[href="#"] {
  cursor: pointer;
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