<template>
    <div class="commodities">
      <h1>기초자산 목록</h1>
      <table>
        <thead>
          <tr>
            <th>심볼</th>
            <th>이름</th>
            <th>최근가</th>
            <th>상세보기</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in list" :key="item.symbol">
            <td>{{ item.symbol }}</td>
            <td>{{ item.name }}</td>
            <td>{{ item.latest_price }}</td>
            <td>
              <RouterLink
                :to="{ name: 'CommodityHistory', params: { symbol: item.symbol } }"
              >
                내역 보기
              </RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { RouterLink } from 'vue-router'
  import api from '@/utils/api'
  
  const list = ref([])
  
  async function fetchList() {
    try {
      const res = await api.get('/commodities/list/')
      list.value = res.data
    } catch (err) {
      console.error('기초자산 목록 호출 실패', err)
    }
  }
  
  onMounted(fetchList)
  </script>
  
  <style scoped>
  .commodities {
    padding: 20px;
  }
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: center;
  }
  th {
    background-color: #f5f5f5;
  }
  </style>
  