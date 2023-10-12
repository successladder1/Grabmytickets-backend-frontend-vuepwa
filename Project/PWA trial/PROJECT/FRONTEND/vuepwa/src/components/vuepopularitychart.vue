<template>
  <div>
    <div>
      <img :src="chart1Data" alt="Chart 1" />
    </div>
    <div>
      <img :src="chart2Data" alt="Chart 2" />
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      chart1Data: null,
      chart2Data: null,
    };
  },
  mounted() {
    this.getChartImages();
  },
  methods: {
    async getChartImages() {
      try {
        const response = await fetch("http://127.0.0.1:5000/api/vuegetpopularity" , {
          headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`
          
        }
        });
        const data = await response.json();
        this.$set(this,'chart1Data',`data:image/png;base64, ${data.chart1}` );
        this.$set(this,'chart2Data',`data:image/png;base64, ${data.chart2}` );
      } catch (error) {
        console.error("Error occurred while fetching chart images:", error);
      }
    },
  },
};
</script>
