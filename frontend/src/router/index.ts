import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false, title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/DashboardView.vue'),
          meta: { title: '控制台', icon: 'Odometer' }
        },
        {
          path: 'stocks',
          name: 'Stocks',
          component: () => import('@/views/StocksView.vue'),
          meta: { title: '自选股票', icon: 'Star' }
        },
        {
          path: 'stock/:code',
          name: 'StockDetail',
          component: () => import('@/views/StockDetailView.vue'),
          meta: { title: '股票详情', icon: 'InfoFilled' }
        },
        {
          path: 'categories',
          name: 'StockCategories',
          component: () => import('@/views/StockCategoriesView.vue'),
          meta: { title: '股票分类', icon: 'Grid' }
        },
        {
          path: 'my-categories',
          name: 'Category',
          component: () => import('@/views/CategoryView.vue'),
          meta: { title: '自定义分类', icon: 'Collection' }
        },
        {
          path: 'alerts',
          name: 'Alert',
          component: () => import('@/views/AlertView.vue'),
          meta: { title: '股票预警', icon: 'BellFilled' }
        },
        {
          path: 'sentiment',
          name: 'Sentiment',
          component: () => import('@/views/SentimentView.vue'),
          meta: { title: '舆情分析', icon: 'TrendCharts' }
        },
        {
          path: 'trading',
          name: 'Trading',
          component: () => import('@/views/TradingView.vue'),
          meta: { title: '模拟交易', icon: 'Money' }
        },
        {
          path: 'portfolio',
          name: 'Portfolio',
          component: () => import('@/views/PortfolioView.vue'),
          meta: { title: '投资组合', icon: 'Wallet' }
        },
        {
          path: 'analysis',
          name: 'Analysis',
          component: () => import('@/views/AnalysisView.vue'),
          meta: { title: '数据分析', icon: 'DataAnalysis' }
        },
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('@/views/SettingsView.vue'),
          meta: { title: '系统设置', icon: 'Setting' }
        }
      ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: '404', requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - AI Trader`
  }

  // 认证检查
  if (to.meta.requiresAuth && !userStore.token) {
    next('/login')
  } else if (to.path === '/login' && userStore.token) {
    next('/')
  } else {
    next()
  }
})

export default router
