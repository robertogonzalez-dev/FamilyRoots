import { Navigate, Outlet } from "react-router-dom";
import type { User } from "../types/user";

interface Props {
  user: User | null;
}

export default function AdminOnly({ user }: Props) {
  if (!user || user.role !== "admin") return <Navigate to="/dashboard" replace />;
  return <Outlet />;
}
