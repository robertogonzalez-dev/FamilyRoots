import axios from "axios";

/**
 * Turn an API error into a readable message. FastAPI sends a string `detail` for
 * HTTPException and a list of `{ msg }` objects for request validation errors.
 */
export function apiErrorMessage(err: unknown, fallback: string): string {
  if (axios.isAxiosError(err)) {
    const detail = err.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail.map((d: { msg: string }) => d.msg).join("; ");
  }
  return fallback;
}
