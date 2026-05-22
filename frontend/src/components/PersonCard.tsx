import { Link } from "react-router-dom";
import { User } from "lucide-react";
import { lifespan } from "../utils/dates";
import type { PersonSummary } from "../types/person";

interface Props {
  person: PersonSummary;
}

const genderBorder = {
  male: "border-l-blue-400",
  female: "border-l-pink-400",
  unknown: "border-l-gray-300",
  other: "border-l-purple-400",
};

export default function PersonCard({ person }: Props) {
  const span = lifespan(person.birth_date, person.death_date);
  return (
    <Link
      to={`/people/${person.id}`}
      className={`card border-l-4 ${genderBorder[person.gender]} flex items-center gap-4 hover:shadow-md transition-shadow`}
    >
      <div className="shrink-0 h-12 w-12 rounded-full overflow-hidden bg-gray-100 border border-gray-200">
        {person.profile_photo_url ? (
          <img src={person.profile_photo_url} alt={person.full_name} className="h-full w-full object-cover" />
        ) : (
          <div className="h-full w-full flex items-center justify-center text-gray-400">
            <User className="h-6 w-6" />
          </div>
        )}
      </div>
      <div className="min-w-0">
        <p className="font-semibold text-gray-900 truncate">{person.full_name || "Unknown"}</p>
        <p className="text-sm text-gray-500">{span}</p>
        {person.is_living && (
          <span className="inline-block mt-1 text-xs font-medium text-green-700 bg-green-100 rounded-full px-2 py-0.5">
            Living
          </span>
        )}
      </div>
    </Link>
  );
}
