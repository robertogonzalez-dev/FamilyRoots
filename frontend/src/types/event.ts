export interface FamilyEvent {
  id: number;
  person_id: number;
  event_type?: string;
  event_date?: string;
  event_place?: string;
  description?: string;
  source_id?: number;
  created_at: string;
  updated_at: string;
}
