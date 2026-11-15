import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'
import { loadAll, type AppData } from '../shared/loadData'

const DataContext = createContext<AppData | null>(null)

export function DataProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<AppData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadAll()
      .then(setData)
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : 'Failed to load data'),
      )
  }, [])

  if (error) {
    return (
      <div className="state-block">
        <h1>Data load failed</h1>
        <p>{error}</p>
        <p className="muted">
          Run <code>python science/scripts/run_pipeline.py</code> then refresh.
        </p>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="state-block">
        <p>Loading MarsTwin data…</p>
      </div>
    )
  }

  return <DataContext.Provider value={data}>{children}</DataContext.Provider>
}

export function useAppData() {
  const ctx = useContext(DataContext)
  if (!ctx) throw new Error('useAppData must be used inside DataProvider')
  return ctx
}
