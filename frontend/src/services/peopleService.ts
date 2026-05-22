import api from "./api";
import type { Person, PersonSummary, PersonCreate, PersonUpdate, RelativesSummary } from "../types/person";

export const peopleService = {
  async list(search?: string): Promise<PersonSummary[]> {
    const { data } = await api.get<PersonSummary[]>("/people", {
      params: search ? { search } : {},
    });
    return data;
  },

  async get(id: number): Promise<Person> {
    const { data } = await api.get<Person>(`/people/${id}`);
    return data;
  },

  async create(person: PersonCreate): Promise<Person> {
    const { data } = await api.post<Person>("/people", person);
    return data;
  },

  async update(id: number, person: PersonUpdate): Promise<Person> {
    const { data } = await api.patch<Person>(`/people/${id}`, person);
    return data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/people/${id}`);
  },

  async getRelatives(id: number): Promise<RelativesSummary> {
    const { data } = await api.get<RelativesSummary>(`/people/${id}/relatives`);
    return data;
  },
};
