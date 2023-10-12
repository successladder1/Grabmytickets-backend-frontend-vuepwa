<template>
  <div class="container">
    <form class="form-signin">
      <h1 class="h3 mb-3 font-weight-normal">USER REGISTRATION</h1>
      <input type="text" class="form-control" placeholder="Email" required autofocus v-model="email">
      <input type="text" class="form-control" placeholder="Username" required autofocus v-model="username">
      <input type="password" class="form-control" placeholder="Password" required v-model="password">
      <button class="btn btn-lg btn-primary btn-block" v-on:click="loginclick">Sign in</button>
      <p class="mt-5 mb-3 text-muted">&copy; GrabMyTickets</p>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: "",
      password: "",
      email: "",
      emailIsValid: true
    };
  },
  methods: {
    loginclick: async function () {
       this.emailIsValid = this.validateEmail(this.email);

      if (!this.emailIsValid) {
        alert('Invalid email')
      }
      else{
      const loginData = {
        email: this.email,
        username: this.username,
        password: this.password
      };

      fetch("http://127.0.0.1:5000/api/vueregister", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(loginData)
      })
        .then((response) => {
          // Check if the response status is 200
          if (response.status === 200) {
            // Handle the JSON data returned from the server
            response.json().then((data) => {
              console.log(data); // Print the response data to the console
              confirm(data.message)
              this.$router.push({ name: "login" });
              
          }
            );
          } else if (response.status === 401) {
            // Invalid credentials, show an error message
            throw new Error("User already exists");
          } else {
            throw new Error("Server error");
          }
        })
        .catch((error) => {
          // Handle errors from the fetch request
          console.error("Error:", error.message);
          alert("Invalid credentials"); // Show an error message to the user
        });
      }
    },
    validateEmail: function (email) {
      // Regular expression for basic email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    }}
};
</script>

<style scoped>
/* Add your CSS styles here */
html,
body {
  height: 100%;
}

body {
  display: -ms-flexbox;
  display: -webkit-box;
  display: flex;
  -ms-flex-align: center;
  -ms-flex-pack: center;
  -webkit-box-align: center;
  align-items: center;
  -webkit-box-pack: center;
  justify-content: center;
  padding-top: 40px;
  padding-bottom: 40px;
  background-color: #f5f5f5;
}

.form-signin {
  width: 100%;
  max-width: 330px;
  padding: 15px;
  margin: 0 auto;
}
.form-signin .checkbox {
  font-weight: 400;
}
.form-signin .form-control {
  position: relative;
  box-sizing: border-box;
  height: auto;
  padding: 10px;
  font-size: 16px;
}
.form-signin .form-control:focus {
  z-index: 2;
}
.form-signin input[type="email"] {
  margin-bottom: -1px;
  border-bottom-right-radius: 0;
  border-bottom-left-radius: 0;
}
.form-signin input[type="password"] {
  margin-bottom: 10px;
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}

</style>