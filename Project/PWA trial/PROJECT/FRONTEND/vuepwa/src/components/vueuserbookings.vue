<template>
  <div :key="componentKey">
    <h1>My current Bookings</h1>
    <ul v-if="bookings.length">
      <li v-for="booking in bookings" :key="booking.booking_id">
        Movie ID: {{ booking.movie_name }} | Venue ID: {{ booking.venue_name }} | Showtime: {{booking.time}} | {{booking.num_of_tickets}} | Price : {{booking.price}} | Date of booking : {{booking.create_date}} <button v-on:click="cancelbooking(booking.booking_id)"> Cancel Booking</button>
      </li>
    </ul>
    <p v-else>No bookings yet.</p>

    <h1>Past Bookings</h1>
    <ul v-if="past_bookings.length">
      <li v-for="past_booking in past_bookings" :key="past_booking.booking_id">
        Movie ID: {{ past_booking.movie_name }} | Venue ID: {{ past_booking.venue_name }} | Showtime: {{past_booking.showtime}} | {{past_booking.num_of_tickets}} | Price : {{past_booking.price}} | Date of booking : {{past_booking.create_date}} | SEEN
      </li>
    </ul>
    <p v-else>No bookings yet.</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      bookings: [],
      past_bookings: [],
       componentKey: 0
    };
  },
  mounted() {
    this.fetchBookings();
  },
  watch: {
    // Watch for changes to the componentKey
    componentKey: {
      handler() {
        // Fetch updated bookings after componentKey changes (i.e., after canceling a booking)
        this.fetchBookings();
      },
      immediate: true, // Fetch bookings immediately when the component is created
    },
  },
  methods: {
    async fetchBookings() {
      try {
        const response = await fetch(
          `http://127.0.0.1:5000/api/vuebook/${this.user_id}`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            },
            mode: "cors",
          }
        );

        if (!response.ok) {
          throw new Error("Network response was not ok.");
        }

        const data = await response.json();
        this.$set(this, 'bookings', data.present_bookings);
        this.$set(this, 'past_bookings', data.past_bookings);
      } catch (error) {
        console.error("Error fetching bookings:", error);
        // Handle the error or show an error message to the user
      }
    },
     cancelbooking: async function(booking_id){
try {
        const response = await fetch(
          `http://127.0.0.1:5000/api/vuebook/${this.user_id}/${booking_id}`,
          {
            method: "DELETE",
            headers: {
              Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            },
            mode: "cors",
          }
        );

        if (!response.ok) {
          throw new Error("Network response was not ok.");
        }

        const data = await response.json();
          
      this.componentKey++;
      
        
      } catch (error) {
        console.error("Error fetching bookings:", error);
        // Handle the error or show an error message to the user
      }
    }
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
};
</script>

<style>
/* Add your CSS styles here */
</style>
