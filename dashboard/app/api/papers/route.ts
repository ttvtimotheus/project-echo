import { NextResponse } from 'next/server'
import { db } from '@/lib/firebase-admin'
import type { Paper } from '@/types'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const limit = parseInt(searchParams.get('limit') || '50')
  const topic = searchParams.get('topic')

  try {
    // Fetch documents from Firestore using Admin SDK
    const [documentsSnap, analysesSnap, summariesSnap] = await Promise.all([
      db.collection('documents').get(),
      db.collection('analyses').get(),
      db.collection('summaries').get(),
    ])

    // Convert to maps for easy lookup
    const analysesMap = new Map()
    analysesSnap.docs.forEach(doc => {
      const data = doc.data()
      if (data.doc_id) {
        analysesMap.set(data.doc_id, data)
      }
    })

    const summariesMap = new Map()
    summariesSnap.docs.forEach(doc => {
      const data = doc.data()
      if (data.doc_id) {
        summariesMap.set(data.doc_id, data)
      }
    })

    // Combine data
    const papers: Paper[] = documentsSnap.docs.map(doc => {
      const docId = doc.id
      const data = doc.data()
      const analysis = analysesMap.get(docId)
      const summary = summariesMap.get(docId)

      return {
        id: docId,
        title: data.title || 'Untitled',
        link: data.link || '',
        summary: summary?.summary || data.summary || '',
        topics: analysis?.topics || [],
        score: analysis?.score || 0,
        timestamp: data.timestamp?.toDate().toISOString() || new Date().toISOString(),
        analyzed_at: analysis?.timestamp?.toDate().toISOString(),
        summarized_at: summary?.timestamp?.toDate().toISOString(),
      }
    })

    // Filter by topic if specified
    let filteredPapers = papers
    if (topic) {
      filteredPapers = papers.filter(p => p.topics.includes(topic))
    }

    // Sort by timestamp (newest first)
    filteredPapers.sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    )

    // Limit results
    const limitedPapers = filteredPapers.slice(0, limit)

    return NextResponse.json({
      papers: limitedPapers,
      total: filteredPapers.length,
    })

  } catch (error) {
    console.error('Error fetching papers:', error)
    return NextResponse.json(
      { error: 'Failed to fetch papers' },
      { status: 500 }
    )
  }
}
