import { createContext, useContext, useState, useEffect } from 'react'
import api, { setTokens, clearTokens, getTokens } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const { access } = getTokens()
    if (!access) {
      setLoading(false)
      return
    }
    api.get('/auth/me')
      .then((res) => setUser(res.data))
      .catch(() => clearTokens())
      .finally(() => setLoading(false))
  }, [])

  async function login(email, password) {
    const { data } = await api.post('/auth/login', { email, password })
    setTokens(data)
    const me = await api.get('/auth/me')
    setUser(me.data)
    return me.data
  }

  async function registerApplicant(payload) {
    await api.post('/auth/register', payload)
    return login(payload.email, payload.password)
  }

  function logout() {
    clearTokens()
    setUser(null)
    window.location.href = '/login'
  }

  return (
    <AuthContext.Provider value={{ user, setUser, loading, login, registerApplicant, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
