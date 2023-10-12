<template>
<div>
        <form class="form-signin" @submit.prevent = "handleSubmit">

          <h1 class="h3 mb-3 font-weight-normal">Are you sure you want to delete {{venue.name}}?</h1>
          <ul>
            
            <li>Name: {{ venue.name }}</li>
            <li>Address: {{ venue.address }}</li>
            <li>City: {{ venue.city }}</li>
            <li>State: {{ venue.state }}</li>
            <li>Country: {{ venue.country }}</li>
            <li>Capacity: {{ venue.capacity }}</li>
            <li>Phone: {{ venue.phone }}</li>
            <li>Email: {{ venue.email }}</li>

        </ul>
          <template v-if="moviesforvenue.length > 0">
        <p>Deleting this venue will also delete the following movies. Are you sure you want to proceed?</p>
        <ul>
          <li v-for="movie in moviesforvenue" :key="movie.id">{{ movie.title }}</li>
        </ul>
      </template>
            <template v-if="flag">
        <p>All the bookings associated with it will also be deleted. Are you sure you want to proceed?</p>
      </template>
          <input type="submit" value="Delete">
        </form>
      </div>
</template>

<script>
export default {
props:['venue_id', 'movie_id'] ,
data() {
    return {
      flag:false,
      venue: {
        name: "",
        address: "",
        city: "",
        state: "",
        country: "",
        capacity: 0,
        phone: "",
        email: ""
      },
      moviesforvenue:[]
    };
  },
    created() {
    this.fetchMoviesforVenue();
    this.fetchvenue();
  },
  methods: {
    fetchvenue: async function(){
          const venueId = this.$route.params.venue_id;
    if (venueId !== "0") {
        console.log(venueId)
      // Fetch venue data from the API using the venue_id
      await fetch(`http://127.0.0.1:5000/api/edit/${venueId}`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`
        },
        mode: "cors"
      })
        .then((response) => response.json())
        .then((data) => {
          // Set the venue data with the fetched data
          this.$set(this, 'venue', data);
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }

    },
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
    },
    handleSubmit() {
      const venueId = this.$route.params.venue_id;
      const apiUrl = venueId !== "0" ? `/edit/${venueId}` : "/add_new_venue";
console.log("venueId:", venueId);
console.log("access_token:", localStorage.getItem("access_token"));
      // Handle form submission for updating or adding a venue
      fetch(`http://127.0.0.1:5000/api/vuedeletevenue/${venueId}`, {
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
            
              this.$router.push({ name: "admin_dashboard" });
           
            
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