
<template>
<div id="app">
   <myheader :key="headerKey" ></myheader>

  </div>
</template>


<script>
import header from "./components/header";
export default {
  name: "App",
  components: {
    'myheader': header
  },
  data() {
    return {
      headerKey: 0 // Initialize with a default value
    };
  },
  watch: {
    // Watch for changes in the route to trigger header component reload
    '$route'() {
      this.headerKey++; // Increment the headerKey to force reload the header component
    }
  }
};
</script>
<style>

</style>
