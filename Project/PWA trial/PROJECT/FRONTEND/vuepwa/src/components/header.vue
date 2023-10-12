<template>
<div>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <router-link class="navbar-brand" to="/">GrabMyTickets</router-link>
    <button
      class="navbar-toggler"
      type="button"
      @click="isNavOpen = !isNavOpen"
      aria-expanded="false"
      aria-label="Toggle navigation"
    >
      <span class="navbar-toggler-icon"></span>
    </button>
    <div :class="navClasses">
      <ul class="navbar-nav">
        <li class="nav-item">
          <router-link class="nav-link" to="/">Home</router-link>
        </li>
        <li class="nav-item" v-if="isLoggedOut">
          <router-link class="nav-link" to="/login">Login</router-link>
        </li>
        <li class="nav-item" v-else>
          <a class="nav-link" @click="logout">Logout</a>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/register">Register</router-link>
        </li>
        <li class="nav-item" v-if="!testIsLoggedOut && is_admin">
          <router-link class="nav-link" to="/vueadmin_dashboard">Admin Dashboard</router-link>
        </li>
        <li class="nav-item" v-if="!testIsLoggedOut && !is_admin">
          <router-link :to="`/vueuserdashboard/${user_id}`" class="nav-link">User Dashboard</router-link>
        </li>
        <li class="nav-item" v-if="!testIsLoggedOut && !is_admin">
          <router-link :to="`/vueuserbookings/${user_id}`" class="nav-link">User Bookings</router-link>
        </li>
        <li class="nav-item" v-if="!testIsLoggedOut && is_admin">
          <router-link to="/vuepopularitychart" class="nav-link">Popularity Chart</router-link>
        </li>
      </ul>
    </div>
  </nav>
  <router-view :key="$route.fullPath" />
</div>
</template>

<script>

export default {
  data() {
    return {
      isNavOpen: false,
      testIsLoggedOut: this.isLoggedOut,
    };
  },
  methods: {
    handleResize() {
      this.isNavOpen = window.innerWidth >= 992;
    },
    logout() {
      // Remove the "access_token" from local storage
      localStorage.removeItem("access_token");

      // Emit the 'loginStatusChanged' event to update the login status
      this.$emit("loginStatusChanged", true);

      // Redirect the user to the login page after logout
      this.$router.push("/login");
    },
  },
  computed: {
    navClasses() {
      // Use Bootstrap's responsive classes to conditionally apply classes
      return {
        'collapse navbar-collapse': true,
        show: this.isNavOpen || window.innerWidth >= 992 // Expand on desktop (lg breakpoint)
      };
    },
    isLoggedOut() {
      // Check if the JWT token exists in local storage
      const token = localStorage.getItem("access_token");
      if (token) {
        const decodedToken = JSON.parse(atob(token.split(".")[1]));
        const expirationDate = new Date(decodedToken.exp * 1000);
        // Compare the expiration date with the current date
        return expirationDate <= new Date();
      } else {
        return true;
      }
    },
    is_admin() {
      const token = localStorage.getItem("access_token");
      if (token) {
        const decodedToken = JSON.parse(atob(token.split(".")[1]));
        const is_admin = decodedToken.is_admin;
        return is_admin === true;
      } else {
        return false;
      }
    },
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
  },
created() {
    // Listen for a custom event 'loginStatusChanged'
    // and update the isLoggedOut property accordingly
    this.$on("loginStatusChanged", (loggedIn) => {
      this.testIsLoggedOut = !loggedIn;
    });
    this.testIsLoggedOut = this.isLoggedOut;
  },
  beforeRouteUpdate(to, from, next) {
    // Force reload the component when the route is updated
    window.location.reload();
    next();
  },
  mounted() {
    window.addEventListener('resize', this.handleResize);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize);
  }
}
</script>

<style>
@media (max-width: 767px) {
  .navbar-nav {
    flex-direction: column;
  }
}
</style>