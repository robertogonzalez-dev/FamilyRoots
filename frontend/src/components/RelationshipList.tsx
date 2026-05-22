import { Link } from "react-router-dom";
import { User } from "lucide-react";
import { lifespan } from "../utils/dates";
import type { PersonSummary } from "../types/person";

interface Props {
  title: string;
  people: PersonSummary[];
  emptyMessage?: string;
}

export default function RelationshipList({ title, people, emptyMessage = "None recorded" }: Props) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">{title}</h3>
      {people.length === 0 ? (
        <p className="text-sm text-gray-400 italic">{emptyMessage}</p>
      ) : (
        <div className="space-y-2">
          {people.map((p) => (
            <Link
              key={p.id}
              to={`/people/${p.id}`}
              className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="h-9 w-9 rounded-full overflow-hidden bg-gray-100 border border-gray-200 shrink-0">
                {p.profile_photo_url ? (
                  <img src={p.profile_photo_url} alt={p.full_name} className="h-full w-full object-cover" />
                ) : (
                  <div className="h-full w-full flex items-center justify-center text-gray-400">
                    <User className="h-4 w-4" />
                  </div>
                )}
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">{p.full_name}</p>
                <p className="text-xs text-gray-500">{lifespan(p.birth_date, p.death_date)}</p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
