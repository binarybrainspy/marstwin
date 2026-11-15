import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './app/AppShell'
import { DataProvider } from './app/DataProvider'
import { CandidatePage } from './features/analogy/CandidatePage'
import { ScreenPage } from './features/map/ScreenPage'
import { MethodPage } from './features/method/MethodPage'
import { HomePage } from './features/usecase/HomePage'
import { ValidatePage } from './features/validation/ValidatePage'

export default function App() {
  return (
    <BrowserRouter>
      <DataProvider>
        <Routes>
          <Route element={<AppShell />}>
            <Route index element={<HomePage />} />
            <Route path="screen" element={<ScreenPage />} />
            <Route path="validate" element={<ValidatePage />} />
            <Route path="candidates/:id" element={<CandidatePage />} />
            <Route path="method" element={<MethodPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </DataProvider>
    </BrowserRouter>
  )
}
