import { useCallback, useEffect, useMemo, useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, type RelationKind, type Sex, type Tree, type TreeGraph } from '../api'
import { fullName, generations, lifespan } from '../layout'

const text = (f: FormData, key: string) => String(f.get(key) ?? '').trim() || null

export default function TreeView() {
  const treeId = Number(useParams().treeId)
  const [tree, setTree] = useState<Tree | null>(null)
  const [graph, setGraph] = useState<TreeGraph>({ people: [], relationships: [] })
  const [error, setError] = useState<string | null>(null)

  const reload = useCallback(() => api.graph(treeId).then(setGraph), [treeId])
  useEffect(() => {
    api.tree(treeId).then(setTree).catch((e: Error) => setError(e.message))
    reload().catch(() => {})
  }, [treeId, reload])

  const rows = useMemo(() => generations(graph.people, graph.relationships), [graph])
  const byId = useMemo(() => new Map(graph.people.map((p) => [p.id, p])), [graph])

  /** Wrap a form action: read its fields, call the API, refresh the graph, reset the form. */
  const onSubmit = (action: (f: FormData) => Promise<unknown>) => async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const form = e.currentTarget
    setError(null)
    try {
      await action(new FormData(form))
      await reload()
      form.reset()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed')
    }
  }

  const addPerson = onSubmit((f) =>
    api.createPerson(treeId, {
      given_name: text(f, 'given_name') ?? '',
      family_name: text(f, 'family_name'),
      sex: f.get('sex') as Sex,
      birth_date: text(f, 'birth_date'),
    }),
  )
  const linkPeople = onSubmit((f) =>
    api.link(treeId, Number(f.get('a')), Number(f.get('b')), f.get('kind') as RelationKind),
  )

  if (error && !tree) return <main><p className="error">{error}</p><Link to="/">← Back</Link></main>

  const personOptions = graph.people.map((p) => <option key={p.id} value={p.id}>{fullName(p)}</option>)

  return (
    <main>
      <Link to="/">← All trees</Link>
      <h1>{tree?.name ?? '…'}</h1>
      {error && <p className="error" role="alert">{error}</p>}

      <section className="tree" aria-label="Family tree">
        {rows.length === 0 && <p className="muted">Add the first person to start your tree.</p>}
        {rows.map((row, i) => (
          <div key={i} className="generation">
            {row.map((p) => (
              <article key={p.id} className={`person ${p.sex}`}>
                <strong>{fullName(p)}</strong>
                <span className="muted">{lifespan(p)}</span>
              </article>
            ))}
          </div>
        ))}
      </section>

      <div className="grid">
        <form className="card stack" onSubmit={addPerson}>
          <h2>Add person</h2>
          <input name="given_name" placeholder="Given name" required />
          <input name="family_name" placeholder="Family name" />
          <select name="sex" defaultValue="unknown">
            <option value="unknown">Sex: unknown</option>
            <option value="female">Female</option>
            <option value="male">Male</option>
          </select>
          <label>Born<input name="birth_date" type="date" /></label>
          <button>Add</button>
        </form>

        <form className="card stack" onSubmit={linkPeople}>
          <h2>Link people</h2>
          <select name="a" required>{personOptions}</select>
          <select name="kind">
            <option value="parent">is a parent of</option>
            <option value="spouse">is the spouse of</option>
          </select>
          <select name="b" required>{personOptions}</select>
          <button disabled={graph.people.length < 2}>Link</button>
          <ul className="muted small">
            {graph.relationships.map((r) => (
              <li key={r.id}>
                {fullName(byId.get(r.person_a_id)!)} {r.kind === 'parent' ? '→ parent of →' : '⚭'}{' '}
                {fullName(byId.get(r.person_b_id)!)}
              </li>
            ))}
          </ul>
        </form>
      </div>
    </main>
  )
}
