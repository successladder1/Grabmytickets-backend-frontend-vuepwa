import Vue from 'vue'
import Router from 'vue-router'
import Login from '@/components/Login'
import Home from '@/components/Home'
import admin_dashboard from '@/components/admin_dashboard'
import register from '@/components/Register'
import venue_movie_dashboard from '@/components/venue_movie_dashboard'
import vuevenueedit from '@/components/vuevenueedit'
import vuemovieedit from '@/components/vuemovieedit'
import vuevenuedelete from '@/components/vuevenuedelete'
import vuemoviedelete from '@/components/vuemoviedelete'
import vueuserdashboard from '@/components/vueuserdashboard'
import vuebook from '@/components/vuebook'
import vueuserbookings from '@/components/vueuserbookings'
import vuevenuedetails from '@/components/vuevenuedetails'
import vuepopularitychart from '@/components/vuepopularitychart'
Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/vueadmin_dashboard',
      name: 'admin_dashboard',
      component: admin_dashboard
    },
    {
      path: '/register',
      name: 'register',
      component: register
    },
    {
      path: '/vuevenue_movie_dashboard/:venue_id',
      name: 'vuevenue_movie_dashboard',
      component: venue_movie_dashboard,
      props: true
    },
    {
      path: '/vuevenueedit/:venue_id',
      name: 'vuevenueedit',
      component: vuevenueedit,
      props:true
    },
    {
      path: '/vuemovieedit/:venue_id/:movie_id',
      name: 'vuemovieedit',
      component: vuemovieedit,
      props:true
    },
    {
      path: '/vuevenuedelete/:venue_id',
      name: 'vuevenuedelete',
      component: vuevenuedelete,
      props:true
    },
    {
      path: '/vuemoviedelete/:venue_id/:movie_id',
      name: 'vuemoviedelete',
      component: vuemoviedelete,
      props:true
    },
    {
      path: '/vueuserdashboard/:user_id',
      name: 'vueuserdashboard',
      component: vueuserdashboard,
      props:true
    },
    {
      path: '/vuebook/:user_id/:venue_id/:movie_id',
      name: 'vuebook',
      component: vuebook,
      props:true
    },
    {
      path: '/vueuserbookings/:user_id',
      name: 'vueuserbookings',
      component: vueuserbookings,
      props:true
    },
    {
      path:'/vuevenuedetails/:user_id/:venue_id',
      name:'vuevenuedetails',
      component: vuevenuedetails,
      props:true
    },
    {
      path:'/vuepopularitychart',
      name:'vuepopularitychart',
      component: vuepopularitychart,
      props:true
    }



  ]
})
