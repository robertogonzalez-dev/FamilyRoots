import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";
import type { User } from "../types/user";

interface Props {
  user: User;
  onLogout: () => void;
}

export default function Layout({ user, onLogout }: Props) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user} onLogout={onLogout} />
      <main className="pt-16">
        <div className="max-w-screen-xl mx-auto px-4 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
