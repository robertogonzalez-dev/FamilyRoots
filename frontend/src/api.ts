const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const TOKEN_KEY = 'familyroots.token'

export type Sex = 'female' | 'male' | 'unknown'
export type RelationKind = 'parent' | 'spouse'

export interface User { id: number; email: string; display_name: string }
export interface Tree { id: number; name: string; description: string | null }
export interface PersonInput {
  given_name: string
  family_name?: string | null
  sex?: Sex
  birth_date?: string | null
  birth_place?: string | null
  death_date?: string | null
  notes?: string | null
}
export interface Person extends PersonInput { id: number; sex: Sex }
export interface Relationship { id: number; person_a_id: number; person_b_id: number; kind: RelationKind }
export interface TreeGraph { people: Person[]; relationships: Relationship[] }

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export const token = {
  get: () => { try { return localStorage.getItem(TOKEN_KEY) } catch { return null } },
  set: (t: string | null) => {
    try { if (t) localStorage.setItem(TOKEN_KEY, t); else localStorage.removeItem(TOKEN_KEY) } catch { /* private mode */ }
  },
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  const t = token.get()
  if (t) headers.set('Authorization', `Bearer ${t}`)
  if (init.body && !(init.body instanceof URLSearchParams)) headers.set('Content-Type', 'application/json')

  const res = await fetch(`${BASE}${path}`, { ...init, headers })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    // FastAPI sends a string for HTTPException and a list of {loc, msg} for validation errors.
    const detail = typeof body.detail === 'string'
      ? body.detail
      : Array.isArray(body.detail)
        ? body.detail.map((d: { msg: string }) => d.msg).join('; ')
        : res.statusText
    throw new ApiError(res.status, detail)
  }
  return (res.status === 204 ? undefined : await res.json()) as T
}

const json = (method: string, body: unknown): RequestInit => ({ method, body: JSON.stringify(body) })

export const api = {
  register: (email: string, password: string, display_name: string) =>
    request<User>('/auth/register', json('POST', { email, password, display_name })),
  login: (email: string, password: string) =>
    request<{ access_token: string }>('/auth/login', {
      method: 'POST',
      body: new URLSearchParams({ username: email, password }),
    }),
  me: () => request<User>('/auth/me'),

  trees: () => request<Tree[]>('/trees'),
  createTree: (name: string, description?: string) => request<Tree>('/trees', json('POST', { name, description })),
  tree: (id: number) => request<Tree>(`/trees/${id}`),
  deleteTree: (id: number) => request<void>(`/trees/${id}`, { method: 'DELETE' }),
  graph: (id: number) => request<TreeGraph>(`/trees/${id}/graph`),

  createPerson: (treeId: number, p: PersonInput) => request<Person>(`/trees/${treeId}/people`, json('POST', p)),
  deletePerson: (treeId: number, pid: number) => request<void>(`/trees/${treeId}/people/${pid}`, { method: 'DELETE' }),
  link: (treeId: number, person_a_id: number, person_b_id: number, kind: RelationKind) =>
    request<Relationship>(`/trees/${treeId}/relationships`, json('POST', { person_a_id, person_b_id, kind })),
}
