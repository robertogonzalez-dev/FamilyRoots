import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./hooks/useAuth";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminOnly from "./components/AdminOnly";
import LoadingSpinner from "./components/LoadingSpinner";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import PeopleList from "./pages/PeopleList";
import PersonDetail from "./pages/PersonDetail";
import AddPerson from "./pages/AddPerson";
import EditPerson from "./pages/EditPerson";
import FamilyTree from "./pages/FamilyTree";
import AdminDashboard from "./pages/AdminDashboard";
import AdminUsers from "./pages/AdminUsers";
import GedcomImport from "./pages/GedcomImport";

export default function App() {
  const { user, loading, isAuthenticated, login, logout } = useAuth();

  if (loading) return <LoadingSpinner size="lg" className="min-h-screen" />;

  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login onLogin={login} />} />
      <Route path="/register" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Register />} />

      {/* Protected */}
      <Route element={<ProtectedRoute user={user} loading={false} />}>
        <Route element={<Layout user={user!} onLogout={logout} />}>
          <Route path="/dashboard" element={<Dashboard user={user!} />} />
          <Route path="/people" element={<PeopleList user={user!} />} />
          <Route path="/people/add" element={<AddPerson />} />
          <Route path="/people/:id" element={<PersonDetail user={user!} />} />
          <Route path="/people/:id/edit" element={<EditPerson />} />
          <Route path="/tree" element={<FamilyTree />} />

          {/* Admin only */}
          <Route element={<AdminOnly user={user} />}>
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/admin/users" element={<AdminUsers />} />
            <Route path="/admin/gedcom" element={<GedcomImport />} />
          </Route>
        </Route>
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} />
    </Routes>
  );
}
