export interface Paper {
  id: string
  title: string
  link: string
  summary: string
  topics: string[]
  score: number
  timestamp: string
  analyzed_at?: string
  summarized_at?: string
}

export interface PipelineMetrics {
  total_documents: number
  total_analyses: number
  total_summaries: number
  total_reports: number
  avg_processing_time: number
  success_rate: number
}

export interface ServiceStatus {
  name: string
  status: 'healthy' | 'degraded' | 'down'
  url: string
  last_check: string
  response_time: number
}

export interface TopicDistribution {
  topic: string
  count: number
  percentage: number
}

export interface Report {
  html: string
  generated_at: string
  paper_count: number
}
