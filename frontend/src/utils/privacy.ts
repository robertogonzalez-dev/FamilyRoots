import type { User } from "../types/user";
import type { PersonSummary } from "../types/person";

export function canEdit(user: User | null): boolean {
  return user?.role === "admin" || user?.role === "editor";
}

export function isAdmin(user: User | null): boolean {
  return user?.role === "admin";
}

export function canViewLiving(user: User | null): boolean {
  return user?.role === "admin" || user?.role === "editor";
}

export function filterVisible(people: PersonSummary[], user: User | null): PersonSummary[] {
  if (!user) return people.filter((p) => !p.is_living);
  if (user.role === "admin" || user.role === "editor") return people;
  return people.filter((p) => !p.is_living);
}
