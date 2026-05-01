/** @jsxImportSource react */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { ReactNode } from 'react'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      retry: 3,
      refetchOnWindowFocus: false,
    },
  },
})

function App(): ReactNode {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/documents" replace />} />
          <Route path="/login" element={<div>Login Page (TBD)</div>} />
          <Route path="/register" element={<div>Register Page (TBD)</div>} />
          <Route path="/documents" element={<div>Documents Page (TBD)</div>} />
          <Route path="/documents/upload" element={<div>Upload Page (TBD)</div>} />
          <Route path="/templates" element={<div>Templates Page (TBD)</div>} />
          <Route path="*" element={<div>Not Found</div>} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App