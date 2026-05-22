import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { Edit, Trash2, User, MapPin, BookOpen, UserPlus } from "lucide-react";
import toast from "react-hot-toast";
import { peopleService } from "../services/peopleService";
import RelationshipList from "../components/RelationshipList";
import AddRelationshipModal from "../components/AddRelationshipModal";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";
import { formatDate, lifespan } from "../utils/dates";
import { canEdit } from "../utils/privacy";
import type { Person, RelativesSummary } from "../types/person";
import type { User as AuthUser } from "../types/user";

interface Props { user: AuthUser }

export default function PersonDetail({ user }: Props) {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [person, setPerson] = useState<Person | null>(null);
  const [relatives, setRelatives] = useState<RelativesSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddRelationship, setShowAddRelationship] = useState(false);

  const personId = Number(id);

  const loadRelatives = () =>
    peopleService.getRelatives(personId).then(setRelatives);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    Promise.all([peopleService.get(personId), peopleService.getRelatives(personId)])
      .then(([p, r]) => { setPerson(p); setRelatives(r); })
      .catch((e) => setError(e.response?.data?.detail ?? "Failed to load person"))
      .finally(() => setLoading(false));
  }, [id]);

  const handleDelete = async () => {
    if (!person || !confirm(`Delete ${person.full_name}? This cannot be undone.`)) return;
    try {
      await peopleService.delete(person.id);
      toast.success("Person deleted");
      navigate("/people");
    } catch {
      toast.error("Failed to delete person");
    }
  };

  if (loading) return <LoadingSpinner size="lg" className="py-24" />;
  if (error) return <ErrorMessage message={error} className="mt-8" />;
  if (!person) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex items-start gap-6">
          <div className="h-24 w-24 rounded-full overflow-hidden bg-gray-100 border-4 border-white shadow shrink-0">
            {person.profile_photo_url ? (
              <img src={person.profile_photo_url} alt={person.full_name} className="h-full w-full object-cover" />
            ) : (
              <div className="h-full w-full flex items-center justify-center text-gray-300">
                <User className="h-12 w-12" />
              </div>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-3xl font-bold text-gray-900">{person.full_name || "Unknown"}</h1>
            {person.maiden_name && (
              <p className="text-gray-500 text-sm">née {person.maiden_name}</p>
            )}
            <p className="text-gray-600 mt-1">{lifespan(person.birth_date, person.death_date)}</p>
            {person.is_living && (
              <span className="inline-block mt-2 text-xs font-medium text-green-700 bg-green-100 rounded-full px-2.5 py-1">
                Living
              </span>
            )}
          </div>
          {canEdit(user) && (
            <div className="flex gap-2 shrink-0">
              <Link to={`/people/${person.id}/edit`} className="btn-secondary">
                <Edit className="h-4 w-4" />
                Edit
              </Link>
              <button onClick={handleDelete} className="btn-danger">
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Details */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Details</h2>
            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              {person.birth_date && (
                <>
                  <div>
                    <dt className="text-gray-500 font-medium">Born</dt>
                    <dd className="text-gray-900">{formatDate(person.birth_date)}</dd>
                  </div>
                  {person.birth_place && (
                    <div>
                      <dt className="text-gray-500 font-medium flex items-center gap-1"><MapPin className="h-3 w-3" />Birth Place</dt>
                      <dd className="text-gray-900">{person.birth_place}</dd>
                    </div>
                  )}
                </>
              )}
              {person.death_date && (
                <>
                  <div>
                    <dt className="text-gray-500 font-medium">Died</dt>
                    <dd className="text-gray-900">{formatDate(person.death_date)}</dd>
                  </div>
                  {person.death_place && (
                    <div>
                      <dt className="text-gray-500 font-medium flex items-center gap-1"><MapPin className="h-3 w-3" />Death Place</dt>
                      <dd className="text-gray-900">{person.death_place}</dd>
                    </div>
                  )}
                </>
              )}
              <div>
                <dt className="text-gray-500 font-medium">Gender</dt>
                <dd className="text-gray-900 capitalize">{person.gender}</dd>
              </div>
              {person.external_id && (
                <div>
                  <dt className="text-gray-500 font-medium">Ancestry ID</dt>
                  <dd className="text-gray-900 font-mono text-xs">{person.external_id}</dd>
                </div>
              )}
            </dl>
          </div>

          {person.biography && (
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-brand-600" /> Biography
              </h2>
              <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{person.biography}</p>
            </div>
          )}
        </div>

        {/* Family sidebar */}
        {relatives && (
          <div className="space-y-6">
            <div className="card space-y-6">
              <RelationshipList title="Parents" people={relatives.parents} />
              <RelationshipList title="Spouses / Partners" people={relatives.spouses} />
              <RelationshipList title="Children" people={relatives.children} />
              <RelationshipList title="Siblings" people={relatives.siblings} />
              {canEdit(user) && (
                <button
                  onClick={() => setShowAddRelationship(true)}
                  className="btn-secondary w-full justify-center text-sm"
                >
                  <UserPlus className="h-4 w-4" />
                  Add Relationship
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {showAddRelationship && person && (
        <AddRelationshipModal
          currentPersonId={person.id}
          currentPersonName={person.full_name || "this person"}
          onClose={() => setShowAddRelationship(false)}
          onAdded={loadRelatives}
        />
      )}
    </div>
  );
}
