import { Link } from "react-router-dom";
import { Users, Upload } from "lucide-react";

export default function AdminDashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Admin Panel</h1>
        <p className="text-gray-500">Manage your FamilyRoots site.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Link to="/admin/users" className="card hover:shadow-md transition-shadow group">
          <Users className="h-8 w-8 text-brand-600 mb-3" />
          <h3 className="font-semibold text-gray-900 group-hover:text-brand-600">User Management</h3>
          <p className="text-sm text-gray-500 mt-1">Invite family members and manage roles</p>
        </Link>
        <Link to="/admin/gedcom" className="card hover:shadow-md transition-shadow group">
          <Upload className="h-8 w-8 text-brand-600 mb-3" />
          <h3 className="font-semibold text-gray-900 group-hover:text-brand-600">Import GEDCOM</h3>
          <p className="text-sm text-gray-500 mt-1">Upload a .ged file from Ancestry.com</p>
        </Link>
      </div>
    </div>
  );
}
