<template>
  <div>
            <form class="form-signin" @submit.prevent="handleSubmit" >
          <h1 class="h3 mb-3 font-weight-normal">Are you sure you want to delete {{movie.title}} </h1>
          <ul>
            <li>Title: {{ movie.title }}</li>
            <li>Genre: {{ movie.genre }}</li>
            <li>Language: {{ movie.language }}</li>
            <li>Rating: {{ movie.rating }}</li>
            <li>Runtime: {{ movie.runtime }}</li>
            <li>Director: {{ movie.director }}</li>
            <li>Synopsis: {{ movie.synopsis }}</li>
            <li>Release date: {{ movie.release_date }}</li>
            <li>Price: {{ movie.price }}</li>
            <li>Release date: {{ movie.seats_available }}</li>
            <li>Release timing: {{ movie.time }}</li>

        </ul>

          <input type="submit" value="Delete">
        </form>
      </div>
</template>

<script>
export default {
props:['venue_id', 'movie_id'] ,
data() {
    return {
      movie: {
                "movie_id": "",
                "title": "",
                "genre": "",
                "language": "",
                "runtime": "",
                "rating": "",
                "director": "",
                "synopsis": "",
                "release_date": "",
                "trailer_url": "",
                "venue_id": "",
                "price": "",
                "date": "",
                "time": "",
                "create_date": "",
                "seats_available": 0
            }
    };
  },
    created() {
    this.fetchmovie();
  },
  methods: {
    fetchmovie: async function(){
          const venueId = this.$route.params.venue_id;
          const movieId=this.$route.params.movie_id;
    if (movieId !== "0") {
        console.log(movieId)
      // Fetch venue data from the API using the venue_id
      await fetch(`http://127.0.0.1:5000/api/edit_movie/${venueId}/${movieId}`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`
        },
        mode: "cors"
      })
        .then((response) => response.json())
        .then((data) => {
          // Set the venue data with the fetched data
          this.$set(this, 'movie', data);
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }

    },
    handleSubmit() {
      const venueId = this.$route.params.venue_id;
      const movieId=this.$route.params.movie_id;
console.log("venueId:", venueId);
console.log("movieId:", movieId);
console.log("access_token:", localStorage.getItem("access_token"));
      // Handle form submission for updating or adding a venue
      fetch(`http://127.0.0.1:5000/api/vuedeletemovie/${venueId}/${movieId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`
          
        },
        mode: "cors"
   
      })
        .then((response) => {
          if (response.ok) {
            // Handle successful form submission
            // Redirect to appropriate page after form submission
            
              this.$router.push({ name: "vuevenue_movie_dashboard" });
           
            
          } else {
            throw new Error("Error submitting form");
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }
  }
};
</script>



<style>

</style>
