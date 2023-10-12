<template>
  <div >
              
                <h1>Movies</h1>
              
                <router-link :to="{ name: 'vuemovieedit', params: { venue_id: venue_id, movie_id: 0 } }">Add a new movie</router-link>
                
                <table class="table1" text-align="center">
                    <thead>
                      <tr>
                        <th scope="col">SNo</th>
                        <th scope="col">Title</th>
                        <th scope="col">Genre</th>
                        <th scope="col">Language</th>
                        <th scope="col">Runtime</th>
                        <th scope="col">Rating</th>
                        <th scope="col">Director</th>
                        <th scope="col" width="600px" text-align="center">Synopsis</th>
                        <th scope="col">Release date</th>
                        <th scope="col">Trailer URL</th>
                        <th scope="col">Price</th>
                        <th scope="col">Date</th>
                        <th scope="col">Time</th>
                        <th scope="col">Seats Available</th>
                        <th scope="col">Edit</th>
                        <th scope="col">Delete</th>
                      </tr>
                    </thead>
                    <tbody>
                        


                      <tr v-for="(movie_venue_obj, index) in moviesforvenue" :key="index">
                        
                        <td>{{movie_venue_obj.movie_id}}</td>
                        <td>{{movie_venue_obj.title}}</td>
                        <td>{{movie_venue_obj.genre}}</td>
                        <td>{{movie_venue_obj.language}}</td>
                        <td>{{movie_venue_obj.runtime}}</td>
                        <td>{{movie_venue_obj.rating}}</td>
                        <td>{{movie_venue_obj.director}}</td>
                        <td style="width: 600px">{{movie_venue_obj.synopsis}}</td>
                        <td>{{movie_venue_obj.release_date}}</td>
                        <td>{{movie_venue_obj.trailer_url}}</td>
                        <td>{{movie_venue_obj.price}}</td>
                        <td>{{movie_venue_obj.date}}</td>
                        <td>{{movie_venue_obj.time}}</td>
                        <td>{{movie_venue_obj.seats_available}}</td>
                        <td><router-link :to="{name: 'vuemovieedit', params:{venue_id: movie_venue_obj.venue_id, movie_id:movie_venue_obj.movie_id}}">Edit</router-link></td>
                        <td><router-link :to="{name: 'vuemoviedelete', params:{venue_id: movie_venue_obj.venue_id, movie_id:movie_venue_obj.movie_id}}">Delete</router-link></td>
                      </tr>
                    
                    </tbody>
                  </table>

                

        
            </div>
</template>

<script>
export default {
  delimiters: ['${','}'],
  props:['venue_id'] ,
  data() {
    return {
      moviesforvenue:[]
    }
  },
  created() {
    this.fetchMoviesforVenue();
  },
  methods: {
    fetchMoviesforVenue() {
      console.log('Fetching Movies...');
      fetch(`http://127.0.0.1:5000/api/vuevenue_movie_dashboard/${this.venue_id}`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        },
        mode :'cors'
      })
        .then((response) => response.json() )
        .then((data) => {
          // Handle the fetched data
          console.log(data)
          this.$set(this, 'moviesforvenue', data.movie_venue_data);
          console.log(this.moviesforvenue)
        })
        .catch((error) => {
          console.error('Error:', error);
        });
    }
  }
};
</script>


<style>

</style>