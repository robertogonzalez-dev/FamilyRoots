import type { Person, Relationship } from './api'

/**
 * Assign each person a generation (0 = oldest known ancestors) so the tree can render as rows.
 * A child sits one row below its lowest parent; spouses are pulled onto the same row.
 */
export function generations(people: Person[], rels: Relationship[]): Person[][] {
  const parents = new Map<number, number[]>()
  for (const r of rels) {
    if (r.kind === 'parent') parents.set(r.person_b_id, [...(parents.get(r.person_b_id) ?? []), r.person_a_id])
  }

  const depth = new Map<number, number>()
  const visit = (id: number, stack: Set<number>): number => {
    const known = depth.get(id)
    if (known !== undefined) return known
    if (stack.has(id)) return 0 // defensive: the API already rejects cycles
    stack.add(id)
    const ps = parents.get(id) ?? []
    const d = ps.length ? Math.max(...ps.map((p) => visit(p, stack))) + 1 : 0
    depth.set(id, d)
    return d
  }
  people.forEach((p) => visit(p.id, new Set()))

  for (const r of rels) {
    if (r.kind !== 'spouse') continue
    const d = Math.max(depth.get(r.person_a_id) ?? 0, depth.get(r.person_b_id) ?? 0)
    depth.set(r.person_a_id, d)
    depth.set(r.person_b_id, d)
  }

  const rows: Person[][] = []
  for (const p of people) {
    const d = depth.get(p.id) ?? 0
    ;(rows[d] ??= []).push(p)
  }
  return rows.filter(Boolean)
}

export const fullName = (p: Pick<Person, 'given_name' | 'family_name'>) =>
  [p.given_name, p.family_name].filter(Boolean).join(' ')

export const lifespan = (p: Person) => {
  const year = (d?: string | null) => (d ? d.slice(0, 4) : '')
  return p.birth_date || p.death_date ? `${year(p.birth_date)}–${year(p.death_date)}` : ''
}
