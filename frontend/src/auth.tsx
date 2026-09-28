import { useEffect, useState, type ReactNode } from 'react'
import { api, token, type User } from './api'
import { AuthContext } from './useAuth'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(() => token.get() !== null)

  useEffect(() => {
    if (!token.get()) return
    api.me().then(setUser).catch(() => token.set(null)).finally(() => setLoading(false))
  }, [])

  const login = async (email: string, password: string) => {
    token.set((await api.login(email, password)).access_token)
    setUser(await api.me())
  }
  const register = async (email: string, password: string, name: string) => {
    await api.register(email, password, name)
    await login(email, password)
  }
  const logout = () => { token.set(null); setUser(null) }

  return <AuthContext.Provider value={{ user, loading, login, register, logout }}>{children}</AuthContext.Provider>
}
