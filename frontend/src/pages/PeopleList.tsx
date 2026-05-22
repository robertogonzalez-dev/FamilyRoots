import { useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { UserPlus } from "lucide-react";
import { usePeople } from "../hooks/usePeople";
import PersonCard from "../components/PersonCard";
import SearchBar from "../components/SearchBar";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";
import type { User } from "../types/user";
import { canEdit } from "../utils/privacy";

interface Props { user: User }

export default function PeopleList({ user }: Props) {
  const { people, loading, error, fetch } = usePeople();

  useEffect(() => { fetch(); }, [fetch]);

  const handleSearch = useCallback(
    (term: string) => { fetch(term || undefined); },
    [fetch]
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">People</h1>
          <p className="text-gray-500">{people.length} records found</p>
        </div>
        {canEdit(user) && (
          <Link to="/people/add" className="btn-primary">
            <UserPlus className="h-4 w-4" />
            Add Person
          </Link>
        )}
      </div>

      <SearchBar onSearch={handleSearch} placeholder="Search by name..." />

      {loading && <LoadingSpinner className="py-12" />}
      {error && <ErrorMessage message={error} />}
      {!loading && !error && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {people.map((p) => <PersonCard key={p.id} person={p} />)}
          {people.length === 0 && (
            <p className="col-span-3 text-center text-gray-400 py-12">No people found.</p>
          )}
        </div>
      )}
    </div>
  );
}
