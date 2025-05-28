<template>
  <div class="bank-locations-view">
    <h1>내 주변 은행 찾기 (카카오 API 검색)</h1>
    <div class="search-bar">
      <input type="text" v-model="searchQuery" @keyup.enter="searchBanks" placeholder="은행명 또는 'OO역 은행' 입력" />
      <button @click="searchBanks">검색</button>
    </div>
    <div id="map" style="width:100%;height:500px;"></div>
    <div v-if="error" class="alert alert-danger mt-3" role="alert">
      <p class="mb-0">오류: {{ error }}</p>
    </div>
    <div v-if="loading && !error" class="d-flex justify-content-center mt-3">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="ms-2 mb-0">지도 또는 검색 결과를 불러오는 중...</p>
    </div>
    <div v-if="!loading && bankLocations.length === 0 && !error && searchAttempted" class="alert alert-info mt-3" role="alert">
      <p class="mb-0">검색 결과가 없습니다. 다른 검색어를 시도해보세요.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
// axios는 현재 이 검색 기능에서는 직접 사용하지 않지만,
// 다른 API 호출이 있다면 그대로 두셔도 됩니다.
// import axios from 'axios';

const mapContainer = ref(null);
const bankLocations = ref([]); // 카카오 API 검색 결과 또는 DB 데이터를 담을 배열
const loading = ref(true);
const error = ref(null);
let kakaoMapInstance = null;
let placesService = null; // Kakao Places 서비스 객체
const searchQuery = ref(''); // 사용자가 입력할 검색어
const searchAttempted = ref(false); // 검색 시도 여부

// VITE_API_BASE_URL은 현재 이 검색 기능에서는 직접 사용되지 않을 수 있습니다.
// const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';
const KAKAO_JS_KEY = import.meta.env.VITE_KAKAO_MAP_JS_KEY;

// 이전 마커들을 저장할 배열
let markers = [];

// Kakao SDK 스크립트를 동적으로 로드하고 API 준비를 확인하는 함수
function loadKakaoMapSDK() {
  return new Promise((resolve, reject) => {
    if (!KAKAO_JS_KEY) {
      const keyErrorMsg = "VITE_KAKAOMAP_JS_KEY가 .env 파일에 정의되지 않았습니다. 키를 설정해주세요.";
      console.error(keyErrorMsg);
      error.value = keyErrorMsg; // 화면에 에러 메시지 표시
      reject(new Error(keyErrorMsg));
      return;
    }

    if (window.kakao && window.kakao.maps && window.kakao.maps.services) {
      console.log('Kakao SDK (maps, services)가 이미 로드되어 있습니다.');
      if (!placesService) {
        placesService = new window.kakao.maps.services.Places();
      }
      resolve(window.kakao);
      return;
    }

    const scriptId = 'kakao-maps-sdk-script';
    if (document.getElementById(scriptId)) {
      console.log('Kakao SDK 스크립트가 이미 문서에 삽입되어 로드 중입니다.');
      // 로드 완료를 기다리는 로직 (간단화)
      let attempts = 0;
      const interval = setInterval(() => {
        attempts++;
        if (window.kakao && window.kakao.maps && window.kakao.maps.services) {
          clearInterval(interval);
          if (!placesService) {
            placesService = new window.kakao.maps.services.Places();
          }
          resolve(window.kakao);
        } else if (attempts > 50) { // 5초 대기
          clearInterval(interval);
          reject(new Error('기존 삽입된 Kakao SDK 로드 시간 초과.'));
        }
      }, 100);
      return;
    }

    console.log('Kakao SDK 스크립트를 동적으로 로드합니다 (services 라이브러리 포함).');
    const script = document.createElement('script');
    script.id = scriptId;
    script.type = 'text/javascript';
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${KAKAO_JS_KEY}&libraries=services&autoload=false`;
    script.async = true;

    script.onload = () => {
      console.log('Kakao SDK 스크립트 동적 로드 완료.');
      if (window.kakao && window.kakao.maps) {
        window.kakao.maps.load(() => {
          console.log('동적 로드된 maps API 사용 준비 완료 (kakao.maps.load 콜백).');
          if (!placesService) {
            placesService = new window.kakao.maps.services.Places();
            console.log('Places service 초기화 완료.');
          }
          resolve(window.kakao);
        });
      } else {
        const loadErrorMsg = "Kakao SDK는 로드되었으나, window.kakao.maps 객체를 찾을 수 없습니다.";
        console.error(loadErrorMsg);
        error.value = loadErrorMsg;
        reject(new Error(loadErrorMsg));
      }
    };

    script.onerror = (event) => {
      const scriptErrorMsg = "Kakao SDK 스크립트를 동적으로 로드하는 데 실패했습니다. 네트워크 연결, 앱키 및 등록된 사이트 도메인을 확인하세요.";
      console.error(scriptErrorMsg, event);
      error.value = scriptErrorMsg;
      reject(new Error(scriptErrorMsg));
    };

    document.head.appendChild(script);
  });
}

const initializeMap = (kakao) => {
  console.log("initializeMap 함수 호출됨");
  if (!mapContainer.value) {
    error.value = "지도 컨테이너(id='map')를 찾을 수 없습니다.";
    loading.value = false;
    console.error(error.value);
    return false;
  }
  const options = {
    center: new kakao.maps.LatLng(37.566826, 126.9786567), // 서울 시청 기본 중심
    level: 5
  };
  try {
    kakaoMapInstance = new kakao.maps.Map(mapContainer.value, options);
    console.log("카카오 지도 객체 생성됨:", kakaoMapInstance);

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          const userPosition = new kakao.maps.LatLng(lat, lng);
          if (kakaoMapInstance) {
            kakaoMapInstance.setCenter(userPosition);
            new kakao.maps.Marker({
              map: kakaoMapInstance,
              position: userPosition,
              title: '현재 위치'
            });
            console.log('사용자 현재 위치로 지도 중앙 이동 및 마커 표시됨.');
          }
        },
        (geoError) => {
          console.warn(`Geolocation 오류(${geoError.code}): ${geoError.message}. 기본 위치로 지도를 표시합니다.`);
        }
      );
    } else {
      console.warn("브라우저가 Geolocation을 지원하지 않습니다. 기본 위치로 지도를 표시합니다.");
    }
    return true;
  } catch (e) {
    error.value = "지도 객체 생성 중 오류 발생: " + e.message;
    loading.value = false;
    console.error(error.value, e);
    return false;
  }
};

// 기존 마커들을 지도에서 제거하는 함수
const clearMarkers = () => {
  for (let i = 0; i < markers.length; i++) {
    markers[i].setMap(null);
  }
  markers = [];
};

// 장소 검색 콜백 함수
const placesSearchCB = (data, status, pagination) => {
  searchAttempted.value = true;
  if (status === kakao.maps.services.Status.OK) {
    console.log(`${data.length}개의 장소 검색 결과 수신됨.`);
    // bankLocations.value = data; // 카카오 API의 응답 형식을 그대로 사용하거나, 필요한 정보만 추출
    bankLocations.value = data.map(place => ({
        id: place.id, // 장소 ID
        bank_name: place.place_name, // 장소명, 업체명
        branch_name: '', // API 응답에 지점명이 명확히 구분되어 있지 않다면 비워두거나 place_name을 활용
        latitude: parseFloat(place.y), // 위도
        longitude: parseFloat(place.x), // 경도
        address: place.address_name, // 전체 도로명 주소
        phone: place.phone // 전화번호 (있는 경우)
    }));

    if (bankLocations.value.length === 0) {
        console.warn("검색 결과가 없습니다.");
    } else {
        displayMarkers(window.kakao); // 검색 결과로 마커 표시
        // 첫 번째 검색 결과로 지도 중심 이동 (선택 사항)
        const bounds = new window.kakao.maps.LatLngBounds();
        bankLocations.value.forEach(loc => {
            bounds.extend(new window.kakao.maps.LatLng(loc.latitude, loc.longitude));
        });
        if (kakaoMapInstance) {
            kakaoMapInstance.setBounds(bounds);
        }
    }
  } else if (status === kakao.maps.services.Status.ZERO_RESULT) {
    console.warn('검색 결과가 존재하지 않습니다.');
    bankLocations.value = []; // 검색 결과 없음
  } else if (status === kakao.maps.services.Status.ERROR) {
    console.error('장소 검색 중 오류 발생:', status);
    error.value = '장소 검색 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
    bankLocations.value = [];
  }
  loading.value = false;
};

// 은행 검색 실행 함수 (카카오 API 직접 호출)
const searchBanks = () => {
  if (!searchQuery.value.trim()) {
    alert('검색어를 입력해주세요.');
    return;
  }
  if (!placesService) {
    error.value = 'Kakao Places Service가 초기화되지 않았습니다. 페이지를 새로고침 해주세요.';
    console.error('Places Service is not initialized.');
    return;
  }

  console.log(`'${searchQuery.value}' 키워드로 은행 검색 실행`);
  loading.value = true;
  error.value = null;
  searchAttempted.value = false; // 검색 시도 상태 초기화
  clearMarkers(); // 이전 마커 제거
  bankLocations.value = []; // 이전 검색 결과 초기화


  // 카테고리 코드 'BK9' (은행)을 사용하거나, 키워드에 "은행"을 포함하여 검색 정확도 향상 가능
  placesService.keywordSearch(searchQuery.value, placesSearchCB, {
    category_group_code: 'BK9', // 은행 카테고리 그룹 코드
    // location: kakaoMapInstance.getCenter(), // 현재 지도 중심 기준으로 검색하고 싶다면
    // radius: 10000 // 반경 (미터 단위, location과 함께 사용)
  });
};


const displayMarkers = (kakao) => {
  if (!kakaoMapInstance) {
    console.warn("지도 객체가 없어 마커를 표시할 수 없습니다.");
    return;
  }
  clearMarkers(); // 함수 호출 시 기존 마커들 제거

  if (!bankLocations.value || bankLocations.value.length === 0) {
    console.warn("은행 위치 데이터가 없어 마커를 표시할 수 없습니다.");
    return;
  }

  console.log(`displayMarkers: ${bankLocations.value.length}개의 마커 표시 시도.`);
  const bounds = new kakao.maps.LatLngBounds();

  bankLocations.value.forEach((location) => {
    if (location.latitude != null && location.longitude != null) {
      const markerPosition = new kakao.maps.LatLng(location.latitude, location.longitude);
      const marker = new kakao.maps.Marker({
        map: kakaoMapInstance,
        position: markerPosition,
        title: location.bank_name // 카카오 API의 place_name 사용
      });
      markers.push(marker); // 새로 생성된 마커를 배열에 추가

      const iwContent = `
        <div style="padding:5px;min-width:150px;font-size:0.9em;">
          <strong>${location.bank_name}</strong><br>
          ${location.address || ''}<br>
          ${location.phone ? `전화: ${location.phone}<br>` : ''}
          <a href="https://map.kakao.com/link/to/${encodeURIComponent(location.bank_name)},${location.latitude},${location.longitude}" style="color:blue" target="_blank">길찾기</a>
        </div>`;
      const infowindow = new kakao.maps.InfoWindow({
        content: iwContent,
        removable: true
      });

      kakao.maps.event.addListener(marker, 'click', function() {
        infowindow.open(kakaoMapInstance, marker);
      });
      bounds.extend(markerPosition);
    } else {
      console.warn(`위치 정보 누락 또는 부정확:`, location);
    }
  });

  if (markers.length > 0) {
    kakaoMapInstance.setBounds(bounds); // 모든 마커가 보이도록 지도 범위 조정
  }
  console.log("모든 마커 처리 완료.");
};


// 이 함수는 이제 직접 사용되지 않거나, 초기 기본 데이터를 DB에서 가져올 때만 사용
// const fetchBankLocations = async (kakaoInstance) => {
//   // 기존 DB에서 모든 은행 정보를 가져오는 로직은 주석 처리 또는 삭제
//   // console.log("fetchBankLocations 함수 호출됨 (기존 방식 - 자체 DB)");
//   // error.value = null;
//   // try {
//   //   const response = await axios.get(`${API_BASE_URL}/bank-locations/`); // Django API 호출
//   //   bankLocations.value = response.data.results || response.data;
//   //
//   //   if (!bankLocations.value || bankLocations.value.length === 0) {
//   //     console.warn("은행 위치 데이터를 가져왔으나 비어있습니다 (자체 DB).");
//   //   } else {
//   //     console.log(`${bankLocations.value.length}개의 은행 위치 데이터 수신됨 (자체 DB).`);
//   //     displayMarkers(kakaoInstance);
//   //   }
//   // } catch (err) {
//   //   console.error('은행 위치 데이터 조회 실패 (자체 DB):', err);
//   //   error.value = `은행 정보를 가져오는 데 실패했습니다: ${err.response?.data?.detail || err.message || '알 수 없는 오류'}`;
//   // } finally {
//   //   loading.value = false;
//   //   console.log("fetchBankLocations (자체 DB) 완료, loading:", loading.value);
//   // }
// };

onMounted(async () => {
  loading.value = true;
  error.value = null;
  mapContainer.value = document.getElementById('map');

  if (!mapContainer.value) {
    error.value = "지도를 표시할 HTML 요소(id='map')를 찾을 수 없습니다.";
    loading.value = false;
    console.error(error.value);
    return;
  }

  try {
    const kakao = await loadKakaoMapSDK();
    console.log('loadKakaoMapSDK 완료. 지도 초기화를 진행합니다.');
    if (initializeMap(kakao)) {
      // 페이지 로드 시 기본 검색어나, 사용자 위치 기반 주변 은행 검색 등을 수행할 수 있습니다.
      // 예: 사용자의 현재 위치를 얻어와서 그 주변의 "은행"을 카카오 API로 검색
      // 또는 `fetchBankLocations`를 호출하여 자체 DB의 기본 목록을 보여줄 수도 있습니다. (선택)
      // 현재는 검색 버튼을 통해 검색하도록 되어 있으므로, onMounted에서 자동 검색은 제외합니다.
      // await fetchBankLocations(kakao); // 이 부분은 이제 searchBanks 함수를 통해 실행됩니다.
    }
  } catch (err) {
    error.value = err.message;
    loading.value = false;
    console.error("BankLocationsView 마운트 중 오류:", err);
  } finally {
    loading.value = false; // onMounted 작업 완료 후 로딩 상태 해제
  }
});

onUnmounted(() => {
  // kakaoMapInstance는 전역 변수처럼 사용되므로 명시적으로 null 처리할 필요는 없을 수 있으나,
  // Vue의 반응성 시스템 밖에서 관리되는 객체이므로 정리해주는 것이 좋습니다.
  // 실제로는 지도 객체 자체를 파괴하는 API가 있다면 그것을 사용하는 것이 더 확실합니다.
  // (카카오맵 API 문서에서 Map 객체 제거/파괴 관련 내용을 확인해보세요.)
  kakaoMapInstance = null;
  console.log("BankLocationsView 언마운트됨, 지도 객체 참조 해제 시도.");
});

</script>

<style scoped>
.bank-locations-view {
  padding: 20px;
  text-align: center;
}
.search-bar {
  margin-bottom: 20px;
}
.search-bar input[type="text"] {
  padding: 8px;
  margin-right: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.search-bar button {
  padding: 8px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.search-bar button:hover {
  background-color: #0056b3;
}
#map {
  width: 100%;
  max-width: 800px; /* 필요에 따라 조정 */
  height: 500px;
  margin: 20px auto;
  border: 1px solid #ccc;
}
.alert {
  max-width: 800px; /* 필요에 따라 조정 */
  margin-left: auto;
  margin-right: auto;
}
</style>