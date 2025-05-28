// frontpjt/src/stores/communityStore.js
import { defineStore } from 'pinia';
import axios from 'axios';
import { useAuthStore } from './authStore'; // authStore 임포트

const API_URL = '/api/community'; // 이전 답변에서 수정한 URL ( /v1 제거됨 )

export const useCommunityStore = defineStore('community', {
  state: () => ({
    posts: [],
    post: null,
    comments: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    // 인증 헤더를 가져오는 헬퍼 함수
    getAuthHeaders() {
      const authStore = useAuthStore();
      if (authStore.isAuthenticated && authStore.token) {
        return { Authorization: `Bearer ${authStore.token}` };
      }
      return {};
    },

    async fetchPosts(boardType = null) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.get(`${API_URL}/posts/`, {
          headers: this.getAuthHeaders() // 인증 헤더 추가
        });
        this.posts = response.data;
      } catch (err) {
        this.error = err.response ? err.response.data : err;
        console.error('Error fetching posts:', this.error);
      } finally {
        this.isLoading = false;
      }
    },

    async fetchPost(postId) {
      this.isLoading = true;
      this.error = null;
      this.post = null; 
      this.comments = [];
      try {
        const postResponse = await axios.get(`${API_URL}/posts/${postId}/`, {
          headers: this.getAuthHeaders() // 인증 헤더 추가
        });
        this.post = postResponse.data;
        await this.fetchComments(postId);
      } catch (err) {
        this.error = err.response ? err.response.data : err;
        console.error(`Error fetching post ${postId}:`, this.error);
      } finally {
        this.isLoading = false;
      }
    },

    async createPost(postData) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.post(`${API_URL}/posts/`, postData, {
          headers: this.getAuthHeaders() // 인증 헤더 추가
        });
        if (response.data) {
          this.posts.unshift(response.data);
        }
        return response.data;
      } catch (err) {
        this.error = err.response ? err.response.data : err;
        console.error('Error creating post:', this.error);
        throw err; 
      } finally {
        this.isLoading = false;
      }
    },
    
    async fetchComments(postId) {
      this.error = null; 
      try {
        const response = await axios.get(`${API_URL}/posts/${postId}/comments/`, {
          headers: this.getAuthHeaders() // 인증 헤더 추가
        });
        this.comments = response.data;
      } catch (err) {
        this.error = err.response ? err.response.data : err; 
        console.error(`Error fetching comments for post ${postId}:`, this.error);
      }
    },

    async createComment(postId, commentData) {
      this.isLoading = true; 
      this.error = null;
      try {
        const response = await axios.post(`${API_URL}/posts/${postId}/comments/`, commentData, {
          headers: this.getAuthHeaders() // 인증 헤더 추가
        });
        if (response.data) { 
          this.comments.push(response.data); 
        }
        return response.data;
      } catch (err) {
        this.error = err.response ? err.response.data : err;
        console.error('Error creating comment:', this.error);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async togglePostReaction(postId, reactionType) {
      this.isLoading = true; 
      this.error = null;
      try {
        const currentPostId = parseInt(postId); // postId를 숫자로 변환
        const response = await axios.post(`${API_URL}/posts/${currentPostId}/toggle-reaction/?type=${reactionType}`, {}, {
          headers: this.getAuthHeaders() // 인증 헤더 추가
        });
        if (this.post && this.post.id === currentPostId) { 
          await this.fetchPost(currentPostId); 
        } else { 
          const postIndex = this.posts.findIndex(p => p.id === currentPostId);
          if (postIndex !== -1) {
            const updatedPost = await axios.get(`${API_URL}/posts/${currentPostId}/`, { headers: this.getAuthHeaders() });
            this.posts[postIndex] = updatedPost.data;
          }
        }
        return response.data;
      } catch (err) {
        this.error = err.response ? err.response.data : err;
        console.error(`Error toggling reaction for post ${postId}:`, this.error);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },
    
    async updatePost(postId, postData) {
      this.isLoading = true;
      this.error = null;
      const currentPostId = parseInt(postId);
      try {
        const response = await axios.put(`${API_URL}/posts/${currentPostId}/`, postData, {
          headers: this.getAuthHeaders() 
        });
        this.post = response.data; 
        const index = this.posts.findIndex(p => p.id === currentPostId);
        if (index !== -1) {
          this.posts[index] = response.data;
        }
        return response.data;
      } catch (err) {
        this.error = err.response ? err.response.data : err;
        console.error(`Error updating post ${postId}:`, err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async deletePost(postId) {
      this.isLoading = true;
      this.error = null;
      const currentPostId = parseInt(postId);
      try {
        await axios.delete(`${API_URL}/posts/${currentPostId}/`, {
          headers: this.getAuthHeaders() 
        });
        this.posts = this.posts.filter(p => p.id !== currentPostId);
        if (this.post && this.post.id === currentPostId) {
          this.post = null; 
        }
      } catch (err) {
        this.error = err.response ? err.response.data : err;
        console.error(`Error deleting post ${postId}:`, err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },
    
    async updateComment(postId, commentId, commentData) {
      this.isLoading = true;
      this.error = null;
      const currentPostId = parseInt(postId);
      try {
        const response = await axios.put(`${API_URL}/posts/${currentPostId}/comments/${commentId}/`, commentData, {
          headers: this.getAuthHeaders()
        });
        const index = this.comments.findIndex(c => c.id === commentId);
        if (index !== -1) {
          this.comments[index] = response.data;
        }
        return response.data;
      } catch (err) {
        this.error = err.response ? err.response.data : err;
        console.error(`Error updating comment ${commentId}:`, err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async deleteComment(postId, commentId) {
      this.isLoading = true;
      this.error = null;
      const currentPostId = parseInt(postId);
      try {
        await axios.delete(`${API_URL}/posts/${currentPostId}/comments/${commentId}/`, {
          headers: this.getAuthHeaders()
        });
        await this.fetchComments(currentPostId); 
      } catch (err) {
        this.error = err.response ? err.response.data : err;
        console.error(`Error deleting comment ${commentId}:`, err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },
  }
});