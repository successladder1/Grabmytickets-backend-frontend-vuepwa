<template>
  <div>
        
            <h5 >{{ venue.name }}</h5>
            <p>Address : {{ venue.address }}</p>
            <p>City : {{ venue.city }}</p>
            <p>State : {{ venue.state }}</p>
            <p>Country : {{ venue.country }}</p>
            <p>Capacity : {{ venue.capacity }}</p>
            <p>Phone : {{ venue.phone }}</p>
            <p>Email : {{ venue.email }}</p>
          <p class="card-text">Shows:</p>
          
<template v-if="movies.length">
      <div v-for="(movie, index) in movies" :key="index" class="card w-50">
        <div class="card-body">
          <h5 class="card-title">{{ movie.title }}</h5>
          <h5>Release date : {{ movie.release_date }}</h5>
          <h5>Showtime : {{ movie.time }}</h5>
          <h5>Genre : {{ movie.genre }}</h5>
          <h5>Runtime : {{ movie.runtime }}</h5>
          <p>Language : {{ movie.language }}</p>
          <p>Rating : {{ movie.rating }}</p>
          <p>Price of ticket : {{ movie.price }}</p>
          <p>Number of seats available : {{ movie.seats_available }}</p>
          <p class="card-text">{{ movie.synopsis }}</p>
          <p>Director: {{ movie.director }}</p>
          <router-link :to="`/vuebook/${user_id}/${venue.venue_id}/${movie.movie_id}`" class="btn btn-primary">Book</router-link> 
        </div>
      </div>
    </template>
    <p v-else>No movies found</p>
  </div>

</template>

<script>
export default {
    data (){
        return {
            venue:{},
            movies :[]
        }
    },
    methods:{
        fetchmovieforvenue: async function(){
            const venueId = this.$route.params.venue_id;
        try{
            const venueId = this.$route.params.venue_id;
        const response = await fetch(`http://127.0.0.1:5000/api/getvenuedetails/${this.user_id}/${venueId}`, {
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

        
        this.$set(this, 'venue', data.venue);
        this.$set(this, 'movies', data.movies);

        }catch (error) {
    console.error('Error fetching user dashboard data:', error);
  }
    }
    },
    mounted(){
        this.fetchmovieforvenue();
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

<style>

</style>