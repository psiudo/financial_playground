<!-- frontpjt/src/views/DashBoardView.vue -->
<template>
  <div class="dashboard container py-4">
    <h1 class="mb-4">대시보드</h1>

    <div v-if="authStore.isLoading && !authStore.user" class="text-center"> <p>사용자 정보를 불러오는 중...</p>
    </div>
    <div v-else-if="!authStore.isAuthenticated || !authStore.user" class="alert alert-warning">
      <p>대시보드 내용을 보려면 먼저 <RouterLink :to="{ name: 'LoginView' }">로그인</RouterLink>해주세요.</p>
    </div>

    <div v-else>
      <section class="user-profile-summary mb-5 p-4 bg-light rounded shadow-sm">
        <h3 class="mb-3">안녕하세요, <span class="text-primary">{{ authStore.user.username }}</span>님!</h3>
        <p>오늘도 성공적인 금융 생활을 시작해보세요.</p>
        <RouterLink :to="{name: 'profile'}" class="btn btn-outline-secondary btn-sm">내 프로필 보기</RouterLink>
      </section>

      <section class="recommendations-section mb-5">
        <ProductRecommendationList /> {/* ★ 컴포넌트 사용 */}
      </section>

      <section class="portfolio-summary mb-5">
        <h3 class="mb-3">내 포트폴리오 요약 📈</h3>
        <div class="alert alert-info">
          포트폴리오 요약 정보가 여기에 표시될 예정입니다. (예: 총 자산, 수익률 등)
        </div>
      </section>

      <section class="recent-activity">
        <h3 class="mb-3">최근 활동 HISTORY 📝</h3>
        <div class="alert alert-info">
          최근 거래 내역 또는 활동 로그가 여기에 표시될 예정입니다.
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { RouterLink } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import ProductRecommendationList from '@/components/ProductRecommendationList.vue'; // ★ 추천 목록 컴포넌트 import

const authStore = useAuthStore();

onMounted(async () => {
  // 대시보드 진입 시 사용자 정보가 최신인지 확인
  // App.vue의 onMounted에서 이미 fetchUser를 호출하고 있을 수 있으므로,
  // 여기서는 authStore.user가 없는 경우에만 호출하거나,
  // 또는 특정 시간 간격으로 업데이트하는 로직을 고려할 수 있습니다.
  // 현재는 authStore.user가 없으면 가져오도록 합니다.
  if (authStore.isAuthenticated && !authStore.user) {
    console.log('DashboardView: User authenticated but no user data in store, fetching user...');
    await authStore.fetchUser();
  } else if (authStore.isAuthenticated && authStore.user) {
    console.log('DashboardView: User authenticated and user data exists in store.');
  } else {
    console.log('DashboardView: User not authenticated.');
  }
});
</script>

<style scoped>
.dashboard {
  max-width: 960px; /* 대시보드 최대 너비 설정 */
}
.user-profile-summary h3 span.text-primary {
  font-weight: bold;
}
</style>