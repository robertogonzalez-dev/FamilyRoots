import { useState, useCallback } from "react";
import { treeService } from "../services/treeService";
import type { Node, Edge } from "reactflow";

export function useTree() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await treeService.getTree();
      setNodes(data.nodes);
      setEdges(data.edges);
    } catch (e: any) {
      setError(e.response?.data?.detail ?? "Failed to load tree");
    } finally {
      setLoading(false);
    }
  }, []);

  return { nodes, edges, loading, error, fetch };
}
