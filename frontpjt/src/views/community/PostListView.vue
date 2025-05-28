<!-- frontpjt/src/views/community/PostListView.vue -->
<template>
  <div class="post-list-view"> <h2>{{ boardTitle }} 게시판</h2>
    <RouterLink :to="{ name: 'postCreate' }">글쓰기</RouterLink>

    <div v-if="communityStore.isLoading">게시글 로딩 중...</div>
    <div v-else-if="communityStore.error" class="error-message">
      게시글을 불러오는 중 오류가 발생했습니다: {{ communityStore.error.message || communityStore.error }}
    </div>
    <div v-else-if="!communityStore.posts || communityStore.posts.length === 0">게시글이 없습니다.</div>
    <ul v-else class="post-ul">
      <li v-for="item in communityStore.posts" :key="item.id" class="post-li">
        <RouterLink :to="{ name: 'postDetail', params: { postId: item.id } }">
          <h3>{{ item.title }}</h3>
        </RouterLink>
        <p class="post-meta">
          작성자: {{ item.author }} | 작성일: {{ formatDate(item.created_at) }}
          </p>
      </li>
    </ul>
    </div>
</template>

<script setup>
import { onMounted, computed, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import { useCommunityStore } from '@/stores/communityStore';

const props = defineProps({
  boardType: {
    type: String,
    default: 'all'
  }
});

const communityStore = useCommunityStore();
const route = useRoute();

const boardTitle = computed(() => {
  if (props.boardType === 'free') return '자유';
  if (props.boardType === 'strategy') return '전략 공유';
  if (props.boardType === 'notice') return '공지사항';
  return '커뮤니티'; // 기본 또는 전체 게시판 제목
});

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR', { 
    year: 'numeric', month: '2-digit', day: '2-digit',
    // hour: '2-digit', minute: '2-digit' // 필요시 시간도 표시
  });
};

onMounted(() => {
  communityStore.fetchPosts(props.boardType);
});

watch(() => route.params.boardType, (newBoardType) => {
  if (newBoardType) {
    communityStore.fetchPosts(newBoardType);
  } else if (route.name === 'communityHome') { // communityHome으로 직접 접근 시
     communityStore.fetchPosts('all'); // 또는 기본 게시판 타입
  }
}, { immediate: true }); // 컴포넌트 마운트 시에도 즉시 실행
</script>

<style scoped>
.post-list-view {
  padding: 20px;
  max-width: 960px; /* 적절한 최대 너비 설정 */
  margin: 2rem auto 0 auto; /* 상단 마진 및 중앙 정렬 */
}
.post-list-view h2 {
  margin-bottom: 1rem;
}
.post-list-view > a { /* 글쓰기 버튼 */
  display: inline-block;
  margin-bottom: 1rem;
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
}
.post-list-view > a:hover {
  background-color: #0056b3;
}
.post-ul {
  list-style: none;
  padding: 0;
}
.post-li {
  border: 1px solid #eee;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 5px;
}
.post-li h3 {
  margin: 0 0 5px 0;
  font-size: 1.25rem;
}
.post-li a {
  text-decoration: none;
  color: #333;
}
.post-li a:hover h3 {
  color: #007bff;
}
.post-meta {
  font-size: 0.9rem;
  color: #666;
}
.error-message {
  color: red;
}
</style>