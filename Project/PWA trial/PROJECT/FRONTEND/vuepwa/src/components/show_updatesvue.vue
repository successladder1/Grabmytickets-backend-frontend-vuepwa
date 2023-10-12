<template>
 <div>
    <ul>
    <li v-for="(message, index) in messages" :key="index"> {{ message }} </li>
        </ul>
 </div>
  
</template>

<script>
export default {
    data() {
    return {
      messages: []
    };
  },
  mounted(){
    var self = this;
    var source =new EventSource('http://127.0.0.1:5000/stream');
    source.addEventListener('greeting', function(event){
        console.log(event)
        let data=JSON.parse(event.data);
        self.messages.push(data.message);
    }, false);
  }

}
</script>

<style>

</style>