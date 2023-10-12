<template>
<div>
   <div class="row gx-4 gx-lg-5 justify-content-center">
            <div class="col-md-10 col-lg-8 col-xl-7">
              
                <h3>Book tickets for the {{movievenue.title}} at {{movievenue.name}} {{movievenue.address}}</h3>
                <h5>Showtime: {{movievenue.time}}</h5>
                <h5>Seats available: {{movievenue.seats_available}}</h5>
                <form id="contactForm" @submit.prevent="addbooking">
                    <div class="form-floating">
                        <input class="form-control" id="num_of_tickets" type="number" placeholder="num_of_tickets" data-sb-validations="required" v-model="num_of_tickets" />
                        <label for="num_of_tickets">num_of_tickets</label>
                        <div class="invalid-feedback" data-sb-feedback="num_of_tickets:required">num_of_tickets is required.</div>
                    </div>
                    
                         <p v-if= "num_of_tickets">The total price is: Rs.{{ compprice }}</p>
                    
                    
                    
                    <br />
                    <div class="d-none" id="submitSuccessMessage">
                        <div class="text-center mb-3">
                            <div class="fw-bolder">Form submission successful!</div>
                            To activate this form, sign up at
                            <br />
                            <a href="https://startbootstrap.com/solution/contact-forms">https://startbootstrap.com/solution/contact-forms</a>
                        </div>
                    </div>
                    <div class="d-none" id="submitErrorMessage"><div class="text-center text-danger mb-3">Error sending message!</div></div>
                
            
                    <button class="btn btn-primary text-uppercase"  type="submit" name="proceed" value="clicked">Proceed to buy</button>
                    
</form>
            </div>
   </div>
</div>
</template>

<script>
export default {
  data() {
    return {
      movievenue:{},
      num_of_tickets:0,
      price:0
     
    };
  },
  mounted() {
    this.fetchvenuemovie();
   
  },
  methods: {
    async fetchvenuemovie() {
      try {
        const venueId = this.$route.params.venue_id;
          const movieId=this.$route.params.movie_id;
        const response = await fetch(
          `http://127.0.0.1:5000/api/getmovievenueuser/${this.user_id}/${venueId}/${movieId}`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${localStorage.getItem("access_token")}`
              
            },
            mode: "cors",
            body: JSON.stringify(this.movie)
          }
        );

        if (!response.ok) {
          throw new Error("Network response was not ok.");
        }

        const data = await response.json();
        console.log(data)
        this.$set(this, 'movievenue', data);
        this.$set(this, 'price', data.price);
        console.log(data)
      } catch (error) {
        console.error("Error fetching bookings:", error);
        // Handle the error or show an error message to the user
      }
    },
addbooking: async function(){
          const venueId = this.$route.params.venue_id;
          const movieId=this.$route.params.movie_id;
          if (Number(this.num_of_tickets) <=0){
            alert("Please enter valid number of tickets")
          }
          else if (Number(this.num_of_tickets>this.movievenue.seats_available)){
            alert("Not enough seats available")
          }
    else{
    if (movieId !== "0") {
        console.log(movieId)
      // Fetch venue data from the API using the venue_id
      const payload = {
        user_id: this.user_id,
        venue_id: venueId,
        movie_id: movieId,
        num_of_tickets: Number(this.num_of_tickets),
        // Add other necessary data here if needed
      };
      console.log(JSON.stringify(payload));
          try {
      const resp = await fetch(`http://127.0.0.1:5000/api/vuebook/${this.user_id}/${venueId}/${movieId}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          "Content-Type": "application/json",
        },
        mode: "cors",
        body: JSON.stringify(payload),
      });

      const data = await resp.json();
        console.log(data)
          if (data['message'] == "Please tell us the number of tickets you want to book."){
            alert(data['message'])
          }
          else if (data['message'] == "Not enough seats available"){
            alert(data['message'])
          }
          else {
          confirm(data['message'])
          this.$router.push({ name: "vueuserbookings" , params: {user_id :this.user_id}});
          }
        }
        catch(error) {
          console.error("Error:", error);
        };
    }
    }

    },
    calcprice: function(){
      return this.price * this.num_of_tickets
    }
},
  computed: {
    compprice(){return this.price*this.num_of_tickets},
    user_id() {
      const jwtToken = localStorage.getItem("access_token");
      if (jwtToken) {
        const parts = jwtToken.split(".");
        const payload = atob(parts[1]);
        return JSON.parse(payload).user_id;
      }
      return null;
    }
  }
};
</script>

<style>

</style>