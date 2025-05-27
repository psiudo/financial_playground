<template>
  <div>
    <h1>{{ symbol }} 가격 이력</h1>
    <input v-model="from" type="date" />
    <input v-model="to"   type="date" />
    <button @click="fetchHistory">조회</button>
    <ul>
      <li v-for="h in history" :key="h.date">
        {{ h.date }} : {{ h.price }}
      </li>
    </ul>
  </div>
</template>

<script>
import api from '@/utils/api'

export default {
  name: 'CommodityHistoryView',
  data() {
    return {
      symbol: this.$route.params.symbol,
      from: '',
      to: '',
      history: [],
    }
  },
  methods: {
    async fetchHistory() {
      try {
        const res = await api.get(
          `/commodities/${this.symbol}/history/`,
          { params: { from: this.from, to: this.to } }
        )
        this.history = res.data
      } catch (e) {
        console.error(e)
      }
    },
  },
  created() {
    this.fetchHistory()
  },
}
</script>
