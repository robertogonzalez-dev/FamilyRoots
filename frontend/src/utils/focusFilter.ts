import type { Node, Edge } from "reactflow";

export interface FocusOptions {
  ancestorDepth: number;
  descendantDepth: number;
}

export function filterByFocus(
  allNodes: Node[],
  allEdges: Edge[],
  focalId: string,
  { ancestorDepth, descendantDepth }: FocusOptions,
): { nodes: Node[]; edges: Edge[] } {
  // Build adjacency maps. Backend convention: source = parent, target = child.
  const parentsOf = new Map<string, string[]>();
  const childrenOf = new Map<string, string[]>();
  const spousesOf = new Map<string, string[]>();

  for (const edge of allEdges) {
    const rel: string | undefined = edge.data?.relationship_type;
    if (rel === "parent_child") {
      if (!parentsOf.has(edge.target)) parentsOf.set(edge.target, []);
      parentsOf.get(edge.target)!.push(edge.source);
      if (!childrenOf.has(edge.source)) childrenOf.set(edge.source, []);
      childrenOf.get(edge.source)!.push(edge.target);
    } else if (rel === "spouse") {
      if (!spousesOf.has(edge.source)) spousesOf.set(edge.source, []);
      spousesOf.get(edge.source)!.push(edge.target);
      if (!spousesOf.has(edge.target)) spousesOf.set(edge.target, []);
      spousesOf.get(edge.target)!.push(edge.source);
    }
  }

  const included = new Set<string>([focalId]);

  // BFS upward through ancestors
  let frontier = [focalId];
  for (let i = 0; i < ancestorDepth; i++) {
    const next: string[] = [];
    for (const id of frontier) {
      for (const parentId of parentsOf.get(id) ?? []) {
        if (!included.has(parentId)) {
          included.add(parentId);
          next.push(parentId);
        }
      }
    }
    frontier = next;
  }

  // BFS downward through descendants
  frontier = [focalId];
  for (let i = 0; i < descendantDepth; i++) {
    const next: string[] = [];
    for (const id of frontier) {
      for (const childId of childrenOf.get(id) ?? []) {
        if (!included.has(childId)) {
          included.add(childId);
          next.push(childId);
        }
      }
    }
    frontier = next;
  }

  // Pull in spouses of every included node so couples are never split
  for (const id of [...included]) {
    for (const spouseId of spousesOf.get(id) ?? []) {
      included.add(spouseId);
    }
  }

  return {
    nodes: allNodes.filter((n) => included.has(n.id)),
    edges: allEdges.filter((e) => included.has(e.source) && included.has(e.target)),
  };
}
