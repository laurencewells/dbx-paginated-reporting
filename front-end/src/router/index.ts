import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
  },
  {
    path: '/home',
    redirect: '/',
  },
  {
    path: '/data-structures',
    name: 'data-structures',
    component: () => import('@/views/DataStructuresView.vue'),
  },
  {
    path: '/template-editor',
    name: 'template-editor',
    component: () => import('@/views/TemplateEditorView.vue'),
  },
  {
    path: '/preview',
    name: 'preview',
    component: () => import('@/views/PreviewView.vue'),
  },
  {
    path: '/guide',
    name: 'guide',
    component: () => import('@/views/GuideView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
