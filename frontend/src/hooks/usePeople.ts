import { useState, useCallback } from "react";
import { peopleService } from "../services/peopleService";
import type { PersonSummary } from "../types/person";

export function usePeople() {
  const [people, setPeople] = useState<PersonSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async (search?: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await peopleService.list(search);
      setPeople(data);
    } catch (e: any) {
      setError(e.response?.data?.detail ?? "Failed to load people");
    } finally {
      setLoading(false);
    }
  }, []);

  return { people, loading, error, fetch };
}
