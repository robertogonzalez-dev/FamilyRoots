import dagre from "dagre";
import type { Node, Edge } from "reactflow";

const NODE_WIDTH = 176; // matches w-44 (11rem)
const NODE_HEIGHT = 100;

export function applyDagreLayout(nodes: Node[], edges: Edge[]): { nodes: Node[]; edges: Edge[] } {
  if (nodes.length === 0) return { nodes, edges };

  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({
    rankdir: "TB",
    ranksep: 80,
    nodesep: 40,
    edgesep: 20,
    marginx: 20,
    marginy: 20,
  });

  for (const node of nodes) {
    g.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT });
  }

  for (const edge of edges) {
    // Spouse edges must not add vertical separation — keep them at the same rank
    if (edge.data?.relationship_type === "spouse") {
      g.setEdge(edge.source, edge.target, { minlen: 0, weight: 0 });
    } else {
      g.setEdge(edge.source, edge.target);
    }
  }

  dagre.layout(g);

  const positioned = nodes.map((node) => {
    const { x, y } = g.node(node.id);
    return {
      ...node,
      position: {
        x: x - NODE_WIDTH / 2,
        y: y - NODE_HEIGHT / 2,
      },
    };
  });

  return { nodes: positioned, edges };
}
