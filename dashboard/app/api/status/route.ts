import { NextResponse } from 'next/server'

const SERVICES = [
  { name: 'analyzer', url: process.env.ANALYZER_URL },
  { name: 'summarizer', url: process.env.SUMMARIZER_URL },
  { name: 'reporter', url: process.env.REPORTER_URL },
]

export async function GET() {
  try {
    const checks = await Promise.all(
      SERVICES.map(async (service) => {
        const start = Date.now()
        try {
          const res = await fetch(`${service.url}/healthz`, { 
            signal: AbortSignal.timeout(5000) 
          })
          const responseTime = Date.now() - start
          return {
            name: service.name,
            status: res.ok ? 'healthy' : 'degraded',
            url: service.url,
            response_time: responseTime,
            last_check: new Date().toISOString(),
          }
        } catch (error) {
          return {
            name: service.name,
            status: 'down',
            url: service.url,
            response_time: -1,
            last_check: new Date().toISOString(),
          }
        }
      })
    )

    return NextResponse.json({ services: checks })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to check service status' },
      { status: 500 }
    )
  }
}
