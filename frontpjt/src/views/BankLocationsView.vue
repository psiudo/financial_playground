<template>
  <div class="bank-locations-view">
    <h1>내 주변 은행 찾기</h1>
    <div id="map" style="width:100%;height:500px;"></div>
    <div v_if="error" class="alert alert-danger mt-3" role="alert">
      <p class="mb-0">오류: {{ error }}</p>
    </div>
    <div v-if="loading && !error" class="d-flex justify-content-center mt-3">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="ms-2 mb-0">지도 및 은행 정보를 불러오는 중...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

const mapContainer = ref(null);
const bankLocations = ref([]);
const loading = ref(true);
const error = ref(null);
let kakaoMapInstance = null;

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';
const KAKAO_JS_KEY = import.meta.env.VITE_KAKAO_MAP_JS_KEY;

// Kakao SDK 스크립트를 동적으로 로드하고 API 준비를 확인하는 함수
function loadKakaoMapSDK() {
  return new Promise((resolve, reject) => {
    if (!KAKAO_JS_KEY) {
      const keyErrorMsg = "VITE_KAKAOMAP_JS_KEY가 .env 파일에 정의되지 않았습니다. 키를 설정해주세요.";
      console.error(keyErrorMsg);
      reject(new Error(keyErrorMsg));
      return;
    }

    // 이미 SDK가 로드되어 있는지 확인 (다른 컴포넌트 등에서 로드했을 경우)
    if (window.kakao && window.kakao.maps) {
      console.log('Kakao SDK (maps)가 이미 로드되어 있습니다.');
      // 이미 로드된 경우, 바로 kakao.maps.load()를 사용할 수 있도록 kakao 객체를 resolve
      // Kakao.init은 JS SDK의 다른 기능 사용 시 필요. 지도 API 키는 script URL의 appkey로 전달됨.
      if (window.Kakao && !window.Kakao.isInitialized()) {
        try {
          window.Kakao.init(KAKAO_JS_KEY);
          console.log('기존 Kakao SDK (JS Key) 초기화 시도 - loadKakaoMapSDK');
        } catch (e) {
          console.warn("기존 Kakao SDK 초기화 중 오류 (무시 가능): " + e.message);
        }
      }
      // kakao.maps.load를 호출할 수 있도록 window.kakao를 resolve
      kakao.maps.load(() => {
        console.log('이미 로드된 maps API 사용 준비 완료 (kakao.maps.load 콜백).');
        resolve(window.kakao);
      });
      return;
    }

    // SDK 스크립트가 로드 중인지 확인 (중복 생성 방지)
    if (document.querySelector(`script[src*="//dapi.kakao.com/v2/maps/sdk.js"]`)) {
      console.log('Kakao SDK 스크립트가 이미 문서에 삽입되어 로드 중입니다. 완료될 때까지 대기합니다.');
      // 이미 삽입된 스크립트의 로드를 기다리는 로직 (이전 ensureKakaoMapsApiReady와 유사)
      let attempts = 0;
      const intervalId = setInterval(() => {
        attempts++;
        if (typeof window.kakao !== "undefined" && typeof window.kakao.maps !== "undefined") {
          clearInterval(intervalId);
          console.log('기존 삽입된 Kakao SDK 및 Maps API 로드 확인됨.');
          if (window.Kakao && !window.Kakao.isInitialized() && KAKAO_JS_KEY) {
             try {
              window.Kakao.init(KAKAO_JS_KEY);
              console.log('기존 삽입된 Kakao SDK (JS Key) 초기화됨 - loadKakaoMapSDK.');
             } catch(e) {
               console.warn("기존 삽입된 Kakao SDK 초기화 중 오류 (지도 기능에는 영향 없을 수 있음): " + e.message);
             }
          }
          kakao.maps.load(() => { // maps API 로드 완료 후 resolve
            console.log('기존 삽입된 maps API 사용 준비 완료 (kakao.maps.load 콜백).');
            resolve(window.kakao);
          });
        } else if (attempts >= 100) { // 약 10초 대기
          clearInterval(intervalId);
          const waitErrorMsg = "기존 삽입된 Kakao SDK (window.kakao.maps)를 시간 내에 로드하지 못했습니다.";
          console.error(waitErrorMsg, "현재 window.kakao:", window.kakao);
          reject(new Error(waitErrorMsg));
        }
      }, 100);
      return;
    }
    
    console.log('Kakao SDK 스크립트를 동적으로 로드합니다.');
    const script = document.createElement('script');
    script.type = 'text/javascript';
    // autoload=false는 중요합니다. kakao.maps.load()를 수동으로 호출할 것이기 때문입니다.
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${KAKAO_JS_KEY}&libraries=services&autoload=false`;
    script.async = true;

    script.onload = () => {
      console.log('Kakao SDK 스크립트 동적 로드 완료.');
      if (typeof window.kakao !== "undefined" && typeof window.kakao.maps !== "undefined") {
        // Kakao.init은 JS SDK의 다른 기능을 사용할 때 필요. 지도 API 키는 이미 script URL의 appkey로 전달됨.
        if (window.Kakao && !window.Kakao.isInitialized()) {
           try {
            window.Kakao.init(KAKAO_JS_KEY);
            console.log('동적 로드된 Kakao SDK (JS Key) 초기화됨 - loadKakaoMapSDK.');
           } catch(e) {
             console.warn("동적 로드된 Kakao SDK 초기화 중 오류 (지도 기능에는 영향 없을 수 있음): " + e.message);
           }
        }
        // kakao.maps.load를 사용하여 지도 관련 API가 완전히 로드된 후에 resolve
        window.kakao.maps.load(() => {
          console.log('동적 로드된 maps API 사용 준비 완료 (kakao.maps.load 콜백).');
          resolve(window.kakao);
        });
      } else {
        const loadErrorMsg = "Kakao SDK는 로드되었으나, window.kakao.maps 객체를 찾을 수 없습니다.";
        console.error(loadErrorMsg);
        reject(new Error(loadErrorMsg));
      }
    };

    script.onerror = (event) => {
      const scriptErrorMsg = "Kakao SDK 스크립트를 동적으로 로드하는 데 실패했습니다. 네트워크 연결 및 스크립트 URL을 확인하세요.";
      console.error(scriptErrorMsg, event);
      reject(new Error(scriptErrorMsg));
    };

    document.head.appendChild(script);
  });
}

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
    // kakao.maps.load() 콜백이 이미 resolve(window.kakao)를 처리하므로,
    // loadKakaoMapSDK()는 이미 maps API가 준비된 kakao 객체를 반환합니다.
    const kakao = await loadKakaoMapSDK(); 
    
    // loadKakaoMapSDK 내부에서 kakao.maps.load가 이미 호출되었으므로, 여기서 바로 지도 초기화
    console.log('loadKakaoMapSDK 완료. 지도 초기화를 진행합니다.');
    if (initializeMap(kakao)) {
      await fetchBankLocations(kakao);
    }

  } catch (err) {
    error.value = err.message; // loadKakaoMapSDK에서 발생한 오류
    loading.value = false;
    console.error("BankLocationsView 마운트 중 오류:", err);
  }
});

// initializeMap, fetchBankLocations, displayMarkers, onUnmounted 함수는 이전과 동일하게 유지
const initializeMap = (kakaoInstance) => {
  console.log("initializeMap 함수 호출됨");
  if (!mapContainer.value) { 
      error.value = "지도 컨테이너(id='map')를 찾을 수 없습니다 (initializeMap 내부).";
      loading.value = false;
      console.error(error.value);
      return false;
  }
  const options = {
    center: new kakaoInstance.maps.LatLng(37.566826, 126.9786567),
    level: 5
  };
  try {
    kakaoMapInstance = new kakaoInstance.maps.Map(mapContainer.value, options);
    console.log("카카오 지도 객체 생성됨:", kakaoMapInstance);
  } catch (e) {
    error.value = "지도 객체 생성 중 오류 발생: " + e.message;
    loading.value = false;
    console.error(error.value, e);
    return false;
  }

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        const userPosition = new kakaoInstance.maps.LatLng(lat, lng);
        if (kakaoMapInstance) {
          kakaoMapInstance.setCenter(userPosition);
          new kakaoInstance.maps.Marker({
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
};

const fetchBankLocations = async (kakaoInstance) => {
  console.log("fetchBankLocations 함수 호출됨");
  error.value = null;
  try {
    const response = await axios.get(`${API_BASE_URL}/bank-locations/`);
    bankLocations.value = response.data.results || response.data; 
    
    if (!bankLocations.value || bankLocations.value.length === 0) {
      console.warn("은행 위치 데이터를 가져왔으나 비어있습니다.");
    } else {
      console.log(`${bankLocations.value.length}개의 은행 위치 데이터 수신됨.`);
      displayMarkers(kakaoInstance);
    }
  } catch (err) {
    console.error('은행 위치 데이터 조회 실패:', err);
    error.value = `은행 정보를 가져오는 데 실패했습니다: ${err.response?.data?.detail || err.message || '알 수 없는 오류'}`;
  } finally {
    loading.value = false;
    console.log("fetchBankLocations 완료, loading:", loading.value);
  }
};

const displayMarkers = (kakaoInstance) => {
  if (!kakaoMapInstance || !bankLocations.value || bankLocations.value.length === 0) {
    console.warn("지도 객체 또는 은행 위치 데이터가 없어 마커를 표시할 수 없습니다.");
    return;
  }
  console.log(`displayMarkers: ${bankLocations.value.length}개의 마커 표시 시도.`);

  bankLocations.value.forEach((location, index) => {
    if (location.latitude != null && location.longitude != null) {
      const markerPosition = new kakaoInstance.maps.LatLng(location.latitude, location.longitude);
      const marker = new kakaoInstance.maps.Marker({
        map: kakaoMapInstance,
        position: markerPosition,
        title: `${location.bank_name || location.bank || '은행'} ${location.branch_name || ''}`
      });

      const iwContent = `<div style="padding:5px;min-width:150px;font-size:0.9em;"><strong>${location.bank_name || location.bank || '은행'} ${location.branch_name || ''}</strong><br>${location.address || ''}<br><a href="https://map.kakao.com/link/to/${encodeURIComponent((location.bank_name || location.bank || '은행') + ' ' + (location.branch_name || ''))},${location.latitude},${location.longitude}" style="color:blue" target="_blank">길찾기</a></div>`;
      const infowindow = new kakaoInstance.maps.InfoWindow({
        content: iwContent,
        removable: true
      });

      kakaoInstance.maps.event.addListener(marker, 'click', function() {
        infowindow.open(kakaoMapInstance, marker);
      });
    } else {
      console.warn(`위치 정보 누락 또는 부정확 (index ${index}):`, location);
    }
  });
  console.log("모든 마커 처리 완료.");
};

onUnmounted(() => {
  if (kakaoMapInstance) {
    kakaoMapInstance = null;
  }
  // 동적으로 추가된 스크립트 제거 (선택적: 다른 곳에서 사용하지 않는다면)
  // const script = document.querySelector(`script[src*="//dapi.kakao.com/v2/maps/sdk.js"]`);
  // if (script) {
  //   script.remove();
  //   console.log('Kakao SDK 스크립트 동적 제거됨.');
  // }
  console.log("BankLocationsView 언마운트됨.");
});

</script>

<style scoped>
.bank-locations-view {
  padding: 20px;
  text-align: center;
}
#map {
  width: 100%;
  max-width: 800px;
  height: 500px;
  margin: 20px auto;
  border: 1px solid #ccc;
}
.alert {
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}
</style>