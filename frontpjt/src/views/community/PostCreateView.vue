<!-- frontpjt/src/views/community/PostCreateView.vue -->
<template>
  <div class="post-create-view">
    <h2>새 게시글 작성</h2>
    <form @submit.prevent="submitPost">
      <div class="form-group">
        <label for="title">제목</label>
        <input type="text" id="title" v-model="title" required />
      </div>
      <div class="form-group">
        <label for="content">내용</label>
        <textarea id="content" v-model="content" rows="10" required></textarea>
      </div>
      
      <button type="submit" :disabled="communityStore.isLoading">
        {{ communityStore.isLoading ? '등록 중...' : '등록' }}
      </button>
      <div v-if="communityStore.error" class="error-message">
        오류: {{ communityStore.error.detail || communityStore.error.message || JSON.stringify(communityStore.error) }}
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router'; // useRoute 임포트
import { useCommunityStore } from '@/stores/communityStore';

const title = ref('');
const content = ref('');

const communityStore = useCommunityStore();
const router = useRouter();
const route = useRoute(); // route 인스턴스 생성

const submitPost = async () => {
  if (!title.value.trim() || !content.value.trim()) {
    alert('제목과 내용을 모두 입력해주세요.');
    return;
  }

  const postData = {
    title: title.value,
    content: content.value,
  };

  try {
    const newPost = await communityStore.createPost(postData); 
    alert('게시글이 성공적으로 등록되었습니다.');
    
    const boardTypeFromRoute = route.params.boardType || 'all'; // 현재 라우트 파라미터 사용
    router.push({ name: 'postList', params: { boardType: boardTypeFromRoute } });
    
  } catch (error) {
    console.error('PostCreateView.vue - 게시글 등록 실패:', error);
    // 오류 메시지는 communityStore.error를 통해 template에서 이미 표시될 수 있습니다.
  }
};
</script>

<style scoped>
.post-create-view {
  max-width: 700px;
  margin: 2rem auto;
  padding: 25px;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  background-color: #fff;
}
.post-create-view h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: var(--color-heading);
}
.form-group {
  margin-bottom: 1.5rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-text-soft, #333); /* 테마 변수 또는 기본값 */
}
.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ccc;
  border-radius: 6px;
  box-sizing: border-box; 
  font-size: 1rem;
}
.form-group textarea {
  resize: vertical;
  min-height: 150px;
}
button[type="submit"] {
  display: block;
  width: 100%;
  padding: 12px 15px;
  background-color: var(--joomak-primary, #007bff); 
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.1rem;
  transition: background-color 0.2s;
}
button[type="submit"]:disabled {
  background-color: #aaa;
  cursor: not-allowed;
}
button[type="submit"]:hover:not(:disabled) {
  background-color: var(--joomak-primary-dark, #0056b3); 
}
.error-message {
  color: red;
  margin-top: 1rem;
  text-align: center;
}
</style>