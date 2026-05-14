'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { getAccessToken } from '@/lib/auth'

export default function SpecPage() {
  const router = useRouter()
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<{ session_id: string; rules_count: number } | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!getAccessToken()) {
      router.push('/login')
    }
  }, [router])

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    setError('')
    try {
      const { parseSpec } = await import('@/lib/api')
      const res = await parseSpec(file)
      setResult(res)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h1>Upload Spec Document</h1>
      {!result ? (
        <>
          <p>Upload a .docx specification document to extract rules.</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <input
              type="file"
              accept=".docx"
              onChange={e => setFile(e.target.files?.[0] ?? null)}
              style={{ padding: '8px' }}
            />
            <button onClick={handleUpload} disabled={!file || loading} style={{ padding: '8px' }}>
              {loading ? 'Uploading...' : 'Upload & Extract Rules'}
            </button>
          </div>
          {error && <div style={{ color: 'red', marginTop: '8px' }}>{error}</div>}
        </>
      ) : (
        <div style={{ marginTop: '20px' }}>
          <p><strong>Session ID:</strong> {result.session_id}</p>
          <p><strong>Rules extracted:</strong> {result.rules_count}</p>
          <button
            onClick={() => router.push(`/spec/${result.session_id}`)}
            style={{ marginTop: '16px', padding: '8px 16px' }}
          >
            Next: Upload Thesis
          </button>
        </div>
      )}
    </div>
  )
}