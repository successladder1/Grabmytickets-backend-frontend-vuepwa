<template>
<div>
      <div class="row gx-4 gx-lg-5 justify-content-center">
        <div class="col-md-10 col-lg-8 col-xl-7">
            <form id="contactForm" @submit.prevent="handleSubmit" >
                <div class="form-floating" >
                    <input class="form-control" id="name" type="text" placeholder="Name" data-sb-validations="required" v-model="venue.name" required/>
                    <label for="name">Name</label>
                    <div class="invalid-feedback" data-sb-feedback="name:required">A name is required.</div>
                </div>
                <div class="form-floating">
                    <input class="form-control" id="address" type="text" placeholder="Address" data-sb-validations="required"  v-model="venue.address" required/>
                    <label for="address">Address</label>
                    <div class="invalid-feedback" data-sb-feedback="address:required">An address is required.</div>
                </div>
                <div class="form-floating">
                    <input class="form-control" id="city" type="text" placeholder="city" data-sb-validations="required"  v-model="venue.city" required/>
                    <label for="city">city</label>
                    <div class="invalid-feedback" data-sb-feedback="city:required">A city is required.</div>
                </div>
                <div class="form-floating">
                    <input class="form-control" id="state" type="text" placeholder="state" data-sb-validations="required"  v-model="venue.state" required/>
                    <label for="state">state</label>
                    <div class="invalid-feedback" data-sb-feedback="state:required">state is required.</div>
                </div>
                <div class="form-floating">
                    <input class="form-control" id="country" type="text" placeholder="country" data-sb-validations="required"  v-model="venue.country" required/>
                    <label for="country">country</label>
                    <div class="invalid-feedback" data-sb-feedback="country:required">country is required.</div>
                </div>
                <div class="form-floating">
                    <input class="form-control" id="capacity" type="number" placeholder="capacity" data-sb-validations="required"  v-model="venue.capacity" required min="0" />
                    <label for="capacity">capacity</label>
                    <div class="invalid-feedback" data-sb-feedback="capacity:required">capacity required.</div>
                </div>
                <div class="form-floating">
                    <input class="form-control" id="phone" type="text" pattern="[0-9]{10}" placeholder="phone" data-sb-validations="required" v-model="venue.phone" required/>
                    <label for="phone">phone</label>
                    <div class="invalid-feedback" data-sb-feedback="phone:required">phone required.</div>
                </div>
                <div class="form-floating">
                    <input class="form-control" id="email" type="email" placeholder="email" data-sb-validations="required"  v-model="venue.email" required/>
                    <label for="email">email</label>
                    <div class="invalid-feedback" data-sb-feedback="email:required">email required.</div>
                </div>
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
               
                <button class="btn btn-primary text-uppercase" >Send</button>
            </form>
            

        </div>
</div>
</div>
</template>

<script>
export default {
  props:['venue_id'] ,
  data() {
    return {
      venue: {
        name: "",
        address: "",
        city: "",
        state: "",
        country: "",
        capacity: 0,
        phone: "",
        email: ""
      }
    };
  },
 created() {
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
    handleSubmit() {
      const venueId = this.$route.params.venue_id;
      const apiUrl = venueId !== "0" ? `/edit/${venueId}` : "/add_new_venue";
console.log("venueId:", venueId);
console.log("access_token:", localStorage.getItem("access_token"));
      // Handle form submission for updating or adding a venue
      fetch(`http://127.0.0.1:5000/api/vueeditvenue/${venueId}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          "Content-Type" : "application/json"
        },
        mode: "cors",
        body: JSON.stringify(this.venue)
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