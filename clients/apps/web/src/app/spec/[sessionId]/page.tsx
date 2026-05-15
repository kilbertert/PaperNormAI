'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { getAccessToken } from '@/lib/auth'

export default function ThesisPage() {
  const router = useRouter()
  const params = useParams()
  const sessionId = params.sessionId as string
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [reportId, setReportId] = useState<string | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!getAccessToken()) {
      router.push('/login')
    }
  }, [router])

  const handleValidate = async () => {
    if (!file) return
    setLoading(true)
    setError('')
    try {
      const { validateWithSpec } = await import('@/lib/api')
      const res = await validateWithSpec(file, sessionId)
      setReportId(res.report_id)
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Validation failed'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h1>Upload Thesis</h1>
      <p><strong>Session ID:</strong> {sessionId}</p>
      {!reportId ? (
        <>
          <p>Upload a .docx thesis document for validation.</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px' }}>
            <input
              type="file"
              accept=".docx"
              onChange={e => setFile(e.target.files?.[0] ?? null)}
              style={{ padding: '8px' }}
            />
            <button onClick={handleValidate} disabled={!file || loading} style={{ padding: '8px' }}>
              {loading ? 'Validating...' : 'Upload & Validate'}
            </button>
          </div>
          {error && <div style={{ color: 'red', marginTop: '8px' }}>{error}</div>}
        </>
      ) : (
        <div style={{ marginTop: '20px' }}>
          <p><strong>Report ID:</strong> {reportId}</p>
          <button
            onClick={() => router.push(`/spec/${sessionId}/report/${reportId}`)}
            style={{ marginTop: '16px', padding: '8px 16px' }}
          >
            View Report
          </button>
        </div>
      )}
    </div>
  )
}