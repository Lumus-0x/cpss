import axios from 'axios'

// Используем переменную окружения или относительный путь
// В продакшене nginx проксирует /api на backend
const API_URL = import.meta.env.VITE_API_URL || 
                import.meta.env.VITE_BACKEND_URL || 
                '/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Добавление токена из localStorage
const token = localStorage.getItem('token')
if (token) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

// Interceptor для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
