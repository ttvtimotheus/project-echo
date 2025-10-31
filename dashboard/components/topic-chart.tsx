'use client'

import { Card, CardContent, Typography } from '@mui/material'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then(r => r.json())

const COLORS = ['#6750A4', '#625B71', '#7D5260', '#4A90E2', '#50C878', '#FFB347']

export function TopicChart() {
  const { data } = useSWR('/api/papers?limit=100', fetcher)
  
  const papers = data?.papers || []
  const topicCounts: Record<string, number> = {}
  
  papers.forEach((p: any) => {
    p.topics.forEach((t: string) => {
      topicCounts[t] = (topicCounts[t] || 0) + 1
    })
  })
  
  const chartData = Object.entries(topicCounts).map(([name, value]) => ({
    name,
    value
  }))

  return (
    <Card className="glass-dark">
      <CardContent>
        <Typography variant="h6" className="mb-4 font-bold">
          Topic Distribution
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={80}
              label
            >
              {chartData.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
