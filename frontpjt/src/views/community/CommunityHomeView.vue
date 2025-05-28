<template>
  <div class="community-home">
    <h1>커뮤니티</h1>
    <p class="description">다양한 금융 정보와 투자 전략을 공유하고 소통하는 공간입니다.</p>
    
    <div class="board-links-container">
      <RouterLink :to="{ name: 'postList', params: { boardType: 'all' } }" class="board-link-card">
        <h2>📚 전체 글 보기</h2>
        <p>모든 게시판의 글을 한눈에 살펴보세요.</p>
      </RouterLink>
      <RouterLink :to="{ name: 'postList', params: { boardType: 'free' } }" class="board-link-card">
        <h2>💬 자유 게시판</h2>
        <p>어떤 주제든 자유롭게 이야기 나누는 공간입니다.</p>
      </RouterLink>
      <RouterLink :to="{ name: 'postList', params: { boardType: 'strategy' } }" class="board-link-card">
        <h2>📈 전략 공유 게시판</h2>
        <p>나만의 투자 전략, 분석, 노하우를 공유해주세요.</p>
      </RouterLink>
      <RouterLink :to="{ name: 'postList', params: { boardType: 'notice' } }" class="board-link-card">
        <h2>📢 공지사항</h2>
        <p>사이트 이용 관련 중요 안내를 확인하세요. (읽기 전용)</p>
      </RouterLink>
    </div>
    <hr class="divider"/>
    <p class="info-text">관심 있는 게시판을 선택하여 글을 읽거나 작성할 수 있습니다.</p>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router';
</script>

<style scoped>
.community-home {
  padding: 20px;
  max-width: 1000px; /* 콘텐츠 최대 너비 */
  margin: 2rem auto 0 auto; /* 상단 마진 및 중앙 정렬 */
  text-align: center; /* 내부 요소들 기본 중앙 정렬 */
}

.community-home h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  color: var(--color-heading);
}

.description {
  font-size: 1.1rem;
  color: var(--color-text-soft);
  margin-bottom: 2.5rem;
}

.board-links-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); /* 반응형 그리드 */
  gap: 20px; /* 카드 사이 간격 */
  margin-bottom: 2.5rem;
}

.board-link-card {
  display: block;
  padding: 25px 20px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  text-decoration: none;
  color: var(--color-text);
  background-color: var(--color-background-soft);
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  text-align: left; /* 카드 내부 텍스트 왼쪽 정렬 */
}

.board-link-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: var(--joomak-primary);
}

.board-link-card h2 {
  font-size: 1.5rem;
  color: var(--joomak-primary-dark);
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.board-link-card p {
  font-size: 0.95rem;
  color: var(--color-text-mute);
  line-height: 1.5;
}

.divider {
  border: 0;
  height: 1px;
  background-color: var(--color-border-hover);
  margin: 2rem 0;
}

.info-text {
  font-size: 0.9rem;
  color: #888;
}
</style>