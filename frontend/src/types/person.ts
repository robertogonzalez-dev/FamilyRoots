export type Gender = "male" | "female" | "unknown" | "other";

export interface Person {
  id: number;
  external_id?: string;
  first_name?: string;
  middle_name?: string;
  last_name?: string;
  maiden_name?: string;
  gender: Gender;
  birth_date?: string;
  birth_place?: string;
  death_date?: string;
  death_place?: string;
  biography?: string;
  is_living: boolean;
  profile_photo_url?: string;
  full_name: string;
  created_at: string;
  updated_at: string;
}

export interface PersonSummary {
  id: number;
  full_name: string;
  birth_date?: string;
  death_date?: string;
  gender: Gender;
  is_living: boolean;
  profile_photo_url?: string;
}

export interface PersonCreate {
  first_name?: string;
  middle_name?: string;
  last_name?: string;
  maiden_name?: string;
  gender?: Gender;
  birth_date?: string;
  birth_place?: string;
  death_date?: string;
  death_place?: string;
  biography?: string;
  is_living?: boolean;
}

export interface PersonUpdate extends Partial<PersonCreate> {}

export interface RelativesSummary {
  parents: PersonSummary[];
  children: PersonSummary[];
  spouses: PersonSummary[];
  siblings: PersonSummary[];
}
