<!-- frontpjt/src/views/community/PostDetailView.vue -->
<template>
  <div class="post-detail-view" v-if="communityStore.post">
    <h1>{{ communityStore.post.title }}</h1>
    <p><strong>작성자:</strong> {{ communityStore.post.author }}</p>
    <p><strong>작성일:</strong> {{ formatDate(communityStore.post.created_at) }}</p>
    <p><strong>수정일:</strong> {{ formatDate(communityStore.post.updated_at) }}</p>
    <hr />
    <div class="post-content" v-html="communityStore.post.content"></div>
    <hr />

    <div class="reactions">
      <h4>반응</h4>
      <button @click="toggleReaction('like')">👍 좋아요</button>
      <button @click="toggleReaction('useful')">💡 유용해요</button>
      <button @click="toggleReaction('hard')">🤔 어려워요</button>
      <button @click="toggleReaction('sad')">😢 슬퍼요</button>
      </div>
    <hr />

    <h3>댓글 ({{ communityStore.comments.length }})</h3>
    <div v-if="communityStore.isLoading && !communityStore.comments.length">댓글 로딩 중...</div>
    <div v-else-if="communityStore.comments.length === 0">작성된 댓글이 없습니다.</div>
    <ul v-else>
      <li v-for="comment in communityStore.comments" :key="comment.id" class="comment-item">
        <p><strong>{{ comment.author }}:</strong></p>
        <p v-if="comment.is_deleted" class="deleted-comment">[삭제된 댓글입니다]</p>
        <p v-else>{{ comment.content }}</p>
        <small>{{ formatDate(comment.created_at) }}</small>
        </li>
    </ul>

    <div class="comment-form">
      <textarea v-model="newCommentContent" placeholder="댓글을 입력하세요"></textarea>
      <button @click="submitComment" :disabled="!newCommentContent.trim() || communityStore.isLoading">
        {{ communityStore.isLoading ? '등록 중...' : '댓글 작성' }}
      </button>
    </div>

    </div>
  <div v-else-if="communityStore.isLoading">게시글 로딩 중...</div>
  <div v-else-if="communityStore.error" class="error-message">
    게시글을 불러오는 중 오류가 발생했습니다: {{ communityStore.error.message || communityStore.error }}
  </div>
  <div v-else>게시글을 찾을 수 없거나, 아직 로드되지 않았습니다.</div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
// import { RouterLink } from 'vue-router'; // <RouterLink> 사용 시 주석 해제
import { useCommunityStore } from '@/stores/communityStore'; // 이 경로를 다시 한번 확인해주세요.
// import { useAuthStore } from '@/stores/authStore'; // 작성자 확인 등 필요시 주석 해제

const route = useRoute();
const router = useRouter();
const communityStore = useCommunityStore();
// const authStore = useAuthStore(); // 필요시 주석 해제

const postId = ref(route.params.postId);
const newCommentContent = ref('');

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

onMounted(() => {
  if (postId.value) {
    communityStore.fetchPost(postId.value); // 게시글과 댓글을 함께 불러옴
  }
});

// const currentUser = computed(() => authStore.isLoggedIn ? authStore.user : null); // authStore에 user 객체가 있다고 가정
// const isAuthor = computed(() => {
//   return communityStore.post && currentUser.value && communityStore.post.author === currentUser.value.username;
//   // 백엔드 PostSerializer의 author 필드가 username 문자열을 반환한다고 가정.
//   // 또는 communityStore.post.author_id === currentUser.value.id 와 같이 ID로 비교 (백엔드 응답 확인 필요)
// });

const submitComment = async () => {
  if (!newCommentContent.value.trim()) {
    alert('댓글 내용을 입력해주세요.');
    return;
  }
  try {
    await communityStore.createComment(postId.value, { content: newCommentContent.value });
    newCommentContent.value = '';
    // createComment 액션 내부에서 댓글 목록을 갱신하거나, 여기서 fetchComments를 다시 호출할 수 있습니다.
    // 현재 communityStore.js의 createComment는 comments 배열에 push만 하므로,
    // 실시간 업데이트를 위해서는 fetchComments를 다시 호출하거나, 스토어 로직을 수정해야 할 수 있습니다.
    // await communityStore.fetchComments(postId.value); // 필요시 댓글 목록 다시 로드
  } catch (error) {
    console.error('댓글 작성 실패:', error);
    alert(`댓글 작성에 실패했습니다: ${error.message || '서버 오류'}`);
  }
};

const toggleReaction = async (reactionType) => {
  if (!postId.value) return;
  try {
    await communityStore.togglePostReaction(postId.value, reactionType);
    // communityStore의 togglePostReaction 액션에서 fetchPost를 호출하여 반응 수 등을 업데이트합니다.
  } catch (error) {
    console.error('반응 토글 실패:', error);
    alert(`반응 처리에 실패했습니다: ${error.message || '서버 오류'}`);
  }
};

// const deleteCurrentPost = async () => {
//   if (confirm('정말로 게시글을 삭제하시겠습니까?')) {
//     try {
//       await communityStore.deletePost(postId.value);
//       alert('게시글이 삭제되었습니다.');
//       router.push({ name: 'communityHome' }); // 또는 게시글 목록으로 이동
//     } catch (error) {
//       console.error('게시글 삭제 실패:', error);
//       alert(`게시글 삭제에 실패했습니다: ${error.message || '서버 오류'}`);
//     }
//   }
// };
</script>

<style scoped>
.post-detail-view {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #fff;
}
.post-content {
  margin-top: 15px;
  margin-bottom: 20px;
  white-space: pre-wrap; /* 줄바꿈 및 공백 유지 */
  line-height: 1.6;
}
.reactions {
  margin-bottom: 20px;
}
.reactions button {
  margin-right: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #ccc;
  cursor: pointer;
  background-color: #f8f9fa;
}
.reactions button:hover {
  background-color: #e9ecef;
}
.comment-form {
  margin-top: 20px;
  margin-bottom: 20px;
}
.comment-form textarea {
  width: 100%;
  min-height: 80px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
  margin-bottom: 10px;
}
.comment-form button {
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.comment-form button:disabled {
  background-color: #6c757d;
}
.comment-item {
  border-bottom: 1px solid #eee;
  padding: 10px 0;
}
.comment-item:last-child {
  border-bottom: none;
}
.comment-item p {
  margin: 5px 0;
}
.comment-item small {
  color: #6c757d;
  font-size: 0.85em;
}
.deleted-comment {
  color: #999;
  font-style: italic;
}
.author-actions {
  margin-top: 20px;
}
.author-actions a,
.author-actions button {
  margin-right: 10px;
}
.error-message {
  color: red;
  margin-top: 10px;
}
hr {
  margin-top: 20px;
  margin-bottom: 20px;
  border: 0;
  border-top: 1px solid #eee;
}
</style>