import type {
  AnalogyCard,
  CoarseBundle,
  KnownAnalog,
  MethodDoc,
  TargetProfile,
  UseCase,
} from './types'

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(path)
  if (!res.ok) throw new Error(`Failed to load ${path}: ${res.status}`)
  return res.json() as Promise<T>
}

export async function loadAll() {
  const [usecases, targets, knownAnalogs, coarse, candidates, method] =
    await Promise.all([
      getJson<UseCase[]>('/data/usecases.json'),
      getJson<TargetProfile[]>('/data/targets.json'),
      getJson<KnownAnalog[]>('/data/known_analogs.json'),
      getJson<CoarseBundle>('/data/coarse_results.json'),
      getJson<AnalogyCard[]>('/data/candidates.json'),
      getJson<MethodDoc>('/data/method.json'),
    ])

  return {
    usecase: usecases[0],
    targets,
    knownAnalogs,
    coarse,
    candidates,
    method,
  }
}

export type AppData = Awaited<ReturnType<typeof loadAll>>
