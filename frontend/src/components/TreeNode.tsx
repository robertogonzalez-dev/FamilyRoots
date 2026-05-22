import { memo } from "react";
import { Handle, Position } from "reactflow";
import { useNavigate } from "react-router-dom";
import { User } from "lucide-react";

interface NodeData {
  person_id: number;
  full_name: string;
  birth_year?: number;
  death_year?: number;
  gender: string;
  is_living: boolean;
  profile_photo_url?: string;
  isFocal?: boolean;
}

const genderBg: Record<string, string> = {
  male: "bg-blue-50 border-blue-300",
  female: "bg-pink-50 border-pink-300",
  unknown: "bg-gray-50 border-gray-300",
  other: "bg-purple-50 border-purple-300",
};

function TreeNode({ data }: { data: NodeData }) {
  const navigate = useNavigate();
  const bg = genderBg[data.gender] ?? genderBg.unknown;
  const years = data.birth_year
    ? data.death_year
      ? `${data.birth_year} – ${data.death_year}`
      : `b. ${data.birth_year}`
    : "";

  return (
    <div
      onClick={() => navigate(`/people/${data.person_id}`)}
      className={`rounded-xl border-2 shadow-sm p-3 w-44 cursor-pointer hover:shadow-md transition-shadow ${bg} ${data.isFocal ? "ring-2 ring-offset-1 ring-indigo-500" : ""}`}
    >
      <Handle type="target" position={Position.Top} className="!bg-gray-400" />
      <div className="flex items-center gap-2">
        <div className="h-9 w-9 rounded-full overflow-hidden bg-white border border-gray-200 shrink-0">
          {data.profile_photo_url ? (
            <img src={data.profile_photo_url} alt={data.full_name} className="h-full w-full object-cover" />
          ) : (
            <div className="h-full w-full flex items-center justify-center text-gray-400">
              <User className="h-4 w-4" />
            </div>
          )}
        </div>
        <div className="min-w-0">
          <p className="text-xs font-semibold text-gray-900 leading-tight truncate">
            {data.full_name || "Unknown"}
          </p>
          {years && <p className="text-[10px] text-gray-500 mt-0.5">{years}</p>}
          {data.is_living && (
            <span className="inline-block text-[9px] font-medium text-green-700 bg-green-100 rounded-full px-1.5 py-0.5 mt-0.5">
              Living
            </span>
          )}
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-gray-400" />
    </div>
  );
}

export default memo(TreeNode);
