<!-- frontpjt/src/views/ProfileView.vue -->
<template>
  <div class="container mt-5">
    <h2>프로필 정보</h2>

    <div v-if="loadingProfile" class="alert alert-info">
      프로필 정보를 불러오는 중입니다...
    </div>

    <div v-if="profileError" class="alert alert-danger">
      프로필 정보를 불러오는데 실패했습니다: {{ profileError }}
    </div>

    <div v-if="user && !loadingProfile && !profileError" class="card">
      <div class="card-body">
        <h5 class="card-title">{{ user.username }}</h5>
        <p class="card-text">이메일: {{ user.email }}</p>
        <p class="card-text">가입일: {{ formatDate(user.signup_date) }}</p>
        <p class="card-text">포인트: {{ user.point_balance !== undefined ? user.point_balance : '정보 없음' }}</p>


        <hr>
        <h4>추가 정보 수정</h4>
        <form @submit.prevent="updateProfile">
          <div class="mb-3">
            <label for="birth_date" class="form-label">생년월일</label>
            <input type="date" class="form-control" id="birth_date" v-model="editableProfile.birth_date">
          </div>
          <div class="mb-3">
            <label for="job" class="form-label">직업</label>
            <input type="text" class="form-control" id="job" v-model="editableProfile.job">
          </div>
          <div class="mb-3">
            <label for="annual_income" class="form-label">연봉 (만원)</label>
            <input type="number" class="form-control" id="annual_income" v-model="editableProfile.annual_income" placeholder="숫자만 입력">
          </div>
          <div class="mb-3">
            <label for="risk_grade" class="form-label">투자 성향</label>
            <select class="form-select" id="risk_grade" v-model="editableProfile.risk_grade">
              <option value="">선택하세요</option>
              <option value="low">안정형</option>
              <option value="middle">중립형</option>
              <option value="high">공격형</option>
            </select>
          </div>
          <div class="mb-3">
            <label for="preferred_bank" class="form-label">선호 은행</label>
            <input type="text" class="form-control" id="preferred_bank" v-model="editableProfile.preferred_bank">
          </div>
          <div class="mb-3">
            <label for="bio" class="form-label">자기소개</label>
            <textarea class="form-control" id="bio" rows="3" v-model="editableProfile.bio"></textarea>
          </div>
          <button type="submit" class="btn btn-primary" :disabled="updatingProfile">
            <span v-if="updatingProfile" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            {{ updatingProfile ? '저장 중...' : '정보 수정' }}
          </button>
        </form>
        <div v-if="updateSuccess" class="alert alert-success mt-3" role="alert">
          프로필이 성공적으로 업데이트되었습니다!
        </div>
        <div v-if="updateError" class="alert alert-danger mt-3" role="alert">
          프로필 업데이트에 실패했습니다: {{ updateError }}
        </div>
      </div>
    </div>

    <hr v-if="user && !loadingProfile && !profileError" class="my-5">

    <h3 v-if="user && !loadingProfile && !profileError">가입한 금융상품 목록</h3>
    <div v-if="user && user.joined_financial_products && user.joined_financial_products.length > 0 && !loadingProfile && !profileError">
      <ul class="list-group">
        <li v-for="joined_item in user.joined_financial_products" :key="joined_item.id" class="list-group-item">
          <span v-if="joined_item.financial_product">
            {{ joined_item.financial_product.fin_prdt_nm }} - {{ joined_item.financial_product.kor_co_nm }}
          </span>
          <span v-else>
            상품 정보를 불러올 수 없습니다.
          </span>
          <p v-if="joined_item.joined_at">가입일: {{ formatDate(joined_item.joined_at) }}</p>
          <p v-if="joined_item.amount">가입 금액: {{ joined_item.amount }} 원</p>
        </li>
      </ul>
    </div>
    <div v-else-if="user && !loadingProfile && !profileError">
      <p>가입한 금융상품이 없습니다.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import api from '@/utils/api'

const authStore = useAuthStore()
const user = ref(authStore.user)
const loadingProfile = ref(false)
const profileError = ref(null)
const updatingProfile = ref(false)

const editableProfile = reactive({
  birth_date: '',
  job: '',
  annual_income: null,
  risk_grade: '',
  preferred_bank: '',
  bio: '',
})
const updateSuccess = ref(false)
const updateError = ref(null)

// **** 함수 정의를 watch보다 위로 옮깁니다. ****
const initializeEditableProfile = (userData) => {
  if (!userData) return; // userData가 null이나 undefined면 실행하지 않음
  editableProfile.birth_date = userData.birth_date || ''
  editableProfile.job = userData.job || ''
  editableProfile.annual_income = userData.annual_income ?? null
  editableProfile.risk_grade = userData.risk_grade || ''
  editableProfile.preferred_bank = userData.preferred_bank || ''
  editableProfile.bio = userData.bio || ''
}

// 스토어의 user 상태가 변경되면 ProfileView의 user ref도 업데이트
watch(() => authStore.user, (newUser) => {
  console.log('AuthStore user changed:', newUser); // 스토어 변경 감지 로그
  user.value = newUser
  if (newUser) {
    initializeEditableProfile(newUser); // 여기서 initializeEditableProfile 호출
  } else {
    // newUser가 null이면 (예: 로그아웃 시), editableProfile도 초기화하거나 적절히 처리
    Object.keys(editableProfile).forEach(key => {
      editableProfile[key] = (key === 'annual_income' ? null : '');
    });
  }
}, { immediate: true, deep: true }); // deep: true 추가하여 객체 내부 변경도 감지 (필요시)


const fetchUserProfile = async () => {
  if (!authStore.isAuthenticated) {
    profileError.value = '로그인이 필요합니다.';
    console.log('fetchUserProfile: Not authenticated');
    return;
  }
  loadingProfile.value = true
  profileError.value = null
  console.log('fetchUserProfile: Fetching profile...');
  try {
    if (!authStore.user) {
      console.log('fetchUserProfile: authStore.user is null, calling authStore.fetchUser()');
      await authStore.fetchUser();
    }
    // authStore.fetchUser()가 user.value를 업데이트하므로, watch가 initializeEditableProfile을 호출할 것임
    // 명시적으로 여기서 한 번 더 호출해도 되지만, watch의 immediate:true 와의 중복 실행 가능성 고려
    // user.value = authStore.user; // 이미 watch에서 처리 중
    
    if (!authStore.user) { // fetchUser 후에도 user가 없다면 오류 처리
      profileError.value = '사용자 정보를 가져오지 못했습니다.';
      console.log('fetchUserProfile: Failed to fetch user from store after authStore.fetchUser()');
    } else {
      console.log('fetchUserProfile: User data available in store:', authStore.user);
      // watch가 이미 처리하므로 여기서 initializeEditableProfile을 다시 호출할 필요는 없을 수 있음
      // 하지만 명확성을 위해 또는 watch가 예상대로 동작 안 할 경우를 대비해 호출 가능
      // initializeEditableProfile(authStore.user); 
    }

  } catch (error) {
    console.error('프로필 정보를 가져오는데 실패했습니다:', error)
    profileError.value = error.response?.data?.detail || '프로필 정보를 가져오는 중 오류가 발생했습니다.'
  } finally {
    loadingProfile.value = false
    console.log('fetchUserProfile: Fetching finished. Loading state:', loadingProfile.value);
  }
}

const updateProfile = async () => {
  updateSuccess.value = false
  updateError.value = null
  updatingProfile.value = true;
  console.log('updateProfile: Updating profile with data:', JSON.parse(JSON.stringify(editableProfile)));
  try {
    const payload = {}
    for (const key in editableProfile) {
      if (editableProfile[key] !== undefined) { // null도 유효한 값으로 보낼 수 있도록 수정
        if (key === 'annual_income' && (editableProfile[key] === '' || editableProfile[key] === null || isNaN(parseInt(editableProfile[key])))) {
            payload[key] = null;
        } else {
            payload[key] = editableProfile[key]
        }
      }
    }
    console.log('updateProfile: Payload to send:', payload);
    const response = await api.patch('/accounts/me/', payload)
    authStore.setUser(response.data) // 스토어 업데이트 (이로 인해 watch 실행, user.value 및 editableProfile 업데이트)
    updateSuccess.value = true
    console.log('updateProfile: Profile updated successfully.');
    setTimeout(() => updateSuccess.value = false, 3000);
  } catch (error) {
    console.error('프로필 업데이트 실패:', error.response ? error.response.data : error.message)
    updateError.value = error.response?.data ? JSON.stringify(error.response.data) : '서버 오류가 발생했습니다.'
  } finally {
    updatingProfile.value = false;
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR')
}

onMounted(() => {
  console.log('ProfileView: Component mounted.');
  fetchUserProfile()
})
</script>

<style scoped>
/* 필요한 경우 스타일 추가 */
.card {
  margin-bottom: 20px;
}
</style>