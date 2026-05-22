import { useEffect, useCallback, useState, useMemo, useRef } from "react";
import ReactFlow, {
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  ReactFlowProvider,
  useReactFlow,
  type Node,
  type Edge,
} from "reactflow";
import "reactflow/dist/style.css";
import { Search, X, ChevronUp, ChevronDown } from "lucide-react";
import { useTree } from "../hooks/useTree";
import TreeNode from "../components/TreeNode";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";
import { applyDagreLayout } from "../utils/treeLayout";
import { filterByFocus } from "../utils/focusFilter";

const nodeTypes = { personNode: TreeNode };

function DepthControl({
  label,
  icon,
  value,
  onChange,
}: {
  label: string;
  icon: React.ReactNode;
  value: number;
  onChange: (v: number) => void;
}) {
  return (
    <div className="flex items-center gap-1.5 text-gray-600">
      {icon}
      <span className="text-xs text-gray-500">{label}:</span>
      <button
        onClick={() => onChange(Math.max(0, value - 1))}
        className="w-5 h-5 rounded border border-gray-300 flex items-center justify-center hover:bg-gray-100 text-xs font-bold leading-none"
      >
        −
      </button>
      <span className="w-4 text-center text-sm font-semibold text-gray-800">
        {value}
      </span>
      <button
        onClick={() => onChange(Math.min(10, value + 1))}
        className="w-5 h-5 rounded border border-gray-300 flex items-center justify-center hover:bg-gray-100 text-xs font-bold leading-none"
      >
        +
      </button>
    </div>
  );
}

function FamilyTreeCanvas({
  rawNodes,
  rawEdges,
}: {
  rawNodes: Node[];
  rawEdges: Edge[];
}) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [focalId, setFocalId] = useState<string | null>(null);
  const [ancestorDepth, setAncestorDepth] = useState(3);
  const [descendantDepth, setDescendantDepth] = useState(2);
  const [search, setSearch] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);
  const { fitView } = useReactFlow();
  const searchRef = useRef<HTMLDivElement>(null);

  const searchResults = useMemo(() => {
    if (!search.trim()) return [];
    const q = search.toLowerCase();
    return rawNodes
      .filter((n) => (n.data.full_name as string)?.toLowerCase().includes(q))
      .slice(0, 8);
  }, [search, rawNodes]);

  useEffect(() => {
    if (rawNodes.length === 0) return;

    let visibleNodes = rawNodes;
    let visibleEdges = rawEdges;

    if (focalId) {
      const filtered = filterByFocus(rawNodes, rawEdges, focalId, {
        ancestorDepth,
        descendantDepth,
      });
      visibleNodes = filtered.nodes;
      visibleEdges = filtered.edges;
    }

    const { nodes: laid, edges: laidEdges } = applyDagreLayout(
      visibleNodes.map((n) => ({
        ...n,
        data: { ...n.data, isFocal: n.id === focalId },
      })),
      visibleEdges,
    );

    setNodes(laid);
    setEdges(laidEdges);
    const timer = setTimeout(() => fitView({ padding: 0.2, duration: 400 }), 50);
    return () => clearTimeout(timer);
  }, [rawNodes, rawEdges, focalId, ancestorDepth, descendantDepth, setNodes, setEdges, fitView]);

  const onConnect = useCallback(
    (connection: Connection) => setEdges((eds) => addEdge(connection, eds)),
    [setEdges],
  );

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as HTMLElement)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const focusPerson = (id: string, name: string) => {
    setFocalId(id);
    setSearch(name);
    setShowDropdown(false);
  };

  const clearFocus = () => {
    setFocalId(null);
    setSearch("");
    setShowDropdown(false);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Family Tree</h1>
          <p className="text-gray-500 text-sm">
            {focalId
              ? `Showing ${nodes.length} of ${rawNodes.length} people`
              : `${rawNodes.length} people · scroll to zoom · click to view profile`}
          </p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          {focalId && (
            <div className="flex items-center gap-4 bg-gray-50 border border-gray-200 rounded-lg px-3 py-1.5">
              <DepthControl
                label="Ancestors"
                icon={<ChevronUp className="h-3.5 w-3.5" />}
                value={ancestorDepth}
                onChange={setAncestorDepth}
              />
              <div className="w-px h-5 bg-gray-200" />
              <DepthControl
                label="Descendants"
                icon={<ChevronDown className="h-3.5 w-3.5" />}
                value={descendantDepth}
                onChange={setDescendantDepth}
              />
            </div>
          )}

          <div ref={searchRef} className="relative">
            <div className="flex items-center gap-1.5 border border-gray-300 rounded-lg px-3 py-1.5 bg-white shadow-sm w-64">
              <Search className="h-3.5 w-3.5 text-gray-400 shrink-0" />
              <input
                type="text"
                placeholder="Focus on a person…"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setShowDropdown(true);
                }}
                onFocus={() => setShowDropdown(true)}
                className="flex-1 text-sm outline-none bg-transparent"
              />
              {(search || focalId) && (
                <button
                  onClick={clearFocus}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              )}
            </div>

            {showDropdown && searchResults.length > 0 && (
              <div className="absolute top-full mt-1 left-0 w-full bg-white border border-gray-200 rounded-lg shadow-lg z-10 overflow-hidden">
                {searchResults.map((n) => (
                  <button
                    key={n.id}
                    onMouseDown={() =>
                      focusPerson(n.id, n.data.full_name as string)
                    }
                    className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center gap-2 border-b border-gray-50 last:border-0"
                  >
                    <span className="font-medium text-gray-900">
                      {n.data.full_name as string}
                    </span>
                    {n.data.birth_year && (
                      <span className="text-gray-400 text-xs ml-auto">
                        b. {n.data.birth_year as number}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <div
        className="rounded-xl border border-gray-200 overflow-hidden shadow-sm"
        style={{ height: "75vh" }}
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.05}
          maxZoom={2}
        >
          <Background color="#e5e7eb" gap={20} />
          <Controls />
        </ReactFlow>
      </div>

      <p className="text-xs text-gray-400">
        Blue edges = parent/child &nbsp;|&nbsp; Pink dashed edges = spouse
      </p>
    </div>
  );
}

export default function FamilyTree() {
  const { nodes: rawNodes, edges: rawEdges, loading, error, fetch } = useTree();

  useEffect(() => {
    fetch();
  }, [fetch]);

  if (loading) return <LoadingSpinner size="lg" className="py-24" />;
  if (error) return <ErrorMessage message={error} className="mt-8" />;

  return (
    <ReactFlowProvider>
      <FamilyTreeCanvas rawNodes={rawNodes} rawEdges={rawEdges} />
    </ReactFlowProvider>
  );
}
