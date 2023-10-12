<template>
    <div class="row gx-4 gx-lg-5 justify-content-center">
        <div class="col-md-10 col-lg-8 col-xl-7">
            <form id="contactForm" @submit.prevent="handleSubmit" >
                <div class="form-floating">
                    <input class="form-control" id="title" type="text" placeholder="title" data-sb-validations="required" v-model="movie.title"  required />
                    <label for="title">Name</label>
                    <div class="invalid-feedback" data-sb-feedback="title:required">A title is required.</div>
                </div>
                <div class="form-floating">
                    <input class="form-control" id="genre" type="text" placeholder="genre" data-sb-validations="required" v-model="movie.genre"  required />
                    <label for="genre">genre</label>
                    <div class="invalid-feedback" data-sb-feedback="genre:required">An genre is required.</div>
                </div>
                <div class="form-floating">
                    <input class="form-control" id="language" type="text" placeholder="language" data-sb-validations="required" v-model="movie.language"  required />
                    <label for="language">language</label>
                    <div class="invalid-feedback" data-sb-feedback="language:required">A language is required.</div>
                </div>
                <div class="form-floating">
                    <input class="form-control" id="runtime" type="text" placeholder="runtime" data-sb-validations="required" v-model="movie.runtime"  required />
                    <label for="runtime">runtime</label>
                    <div class="invalid-feedback" data-sb-feedback="runtime:required">runtime is required.</div>
                </div>
                <div class="form-floating">
                    <input class="form-control" id="rating" type="text" placeholder="rating" data-sb-validations="required" v-model="movie.rating"  required />
                    <label for="rating">rating</label>
                    <div class="invalid-feedback" data-sb-feedback="rating:required">rating is required.</div>
                </div>
                <div class="form-floating">
                    <input class="form-control" id="director" type="text" placeholder="director" data-sb-validations="required" v-model="movie.director"  required />
                    <label for="director">director</label>
                    <div class="invalid-feedback" data-sb-feedback="director:required">director required.</div>
                </div>
                <div class="form-floating">
                    <input class="form-control" id="synopsis" type="text" placeholder="synopsis" data-sb-validations="required" v-model="movie.synopsis"  required />
                    <label for="synopsis">synopsis</label>
                    <div class="invalid-feedback" data-sb-feedback="synopsis:required">synopsis required.</div>
                </div>
                <div class="form-floating">
                    <input class="form-control" id="release_date" type="text" placeholder="release_date" data-sb-validations="required" v-model="movie.release_date"  required />
                    <label for="release_date">release_date</label>
                    <div class="invalid-feedback" data-sb-feedback="release_date:required">release_date required.</div>
                </div>
                <div class="form-floating">
                    <input class="form-control" id="trailer_url" type="text" pattern="https?://.+" placeholder="trailer_url" data-sb-validations="required" v-model="movie.trailer_url"  required/>
                    <label for="trailer_url">trailer_url</label>
                    <div class="invalid-feedback" data-sb-feedback="trailer_url:required">trailer_url required.</div>
                </div>
                <div class="form-floating">
                  <input class="form-control" id="price" type="number" placeholder="price" data-sb-validations="required" v-model="movie.price"  required min="0" />
                  <label for="price">price. Only numerical values allowed.</label>
                  <div class="invalid-feedback" data-sb-feedback="price:required">price required.</div>
              </div>
              <div class="form-floating">
                <input class="form-control" id="date" type="text" placeholder="date" data-sb-validations="required"  v-model="movie.date"/>
                <label for="date">date of show (Readable)</label>
                <div class="invalid-feedback" data-sb-feedback="date:required">date of show required.</div>
            </div>
            <div class="form-floating">
              
              <input class="form-control" type="text" id="time" name="time" placeholder="datetime" data-sb-validations="required" pattern="\d{2}:\d{2}:\d{4} \d{2}:\d{2}:\d{2}" required title="Please enter the datetime in dd:mm:yyyy hh:mm:ss format" v-model="movie.time">
              <label for="time">Enter show datetime (dd:mm:yyyy hh:mm:ss):</label>
              <div class="invalid-feedback" data-sb-feedback="time:required">time required.</div>
          </div>
          <div class="form-floating">
            <input class="form-control" id="seats_available" type="number" placeholder="seats_available" data-sb-validations="required" name="seats_available" v-model="movie.seats_available" required min="0" />
            <label for="seats_available">seats available. Only numerical values allowed.</label>
            <div class="invalid-feedback" data-sb-feedback="price:required">seats available required.</div>
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
                
                <button class="btn btn-primary text-uppercase" id="submitButton" type="submit">Send</button>
            </form>

            


            <hr class="my-4" />

        </div></div>
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
      fetch(`http://127.0.0.1:5000/api/vueeditmovie/${venueId}/${movieId}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          "Content-Type" : "application/json"
        },
        mode: "cors",
        body: JSON.stringify(this.movie)
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