import { NextResponse } from 'next/server'
import type { Paper } from '@/types'

const GCP_PROJECT = process.env.GCP_PROJECT || 'echo-476821'
const FIRESTORE_API = `https://firestore.googleapis.com/v1/projects/${GCP_PROJECT}/databases/(default)/documents`

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const limit = parseInt(searchParams.get('limit') || '50')
  const topic = searchParams.get('topic')

  try {
    // Fetch documents from Firestore
    const docsResponse = await fetch(`${FIRESTORE_API}/documents`, {
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!docsResponse.ok) {
      throw new Error('Failed to fetch documents')
    }

    const docsData = await docsResponse.json()
    
    // Fetch analyses
    const analysesResponse = await fetch(`${FIRESTORE_API}/analyses`, {
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const analysesData = analysesResponse.ok ? await analysesResponse.json() : { documents: [] }

    // Fetch summaries
    const summariesResponse = await fetch(`${FIRESTORE_API}/summaries`, {
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const summariesData = summariesResponse.ok ? await summariesResponse.json() : { documents: [] }

    // Combine data
    const papers: Paper[] = (docsData.documents || []).map((doc: any) => {
      const docId = doc.name.split('/').pop()
      const fields = doc.fields

      // Find corresponding analysis
      const analysis = (analysesData.documents || []).find((a: any) => 
        a.fields?.doc_id?.stringValue === docId
      )

      // Find corresponding summary
      const summary = (summariesData.documents || []).find((s: any) => 
        s.fields?.doc_id?.stringValue === docId
      )

      return {
        id: docId,
        title: fields?.title?.stringValue || 'Untitled',
        link: fields?.link?.stringValue || '',
        summary: summary?.fields?.summary?.stringValue || fields?.summary?.stringValue || '',
        topics: analysis?.fields?.topics?.arrayValue?.values?.map((v: any) => v.stringValue) || [],
        score: analysis?.fields?.score?.doubleValue || 0,
        timestamp: fields?.timestamp?.timestampValue || new Date().toISOString(),
        analyzed_at: analysis?.fields?.timestamp?.timestampValue,
        summarized_at: summary?.fields?.timestamp?.timestampValue,
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
