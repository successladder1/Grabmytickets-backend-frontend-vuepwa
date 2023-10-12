<template>
  <div>
    <h1>Welcome to Admin dashboard</h1>
    <div class="row gx-4 gx-lg-5 justify-content-center">
      <div class="col-12">
        <router-link to="/vuevenueedit/0">
          <button>Add a new VENUE</button>
        </router-link>
        <h1>Venues</h1>
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th scope="col">SNo</th>
                <th scope="col">Name</th>
                <th scope="col">Address</th>
                <th scope="col">City</th>
                <th scope="col">State</th>
                <th scope="col">Country</th>
                <th scope="col">Capacity</th>
                <th scope="col">Phone</th>
                <th scope="col">Email</th>
                <th scope="col">Export</th>
                <th scope="col">Edit</th>
                <th scope="col">Delete</th>
                <th scope="col">Movies</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="venue in venues" :key="venue.venue_id">
                <td>{{ venue.venue_id }}</td>
                <td>{{ venue.name }}</td>
                <td>{{ venue.address }}</td>
                <td>{{ venue.city }}</td>
                <td>{{ venue.state }}</td>
                <td>{{ venue.country }}</td>
                <td>{{ venue.capacity }}</td>
                <td>{{ venue.phone }}</td>
                <td>{{ venue.email }}</td>
                <td>
                  <button v-on:click="csvhandler(venue.venue_id)">Click</button>
                </td>
                <td>
                  <router-link
                    :to="{ name: 'vuevenueedit', params: { venue_id: venue.venue_id } }"
                  >
                    <button>Edit</button>
                  </router-link>
                </td>
                <td>
                  <router-link
                    :to="{ name: 'vuevenuedelete', params: { venue_id: venue.venue_id } }"
                  >
                    <button>Delete</button>
                  </router-link>
                </td>
                <td>
                  <router-link
                    :to="{ name: 'vuevenue_movie_dashboard', params: { venue_id: venue.venue_id } }"
                  >
                    <button>Go to Movies</button>
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  delimiters: ['${','}'],
  data() {
    return {
      venues:[]
    }
  },
  mounted() {
    this.fetchVenues();
  },
  methods: {
    fetchVenues() {
      console.log('Fetching venues...');
      fetch('http://127.0.0.1:5000/api/vueadmin_dashboard', {
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
          this.$set(this, 'venues', data.venues_data);
          console.log(this.venues)
        })
        .catch((error) => {
          console.error('Error:', error);
        });
    },
        csvhandler(venue_id) {
          console.log(`http://127.0.0.1:5000/generate_csv/${venue_id}`)
      fetch(`http://127.0.0.1:5000/generate_csv/${venue_id}`)
        .then((response) => response.json())
        .then((data) => {
          console.log('Task ID:', data.task_id);
          return data.task_id;
        })
        .then((taskId) => {
          const interval = setInterval(() => {
            fetch(`http://127.0.0.1:5000/status/${taskId}`)
              .then((response) => response.json())
              .then((data) => {
                console.log(data);
                if (data.status === 'SUCCESS') {
                  console.log('CSV generation successful');
                  
                  clearInterval(interval); // Stop the interval once task is completed
                  window.location.href='http://127.0.0.1:5000/download-file'
                } else if (data.status === 'PENDING' || data.status === 'STARTED') {
                  console.log('CSV generation in progress...');
                } else {
                  console.error('CSV generation failed');
                  clearInterval(interval); // Stop the interval on failure as well
                }
              })
              .catch((error) => {
                console.error('Error:', error);
                clearInterval(interval); // Stop the interval on error as well
              });
          }, 1000); // Check status every 1 second
        })
        .catch((error) => {
          console.error('Error:', error);
        });
    }
  }
};
</script>

<style scoped>

</style>
