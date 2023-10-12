<template>
  <div :key="componentKey">
  <div class="d-flex justify-content-end">
    How would you like to recieve monthly reports?
    <select  v-model="reportoption">
                  <option value="HTML">HTML</option>
                  <option value="PDF">PDF</option>
                </select>
    <button v-on:click="reportoptionhandler">Save</button>
  </div>

    <h1 v-if="query">Search results for "{{ query }}" in "{{ category }}" category:</h1>
    
              
              <div class="input-group">
                <input  v-model="query">
                <div >
                <select  v-model="category">
                  <option value="venue">Venue</option>
                  <option value="movie">Movie</option>
                </select>
              <button  v-on:click='fetchUserDashboardData' >Search</button>
            </div>
          </div>
            
    <div v-if="category === 'venue'">
      <div v-for="venue in venues" :key="venue.venue_id" class="card">
        <div class="card-header"></div>
        <div class="card-body">
            <router-link :to="`/vuevenuedetails/${user_id}/${venue.venue_id}`">
            <h5 class="card-title">{{ venue.name }}</h5>
          </router-link>
          <p class="card-text">Shows:</p>
          <div v-if="movies_by_venue[venue.venue_id]">
            <div v-for="movieObject in movies_by_venue[venue.venue_id]" :key="movieObject.movie_id" class="card w-50">
              <div class="card-body">
                <h5 class="card-title">{{ movieObject.title }}</h5>
                <h5>Showtime: {{ movieObject.time }}</h5>
                <p>Price of ticket: {{ movieObject.price }}</p>
                <p>Number of seats available: {{ movieObject.seats_available }}</p>
                <p class="card-text">{{ movieObject.synopsis }}</p>
                <router-link :to="`/vuebook/${user_id}/${venue.venue_id}/${movieObject.movie_id}`" class="btn btn-primary">Book</router-link> 
              </div>
            </div>
          </div>
          <p v-else>No movies found</p>
        </div>
      </div>
    </div>
    <div v-else-if="category === 'movie'">
      <div v-for="movieItem in movies" :key="movieItem.movie_id" class="card">
        <div class="card-body">
          <h5 class="card-title">{{ movieItem.movie.title }}</h5>
        
          <p class="card-text">{{ movieItem.movie.description }}</p>
          <p class="card-text">Showtimes:</p>
          <ul class="list-unstyled">
            <li v-for="venue in movieItem.venues" :key="venue.venue_id">
              {{ venue.name }} - {{ venue.address }}
              <router-link :to="`/vuebook/${user_id}/${venue.venue_id}/${movieItem.movie.movie_id}`" class="btn btn-primary">Book</router-link> 
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>



<script>
export default {
  data() {
    return {
      query: '',
      category: 'venue',
      venues: [],
      movies_by_venue: {},
      movies:[],
      reportoption:"",
      componentKey: 0
    };
  },

  methods: {
      fetchUserDashboardData: async function() {

  console.log(this.category)
  console.log(this.query)
    console.log(this.user_id)
    if (this.category =='venue'){
    if (this.query.trim() === ''){
      
      try {
        console.log(`http://127.0.0.1:5000/api/vueuserdashboard/${this.user_id}/${this.category}`)
      const response = await fetch(`http://127.0.0.1:5000/api/vueuserdashboard/${this.user_id}/${this.category}`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      },
      mode: 'cors'
    });

    if (!response.ok) {
      throw new Error('Failed to fetch user dashboard data');
    }

    const data = await response.json();

        // this.$set(this, 'category', data.category);
        // this.$set(this, 'query', data.category);
        this.$set(this, 'venues', data.venues_data);
        this.$set(this, 'movies_by_venue', data.movies_by_venue);

      
  } catch (error) {
    console.error('Error fetching user dashboard data:', error);
  }
}else {
          const selectedCategory = this.category;
      const searchQuery = this.query;
  console.log(`http://127.0.0.1:5000/api/searchbyuser/${this.user_id}/${this.category}/${this.query}`)
  try{
    const response = await fetch(`http://127.0.0.1:5000/api/searchbyuser/${this.user_id}/${this.category}/${this.query}`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      },
      mode: 'cors'
    });

    if (!response.ok) {
      throw new Error('Failed to fetch user dashboard data');
    }

    const data = await response.json();

       
        this.$set(this, 'venues', data.venues_data);
        this.$set(this, 'movies_by_venue', data.movies_by_venue);

  } catch (error) {
    console.error('Error fetching user dashboard data:', error);
  }

}}
    else if (this.category == 'movie'){
              const selectedCategory = this.category;
      const searchQuery = this.query;
      console.log(`http://127.0.0.1:5000/api/searchbyuser/${this.user_id}/${this.category}/${this.query}`)
      try{
    const response = await fetch(`http://127.0.0.1:5000/api/searchbyuser/${this.user_id}/${this.category}/${this.query}`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      },
      mode: 'cors'
    });
console.log(response)
    if (!response.ok) {
      throw new Error('Failed to fetch user dashboard data');
    }

    const data = await response.json();

        
        this.$set(this, 'movies', data.movies);
        this.$set(this, 'venues',[]);
        this.$set(this, 'movies_by_venue',{});
        // this.$set(this, 'category', data.category);
        // this.$set(this, 'query', data.category);
  } catch (error) {
    console.error('Error fetching user dashboard data:', error);
  }
}
 },
 reportoptionhandler: async function() {
      try{
    const response = await fetch(`http://127.0.0.1:5000/api/reportoptionhandler/${this.user_id}/${this.reportoption}`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      },
      mode: 'cors'
    });
  console.log(response)
    if (!response.ok) {
          throw new Error("Network response was not ok.");
        }

        const data = await response.json();
          confirm(data.message)
        this.componentKey++;
      
        
      } catch (error) {
        console.error("Error ", error);
        // Handle the error or show an error message to the user
      }
 }
 },
  mounted() {
    // Fetch data when the component is mounted
    this.fetchUserDashboardData();
  },
computed: {
    user_id() {
      const jwtToken = localStorage.getItem("access_token");
      if (jwtToken) {
        const parts = jwtToken.split(".");
        
        // Decode the payload (second part of the token)
        const payload = atob(parts[1]);
        return JSON.parse(payload).user_id;
      }
      return null;
    }
  
  }
}
</script>

<style scoped>

</style>