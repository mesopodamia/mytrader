import { defineStore } from 'pinia'
import axios from 'axios'

interface User {
  id: number
  username: string
  email: string | null
  is_active: boolean
  is_admin: boolean
  created_at?: string
}

interface AuthState {
  token: string | null
  isAuthenticated: boolean
  user: User | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem('token'),
    isAuthenticated: !!localStorage.getItem('token'),
    user: null
  }),

  getters: {
    getUser: (state) => state.user,
    is_admin: (state) => state.user?.is_admin || false
  },

  actions: {
    async login(username: string, password: string) {
      try {
        const formData = new URLSearchParams()
        formData.append('username', username)
        formData.append('password', password)

        const response = await axios.post('/api/v1/auth/token', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        })

        this.token = response.data.access_token
        localStorage.setItem('token', response.data.access_token)
        this.isAuthenticated = true

        await this.fetchUserProfile()
        return { success: true }
      } catch (error: any) {
        console.error('登录错误:', error)
        return { 
          success: false, 
          message: error.response?.data?.detail || '登录失败' 
        }
      }
    },

    async fetchUserProfile() {
      try {
        const response = await axios.get('/api/v1/auth/me', {
          headers: {
            Authorization: `Bearer ${this.token}`
          }
        })
        this.user = response.data
      } catch (error) {
        console.error('获取用户信息失败:', error)
      }
    },

    logout() {
      this.token = null
      this.isAuthenticated = false
      this.user = null
      localStorage.removeItem('token')
    }
  }
})
