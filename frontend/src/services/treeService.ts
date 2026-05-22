import api from "./api";
import type { Node, Edge } from "reactflow";

interface TreeData {
  nodes: Node[];
  edges: Edge[];
}

export const treeService = {
  async getTree(): Promise<TreeData> {
    const { data } = await api.get<TreeData>("/tree");
    return data;
  },
};
