import { format, parseISO, isValid } from "date-fns";

export function formatDate(dateStr?: string | null): string {
  if (!dateStr) return "—";
  try {
    const d = parseISO(dateStr);
    return isValid(d) ? format(d, "MMMM d, yyyy") : dateStr;
  } catch {
    return dateStr;
  }
}

export function formatYear(dateStr?: string | null): string {
  if (!dateStr) return "";
  try {
    const d = parseISO(dateStr);
    return isValid(d) ? format(d, "yyyy") : "";
  } catch {
    return "";
  }
}

export function lifespan(birthDate?: string | null, deathDate?: string | null): string {
  const b = formatYear(birthDate);
  const d = formatYear(deathDate);
  if (!b && !d) return "";
  if (!d) return b ? `b. ${b}` : "";
  return `${b || "?"} – ${d}`;
}
