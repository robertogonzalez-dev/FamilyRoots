import { Navigate, Outlet } from "react-router-dom";
import LoadingSpinner from "./LoadingSpinner";
import type { User } from "../types/user";

interface Props {
  user: User | null;
  loading: boolean;
}

export default function ProtectedRoute({ user, loading }: Props) {
  if (loading) return <LoadingSpinner size="lg" className="min-h-screen" />;
  if (!user) return <Navigate to="/login" replace />;
  return <Outlet />;
}
