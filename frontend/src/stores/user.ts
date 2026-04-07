import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_BASE_URL = '/api/v1'

interface UserInfo {
  id: number
  username: string
  email: string
  full_name: string | null
  role: string
  is_active: boolean
  created_at: string
}

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref<string | null>(localStorage.getItem('token'))
  const userInfo = ref<UserInfo | null>(null)
  const loading = ref(false)

  // Getters
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')

  // Actions
  const setToken = (newToken: string | null) => {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
    } else {
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    }
  }

  const login = async (username: string, password: string) => {
    loading.value = true
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login/json`, {
        username,
        password
      })

      const { access_token, user } = response.data
      setToken(access_token)
      userInfo.value = user

      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '登录失败'
      }
    } finally {
      loading.value = false
    }
  }

  const register = async (data: {
    username: string
    email: string
    password: string
    full_name?: string
  }) => {
    loading.value = true
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/register`, data)
      return { success: true, data: response.data }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '注册失败'
      }
    } finally {
      loading.value = false
    }
  }

  const fetchUserInfo = async () => {
    if (!token.value) return

    try {
      const response = await axios.get(`${API_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      userInfo.value = response.data
    } catch (error) {
      logout()
    }
  }

  const logout = () => {
    setToken(null)
    userInfo.value = null
  }

  const updateProfile = async (data: { full_name?: string; email?: string }) => {
    try {
      const response = await axios.put(`${API_BASE_URL}/auth/me`, data)
      userInfo.value = response.data
      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '更新失败'
      }
    }
  }

  const changePassword = async (oldPassword: string, newPassword: string) => {
    try {
      await axios.post(`${API_BASE_URL}/auth/change-password`, {
        old_password: oldPassword,
        new_password: newPassword
      })
      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '修改密码失败'
      }
    }
  }

  // 初始化时如果有token，设置axios默认header
  if (token.value) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
  }

  return {
    token,
    userInfo,
    loading,
    isLoggedIn,
    isAdmin,
    login,
    register,
    logout,
    fetchUserInfo,
    updateProfile,
    changePassword
  }
})
