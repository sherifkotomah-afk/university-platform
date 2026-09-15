import axios from 'axios'

// Set VITE_API_URL in your Vercel environment variables to point at your
// Render backend, e.g. https://university-platform-api.onrender.com
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({ baseURL: API_URL })

// --- Per-tab sessions ---
// Deliberately using sessionStorage, not localStorage. sessionStorage is
// isolated per browser tab, so opening a second tab and logging in as a
// different user does NOT affect the first tab's session. The tradeoff:
// closing a tab ends that tab's session — there is no "stay logged in
// after closing the tab" with this approach, because that's what makes
// tabs independent in the first place. True cookies can't do this: cookies
// are shared across every tab of the same browser for the same site.
function getTokens() {
  return {
    access: sessionStorage.getItem('access_token'),
    refresh: sessionStorage.getItem('refresh_token'),
  }
}

function setTokens({ access_token, refresh_token }) {
  if (access_token) sessionStorage.setItem('access_token', access_token)
  if (refresh_token) sessionStorage.setItem('refresh_token', refresh_token)
}

export function clearTokens() {
  sessionStorage.removeItem('access_token')
  sessionStorage.removeItem('refresh_token')
}

api.interceptors.request.use((config) => {
  const { access } = getTokens()
  if (access) config.headers.Authorization = `Bearer ${access}`
  return config
})

// If a request 401s, try refreshing the access token once, then retry.
let isRefreshing = false
let queue = []

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      const { refresh } = getTokens()
      if (!refresh) {
        clearTokens()
        window.location.href = '/login'
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          queue.push({ resolve, reject })
        }).then(() => api(originalRequest))
      }

      originalRequest._retry = true
      isRefreshing = true
      try {
        const { data } = await axios.post(`${API_URL}/auth/refresh`, { refresh_token: refresh })
        setTokens(data)
        queue.forEach((p) => p.resolve())
        queue = []
        return api(originalRequest)
      } catch (refreshError) {
        clearTokens()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  }
)

export { setTokens, getTokens }
export default api
