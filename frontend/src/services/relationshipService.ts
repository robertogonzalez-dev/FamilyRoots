import api from "./api";
import type { Relationship, RelationshipCreate } from "../types/relationship";

export const relationshipService = {
  async list(): Promise<Relationship[]> {
    const { data } = await api.get<Relationship[]>("/relationships");
    return data;
  },

  async create(rel: RelationshipCreate): Promise<Relationship> {
    const { data } = await api.post<Relationship>("/relationships", rel);
    return data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/relationships/${id}`);
  },
};
