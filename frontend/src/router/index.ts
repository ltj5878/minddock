import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/inbox',
    },
    {
      path: '/',
      component: () => import('../layouts/MainLayout.vue'),
      children: [
        {
          path: 'inbox',
          name: 'Inbox',
          component: () => import('../views/InboxView.vue'),
        },
        {
          path: 'ask',
          name: 'Ask',
          component: () => import('../views/AskView.vue'),
        },
        {
          path: 'projects',
          name: 'Projects',
          component: () => import('../views/ProjectsView.vue'),
        },
        {
          path: 'projects/:id',
          name: 'ProjectDetail',
          component: () => import('../views/ProjectDetailView.vue'),
        },
        {
          path: 'review',
          name: 'Review',
          component: () => import('../views/ReviewView.vue'),
        },
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('../views/SettingsView.vue'),
        },
      ],
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/LoginView.vue'),
    },
  ],
})

export default router
