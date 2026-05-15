'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { getAccessToken } from '@/lib/auth'
import type { ValidationReportResponse } from '@/lib/types'

export default function ReportPage() {
  const router = useRouter()
  const params = useParams()
  const sessionId = params.sessionId as string
  const reportId = params.reportId as string
  const [report, setReport] = useState<ValidationReportResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [correcting, setCorrecting] = useState(false)
  const [correctionStatus, setCorrectionStatus] = useState('')

  useEffect(() => {
    if (!getAccessToken()) {
      router.push('/login')
      return
    }
    const fetchReport = async () => {
      try {
        const { getReport } = await import('@/lib/api')
        const data = await getReport(reportId)
        setReport(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch report')
      } finally {
        setLoading(false)
      }
    }
    fetchReport()
  }, [router, reportId])

  const handleDownloadCorrection = async () => {
    if (!report?.report_id) {
      setError('Report ID not available')
      return
    }
    setCorrecting(true)
    setError('')
    setCorrectionStatus('Creating correction job...')
    try {
      const { createCorrectionJob, getCorrectionJob, getCorrectionDownloadUrl } = await import('@/lib/api')

      // Step 1: Create correction job using report_id as document_id
      const job = await createCorrectionJob(report.report_id, [])

      setCorrectionStatus('Processing corrections...')

      // Step 2: Poll until completed
      let attempts = 0
      while (attempts < 60) {
        await new Promise(r => setTimeout(r, 2000))
        const status = await getCorrectionJob(job.job_id)

        if (status.status === 'completed') {
          setCorrectionStatus('Downloading...')
          // Step 3: Trigger download using fetch with auth header
          const downloadUrl = getCorrectionDownloadUrl(job.job_id)
          const token = localStorage.getItem('access_token')
          const response = await fetch(downloadUrl, {
            headers: { Authorization: `Bearer ${token}` },
          })
          if (!response.ok) throw new Error('Download failed')
          const blob = await response.blob()
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = 'corrected_document.docx'
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          URL.revokeObjectURL(url)
          setCorrectionStatus('')
          setCorrecting(false)
          return
        } else if (status.status === 'failed') {
          throw new Error(status.error_message || 'Correction failed')
        }

        attempts++
        setCorrectionStatus(`Processing... (${attempts * 2}s)`)
      }

      throw new Error('Correction timed out')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Correction failed')
      setCorrecting(false)
      setCorrectionStatus('')
    }
  }

  if (loading) return <div style={{ padding: '20px' }}>Loading...</div>
  if (error) return <div style={{ padding: '20px', color: 'red' }}>{error}</div>
  if (!report) return null

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Validation Report</h1>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', margin: '20px 0' }}>
        <div style={{ border: '1px solid #ccc', padding: '12px', borderRadius: '4px', textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{report.total_count}</div>
          <div>Total</div>
        </div>
        <div style={{ border: '1px solid #ccc', padding: '12px', borderRadius: '4px', textAlign: 'center', backgroundColor: '#fee' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'red' }}>{report.error_count}</div>
          <div>Errors</div>
        </div>
        <div style={{ border: '1px solid #ccc', padding: '12px', borderRadius: '4px', textAlign: 'center', backgroundColor: '#ffe' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'orange' }}>{report.warning_count}</div>
          <div>Warnings</div>
        </div>
        <div style={{ border: '1px solid #ccc', padding: '12px', borderRadius: '4px', textAlign: 'center', backgroundColor: '#efe' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'green' }}>{report.info_count}</div>
          <div>Info</div>
        </div>
      </div>

      {report.document_name && <p><strong>Document:</strong> {report.document_name}</p>}

      {/* Step 9: Correction download */}
      <div style={{ marginTop: '20px', padding: '16px', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
        <p style={{ marginBottom: '12px' }}>Found {report.total_count} violations. Generate a corrected document.</p>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={handleDownloadCorrection}
            disabled={correcting}
            style={{
              padding: '10px 20px',
              fontSize: '14px',
              backgroundColor: correcting ? '#ccc' : '#2563eb',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: correcting ? 'not-allowed' : 'pointer',
            }}
          >
            {correcting ? 'Generating...' : 'Generate Corrected Document'}
          </button>
          {correctionStatus && <span style={{ color: '#666' }}>{correctionStatus}</span>}
        </div>
        {error && <p style={{ color: 'red', marginTop: '8px' }}>{error}</p>}
      </div>

      <h2 style={{ marginTop: '24px' }}>Violations</h2>
      {report.violations.length === 0 ? (
        <p>No violations found.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {report.violations.map(v => (
            <div key={v.id} style={{ border: '1px solid #ddd', padding: '12px', borderRadius: '4px', backgroundColor: v.severity === 'error' ? '#fff5f5' : v.severity === 'warning' ? '#fffbf0' : '#f5fff5' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontWeight: 'bold', textTransform: 'uppercase', color: v.severity === 'error' ? 'red' : v.severity === 'warning' ? 'orange' : 'green' }}>
                  {v.severity}
                </span>
                <span style={{ color: '#666' }}>{v.category}</span>
              </div>
              <p style={{ margin: '4px 0' }}>{v.description}</p>
              {v.paragraph_index && <p style={{ margin: '4px 0', color: '#666' }}>Paragraph {v.paragraph_index}</p>}
              <div style={{ marginTop: '8px', padding: '8px', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
                <p style={{ margin: '2px 0' }}><strong>Original:</strong> {v.original_content}</p>
                <p style={{ margin: '2px 0' }}><strong>Suggested fix:</strong> {v.suggested_fix}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}