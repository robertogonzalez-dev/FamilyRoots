import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { api, type Tree } from '../api'

export default function Trees() {
  const [trees, setTrees] = useState<Tree[] | null>(null)
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.trees().then(setTrees).catch((e: Error) => setError(e.message))
  }, [])

  const create = async (e: FormEvent) => {
    e.preventDefault()
    const tree = await api.createTree(name)
    setTrees((t) => [...(t ?? []), tree])
    setName('')
  }

  return (
    <main>
      <h1>Your family trees</h1>
      {error && <p className="error">{error}</p>}
      {trees === null ? (
        <p className="muted">Loading…</p>
      ) : trees.length === 0 ? (
        <p className="muted">No trees yet. Start one below.</p>
      ) : (
        <ul className="grid">
          {trees.map((t) => (
            <li key={t.id} className="card">
              <Link to={`/trees/${t.id}`}><strong>{t.name}</strong></Link>
              {t.description && <p className="muted">{t.description}</p>}
            </li>
          ))}
        </ul>
      )}
      <form onSubmit={create} className="row">
        <input placeholder="e.g. Gonzalez family" value={name} onChange={(e) => setName(e.target.value)} required />
        <button>New tree</button>
      </form>
    </main>
  )
}
