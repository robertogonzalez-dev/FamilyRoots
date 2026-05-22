import { useEffect, useRef, useState } from "react";
import { X, Search, User } from "lucide-react";
import toast from "react-hot-toast";
import { peopleService } from "../services/peopleService";
import { relationshipService } from "../services/relationshipService";
import { lifespan } from "../utils/dates";
import type { PersonSummary } from "../types/person";
import type { RelationshipCreate, RelationshipType } from "../types/relationship";

interface Props {
  currentPersonId: number;
  currentPersonName: string;
  onClose: () => void;
  onAdded: () => void;
}

type Direction = "is_parent_of" | "is_child_of" | "is_sibling_of" | "is_spouse_of";

const DIRECTION_LABELS: { value: Direction; label: string }[] = [
  { value: "is_parent_of", label: "is a parent of" },
  { value: "is_child_of", label: "is a child of" },
  { value: "is_sibling_of", label: "is a sibling of" },
  { value: "is_spouse_of", label: "is a spouse/partner of" },
];

function buildRelationship(
  currentId: number,
  otherId: number,
  direction: Direction
): RelationshipCreate {
  if (direction === "is_parent_of") {
    return { person1_id: otherId, person2_id: currentId, relationship_type: "parent_child" };
  }
  if (direction === "is_child_of") {
    return { person1_id: currentId, person2_id: otherId, relationship_type: "parent_child" };
  }
  const type: RelationshipType = direction === "is_spouse_of" ? "spouse" : "sibling";
  return { person1_id: currentId, person2_id: otherId, relationship_type: type };
}

export default function AddRelationshipModal({ currentPersonId, currentPersonName, onClose, onAdded }: Props) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<PersonSummary[]>([]);
  const [selected, setSelected] = useState<PersonSummary | null>(null);
  const [direction, setDirection] = useState<Direction>("is_sibling_of");
  const [saving, setSaving] = useState(false);
  const searchRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    searchRef.current?.focus();
  }, []);

  useEffect(() => {
    if (!query.trim()) { setResults([]); return; }
    const timer = setTimeout(async () => {
      const people = await peopleService.list(query);
      setResults(people.filter((p) => p.id !== currentPersonId));
    }, 300);
    return () => clearTimeout(timer);
  }, [query, currentPersonId]);

  const handleSubmit = async () => {
    if (!selected) return;
    setSaving(true);
    try {
      const rel = buildRelationship(currentPersonId, selected.id, direction);
      await relationshipService.create(rel);
      toast.success(`Relationship added`);
      onAdded();
      onClose();
    } catch {
      toast.error("Failed to add relationship");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={onClose}>
      <div
        className="bg-white rounded-2xl shadow-xl w-full max-w-md"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">Add Relationship</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          {/* Person search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search person</label>
            {selected ? (
              <div className="flex items-center gap-3 p-3 rounded-lg border border-brand-300 bg-brand-50">
                <div className="h-9 w-9 rounded-full bg-gray-100 border border-gray-200 flex items-center justify-center shrink-0">
                  {selected.profile_photo_url ? (
                    <img src={selected.profile_photo_url} alt={selected.full_name} className="h-full w-full rounded-full object-cover" />
                  ) : (
                    <User className="h-4 w-4 text-gray-400" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">{selected.full_name}</p>
                  <p className="text-xs text-gray-500">{lifespan(selected.birth_date, selected.death_date)}</p>
                </div>
                <button
                  className="text-xs text-gray-400 hover:text-gray-600"
                  onClick={() => setSelected(null)}
                >
                  Change
                </button>
              </div>
            ) : (
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
                <input
                  ref={searchRef}
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Type a name…"
                  className="input pl-9"
                />
                {results.length > 0 && (
                  <div className="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded-xl shadow-lg max-h-52 overflow-y-auto">
                    {results.map((p) => (
                      <button
                        key={p.id}
                        className="flex items-center gap-3 w-full px-3 py-2 hover:bg-gray-50 text-left"
                        onClick={() => { setSelected(p); setQuery(""); setResults([]); }}
                      >
                        <div className="h-8 w-8 rounded-full bg-gray-100 border border-gray-200 flex items-center justify-center shrink-0">
                          {p.profile_photo_url ? (
                            <img src={p.profile_photo_url} alt={p.full_name} className="h-full w-full rounded-full object-cover" />
                          ) : (
                            <User className="h-4 w-4 text-gray-400" />
                          )}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">{p.full_name}</p>
                          <p className="text-xs text-gray-500">{lifespan(p.birth_date, p.death_date)}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Relationship direction */}
          {selected && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Relationship</label>
              <p className="text-sm text-gray-500 mb-2">
                <span className="font-medium text-gray-800">{selected.full_name}</span>
                {" "}
                <span className="italic">&nbsp;&nbsp;&nbsp;</span>
                {" "}
                <span className="font-medium text-gray-800">{currentPersonName}</span>
              </p>
              <div className="grid grid-cols-2 gap-2">
                {DIRECTION_LABELS.map(({ value, label }) => (
                  <button
                    key={value}
                    onClick={() => setDirection(value)}
                    className={`px-3 py-2 text-sm rounded-lg border text-left transition-colors ${
                      direction === value
                        ? "border-brand-500 bg-brand-50 text-brand-700 font-medium"
                        : "border-gray-200 text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-end gap-3 p-5 border-t border-gray-100">
          <button onClick={onClose} className="btn-secondary">Cancel</button>
          <button
            onClick={handleSubmit}
            disabled={!selected || saving}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? "Saving…" : "Add Relationship"}
          </button>
        </div>
      </div>
    </div>
  );
}
