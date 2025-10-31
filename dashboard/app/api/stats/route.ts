import { NextResponse } from 'next/server'

const GCP_PROJECT = process.env.GCP_PROJECT || 'echo-476821'
const FIRESTORE_API = `https://firestore.googleapis.com/v1/projects/${GCP_PROJECT}/databases/(default)/documents`

export async function GET() {
  try {
    // Fetch counts from all collections
    const [docsRes, analysesRes, summariesRes, reportsRes] = await Promise.all([
      fetch(`${FIRESTORE_API}/documents`),
      fetch(`${FIRESTORE_API}/analyses`),
      fetch(`${FIRESTORE_API}/summaries`),
      fetch(`${FIRESTORE_API}/reports`),
    ])

    const docsData = await docsRes.json()
    const analysesData = await analysesRes.json()
    const summariesData = await summariesRes.json()
    const reportsData = await reportsRes.json()

    const stats = {
      total_documents: docsData.documents?.length || 0,
      total_analyses: analysesData.documents?.length || 0,
      total_summaries: summariesData.documents?.length || 0,
      total_reports: reportsData.documents?.length || 0,
      success_rate: docsData.documents?.length > 0 
        ? ((summariesData.documents?.length || 0) / docsData.documents.length * 100).toFixed(1)
        : 0,
    }

    return NextResponse.json(stats)
  } catch (error) {
    console.error('Error fetching stats:', error)
    return NextResponse.json(
      { error: 'Failed to fetch stats' },
      { status: 500 }
    )
  }
}
