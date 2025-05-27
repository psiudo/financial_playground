<template>
  <header>
    <RouterLink to="/" class="logo-link">
      <img
        alt="Joomak logo"
        class="logo"
        src="@/assets/logo.svg"
        width="125"
        height="125"
      />
    </RouterLink>

    <div class="wrapper">
      <h1 class="site-title">주막에 오신 것을 환영합니다!</h1>

      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink :to="{ name: 'DashBoardView' }">대시보드</RouterLink>
        <RouterLink :to="{ name: 'MarketplaceView' }">마켓플레이스</RouterLink>
        <RouterLink :to="{ name: 'Commodities' }">기초자산</RouterLink>
        <RouterLink :to="{ name: 'StrategyListView' }">나의 전략</RouterLink>
        <RouterLink :to="{ name: 'FinancialProductListView' }">예적금 비교</RouterLink>

        <template v-if="authStore.isAuthenticated">
          <RouterLink :to="{ name: 'profile' }" class="ms-2">프로필</RouterLink>
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
// HelloWorld 임포트 제거
// import HelloWorld from './components/HelloWorld.vue';
import { useAuthStore } from '@/stores/authStore';
import { onMounted } from 'vue';

const authStore = useAuthStore();
const router = useRouter();

const handleLogout = () => {
  authStore.logout();
  // authStore.logout() 내부에서 페이지 이동 처리
};

onMounted(async () => {
  if (authStore.token && !authStore.user) {
    await authStore.fetchUser();
  }
});
</script>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
  /* Joomak 테마에 맞춰 헤더 배경색이나 구분선 등을 추가할 수 있습니다. */
  /* 예: border-bottom: 1px solid var(--joomak-border-subtle); */
  /* padding-bottom: 1rem; */
}

.logo-link {
  display: inline-block; /* 로고 크기에 맞게 영역 차지 */
}

.logo {
  display: block;
  margin: 0 auto 2rem; /* 기존 스타일 유지 */
}

.site-title {
  /* 필요에 따라 HelloWorld의 h1 스타일과 유사하게 또는 새롭게 정의 */
  font-weight: 500;
  font-size: 2.2rem; /* 적절한 크기로 조정 */
  color: var(--color-heading); /* Joomak 테마의 제목 색상 사용 */
  text-align: center;
  margin-bottom: 1.5rem; /* 네비게이션과의 간격 */
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 1rem; /* site-title과의 간격을 조정했으므로 필요시 재조정 */
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
  color: var(--color-text); /* Joomak 테마의 본문 텍스트 색상 */
  text-decoration: none;
  transition: color 0.3s, background-color 0.3s; /* 부드러운 전환 효과 */
}

nav a:first-of-type {
  border-left: 0;
}

/* 활성 링크 스타일 */
nav a.router-link-exact-active {
  color: var(--joomak-primary-dark); /* Joomak 테마의 강조 색상 (더 어둡게) */
  font-weight: bold; /* 활성 링크 강조 */
}

nav a.router-link-exact-active:hover {
  background-color: transparent; /* 활성 링크 호버 시 배경 변경 없음 */
}

/* 일반 링크 호버 스타일 */
nav a:not(.router-link-exact-active):not(.nav-link-button):hover {
  color: var(--joomak-primary); /* Joomak 테마의 기본 강조 색상 */
  background-color: rgba(var(--joomak-primary-rgb, 58, 95, 205), 0.1); /* Joomak 테마 색상 기반의 은은한 배경 (base.css에 --joomak-primary-rgb 추가 필요) */
}


/* 로그인/로그아웃 버튼 스타일 (기존 스타일 유지) */
.nav-link-button {
  padding: 0.375rem 0.75rem;
  border-radius: 0.25rem;
  text-decoration: none;
  color: #0d6efd;
  border: 1px solid #0d6efd;
  margin-left: 0.5rem;
  transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out;
}
.nav-link-button:hover {
  color: #fff;
  background-color: #0d6efd;
  border-color: #0d6efd;
}
/* 로그아웃 버튼 */
nav a[href="#"].nav-link-button {
  color: #dc3545;
  border-color: #dc3545;
}
nav a[href="#"].nav-link-button:hover {
  color: #fff;
  background-color: #dc3545;
  border-color: #dc3545;
}

/* --- 반응형 스타일 --- */
@media (min-width: 1024px) {
  header {
    display: flex;
    align-items: center; /* 수직 중앙 정렬 */
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo-link { /* 로고 링크 위치 조정 */
    margin-right: 2rem;
  }
  .logo {
    margin: 0; /* 로고 자체의 마진 제거 (부모에서 처리) */
  }

  header .wrapper {
    display: flex;
    flex-direction: column; /* 제목과 네비게이션을 수직으로 배치 */
    align-items: flex-start; /* 왼쪽 정렬 */
    flex-grow: 1; /* 남은 공간 채우기 */
  }

  .site-title {
    text-align: left; /* 데스크탑에서 제목 왼쪽 정렬 */
    font-size: 2.6rem; /* 데스크탑에서 제목 약간 더 크게 */
    margin-bottom: 0.5rem; /* 네비게이션과의 간격 줄임 */
  }

  nav {
    text-align: left;
    margin-left: -1rem; /* 기존 스타일 유지 */
    font-size: 1rem;
    padding: 0.5rem 0; /* 패딩 조정 */
    margin-top: 0; /* 제목 바로 아래에 오도록 */
  }
}
</style>