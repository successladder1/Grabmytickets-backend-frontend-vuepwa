<template>
    <div>
          <h1> Welcome to GrabMyTickets </h1>
            <showupdatecomp> </showupdatecomp>
            <input v-model='webhookmessage'/>
            <button v-on:click="handlewebhook">Click me to test webhooks </button>
    </div>

</template>

<script>
import show_updatesvue from './show_updatesvue.vue'
export default {
    data(){
        return {
            webhookmessage:''
        }
    },
    components: {
        showupdatecomp :show_updatesvue
    },
    methods:{
        handlecelery: function(){
            fetch('http://127.0.0.1:5000/hello/yukti')
        .then((response) => response.json() )
        .then((data) => {
          // Handle the fetched data
          console.log(data)
          this.$set(this, 'dummy', data.result)
        })
        },
    handlewebhook:function(){
      let data={'text':this.webhookmessage}
      fetch('https://chat.googleapis.com/v1/spaces/AAAAh-UtaYA/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=eKOI5rVI5DgVyy4FI8vaBFUc9dGQNneZf27Zo3HczK8', {
        method: 'POST',
        headers: {
      'Content-Type': 'application/json' 
    },
        body:JSON.stringify(data)
      }).then(r=>r.json())
      .then(data=> console.log(data))
      .catch(error=>console.log(error))
    }
  },
};
</script>

<style scoped>

</style>
