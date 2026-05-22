export type RelationshipType =
  | "parent_child"
  | "spouse"
  | "sibling"
  | "adopted_child"
  | "step_parent";

export interface Relationship {
  id: number;
  person1_id: number;
  person2_id: number;
  relationship_type: RelationshipType;
  start_date?: string;
  end_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface RelationshipCreate {
  person1_id: number;
  person2_id: number;
  relationship_type: RelationshipType;
  start_date?: string;
  end_date?: string;
  notes?: string;
}
