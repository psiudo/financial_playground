<template>
  <div class="post-edit-view">
    <h2>게시글 수정</h2>
    <form @submit.prevent="submitEdit" v-if="communityStore.post">
      <div class="form-group">
        <label for="title">제목</label>
        <input type="text" id="title" v-model="editablePost.title" required />
      </div>
      <div class="form-group">
        <label for="content">내용</label>
        <textarea id="content" v-model="editablePost.content" rows="10" required></textarea>
      </div>
      <button type="submit" :disabled="communityStore.isLoading">
        {{ communityStore.isLoading ? '수정 중...' : '수정 완료' }}
      </button>
      <button type="button" @click="cancelEdit">취소</button>
      <div v-if="communityStore.error" class="error-message">
        오류: {{ communityStore.error.message || communityStore.error }}
      </div>
    </form>
    <div v-else-if="communityStore.isLoading">게시글 정보 로딩 중...</div>
    <div v-else>수정할 게시글 정보를 불러올 수 없습니다.</div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useCommunityStore } from '@/stores/communityStore';

const route = useRoute();
const router = useRouter();
const communityStore = useCommunityStore();

const postId = ref(route.params.postId);
const editablePost = ref({
  title: '',
  content: '',
  // 기존 게시글의 다른 필드들도 포함 가능
});

onMounted(async () => {
  if (postId.value) {
    // 기존 데이터를 불러와 폼에 채우기
    // 스토어에 이미 post 데이터가 있다면 사용, 없다면 fetchPost 호출
    if (!communityStore.post || communityStore.post.id !== parseInt(postId.value)) {
      await communityStore.fetchPost(postId.value);
    }
    // fetchPost가 완료된 후 스토어의 post 상태를 editablePost에 복사
    if (communityStore.post) {
      editablePost.value.title = communityStore.post.title;
      editablePost.value.content = communityStore.post.content;
      // 필요한 다른 필드들도 복사
    }
  }
});

// 스토어의 post가 변경될 때 editablePost 업데이트 (선택적, onMounted에서 충분할 수 있음)
watch(() => communityStore.post, (newPost) => {
  if (newPost && newPost.id === parseInt(postId.value)) {
    editablePost.value.title = newPost.title;
    editablePost.value.content = newPost.content;
  }
}, { immediate: true });


const submitEdit = async () => {
  if (!editablePost.value.title.trim() || !editablePost.value.content.trim()) {
    alert('제목과 내용을 모두 입력해주세요.');
    return;
  }

  try {
    await communityStore.updatePost(postId.value, {
      title: editablePost.value.title,
      content: editablePost.value.content,
      // TODO: 수정된 다른 필드들도 포함
    });
    alert('게시글이 성공적으로 수정되었습니다.');
    router.push({ name: 'postDetail', params: { postId: postId.value } });
  } catch (error) {
    console.error('게시글 수정 실패:', error);
    // alert('게시글 수정에 실패했습니다.');
  }
};

const cancelEdit = () => {
  router.back(); // 또는 상세 페이지로 이동
};
</script>

<style scoped>
/* PostCreateView.vue와 유사한 스타일 사용 가능 */
.post-edit-view {
  max-width: 700px;
  margin: 20px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
}
.form-group {
  margin-bottom: 15px;
}
.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}
.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}
textarea {
  resize: vertical;
}
button {
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
}
button[type="button"] {
  background-color: #6c757d;
}
button:disabled {
  background-color: #ccc;
}
.error-message {
  color: red;
  margin-top: 10px;
}
</style>