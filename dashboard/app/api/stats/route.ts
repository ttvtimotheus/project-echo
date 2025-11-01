import { NextResponse } from 'next/server'
import { db } from '@/lib/firebase-admin'

export async function GET() {
  try {
    // Fetch counts from all collections
    const [documentsSnap, analysesSnap, summariesSnap, reportsSnap] = await Promise.all([
      db.collection('documents').count().get(),
      db.collection('analyses').count().get(),
      db.collection('summaries').count().get(),
      db.collection('reports').count().get(),
    ])

    const total_documents = documentsSnap.data().count
    const total_analyses = analysesSnap.data().count
    const total_summaries = summariesSnap.data().count
    const total_reports = reportsSnap.data().count

    const stats = {
      total_documents,
      total_analyses,
      total_summaries,
      total_reports,
      success_rate: total_documents > 0 
        ? ((total_summaries / total_documents) * 100).toFixed(1)
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
