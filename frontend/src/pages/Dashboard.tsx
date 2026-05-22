import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Users, Network, UserCheck, Heart } from "lucide-react";
import { adminService } from "../services/adminService";
import LoadingSpinner from "../components/LoadingSpinner";
import type { User } from "../types/user";

interface Props { user: User }

interface Stats {
  total_people: number;
  total_relationships: number;
  total_users: number;
  living_people: number;
}

const statCards = [
  { key: "total_people" as const, label: "People", icon: Users, color: "text-blue-600 bg-blue-50", link: "/people" },
  { key: "total_relationships" as const, label: "Relationships", icon: Heart, color: "text-pink-600 bg-pink-50", link: "/tree" },
  { key: "living_people" as const, label: "Living", icon: UserCheck, color: "text-green-600 bg-green-50", link: "/people" },
  { key: "total_users" as const, label: "Users", icon: Network, color: "text-purple-600 bg-purple-50", link: "/admin" },
];

export default function Dashboard({ user }: Props) {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user.role === "admin") {
      setLoading(true);
      adminService.getDashboard().then(setStats).finally(() => setLoading(false));
    }
  }, [user.role]);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Welcome back, {user.full_name.split(" ")[0]}!</h1>
        <p className="text-gray-500 mt-1">Your family history is waiting to be explored.</p>
      </div>

      {user.role === "admin" && (
        <div>
          <h2 className="text-lg font-semibold text-gray-700 mb-4">Overview</h2>
          {loading ? (
            <LoadingSpinner />
          ) : stats ? (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {statCards.map(({ key, label, icon: Icon, color, link }) => (
                <Link key={key} to={link} className="card flex items-center gap-4 hover:shadow-md transition-shadow">
                  <div className={`p-3 rounded-xl ${color}`}>
                    <Icon className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-gray-900">{stats[key].toLocaleString()}</p>
                    <p className="text-sm text-gray-500">{label}</p>
                  </div>
                </Link>
              ))}
            </div>
          ) : null}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link to="/people" className="card hover:shadow-md transition-shadow group">
          <Users className="h-8 w-8 text-brand-600 mb-3" />
          <h3 className="font-semibold text-gray-900 group-hover:text-brand-600 transition-colors">Browse People</h3>
          <p className="text-sm text-gray-500 mt-1">View and search family members</p>
        </Link>
        <Link to="/tree" className="card hover:shadow-md transition-shadow group">
          <Network className="h-8 w-8 text-brand-600 mb-3" />
          <h3 className="font-semibold text-gray-900 group-hover:text-brand-600 transition-colors">Family Tree</h3>
          <p className="text-sm text-gray-500 mt-1">Interactive visual family tree</p>
        </Link>
        {user.role === "admin" && (
          <Link to="/admin" className="card hover:shadow-md transition-shadow group">
            <UserCheck className="h-8 w-8 text-brand-600 mb-3" />
            <h3 className="font-semibold text-gray-900 group-hover:text-brand-600 transition-colors">Admin Panel</h3>
            <p className="text-sm text-gray-500 mt-1">Manage users and import data</p>
          </Link>
        )}
      </div>
    </div>
  );
}
