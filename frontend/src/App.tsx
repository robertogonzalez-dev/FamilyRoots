import type { ReactNode } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './auth'
import { useAuth } from './useAuth'
import Login from './pages/Login'
import Trees from './pages/Trees'
import TreeView from './pages/TreeView'

function Protected({ children }: { children: ReactNode }) {
  const { user, loading, logout } = useAuth()
  if (loading) return <main className="muted">Loading…</main>
  if (!user) return <Navigate to="/login" replace />
  return (
    <>
      <header className="topbar">
        <span>🌳 FamilyRoots</span>
        <span>{user.display_name} · <button className="link" onClick={logout}>Sign out</button></span>
      </header>
      {children}
    </>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Protected><Trees /></Protected>} />
          <Route path="/trees/:treeId" element={<Protected><TreeView /></Protected>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
