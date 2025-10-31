#!/bin/bash

# Generate all dashboard components for Project ECHO
echo "Generating ECHO Dashboard components..."

# Create components directory
mkdir -p components lib

# Theme Provider
cat > components/theme-provider.tsx << 'EOF'
'use client'

import { ThemeProvider as MuiThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#6750A4',
    },
    secondary: {
      main: '#625B71',
    },
    background: {
      default: '#0a0a0a',
      paper: '#1C1B1F',
    },
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif',
  },
})

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return (
    <MuiThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </MuiThemeProvider>
  )
}
EOF

# Header Component
cat > components/header.tsx << 'EOF'
'use client'

import { AppBar, Toolbar, Typography, Box, Chip } from '@mui/material'
import { Sparkles } from 'lucide-react'

export function Header() {
  return (
    <AppBar position="sticky" className="glass-dark">
      <Toolbar>
        <Box className="flex items-center gap-3">
          <Sparkles className="w-8 h-8 text-primary-500" />
          <Typography variant="h5" className="font-bold bg-gradient-to-r from-primary-300 to-primary-500 bg-clip-text text-transparent">
            ECHO
          </Typography>
        </Box>
        <Box className="flex-1" />
        <Chip label="LIVE" color="success" size="small" className="animate-pulse" />
      </Toolbar>
    </AppBar>
  )
}
EOF

# Hero Component
cat > components/hero.tsx << 'EOF'
'use client'

import { Box, Typography } from '@mui/material'
import { motion } from 'framer-motion'

export function Hero() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Box className="text-center py-12">
        <Typography variant="h2" className="font-bold mb-4 bg-gradient-to-r from-primary-200 via-primary-400 to-secondary-400 bg-clip-text text-transparent">
          AI Research Intelligence
        </Typography>
        <Typography variant="h6" className="text-gray-400 max-w-2xl mx-auto">
          Autonomous pipeline analyzing academic papers in real-time with GPU-accelerated AI
        </Typography>
      </Box>
    </motion.div>
  )
}
EOF

# Stats Component
cat > components/stats.tsx << 'EOF'
'use client'

import { Box, Card, CardContent, Typography, Grid } from '@mui/material'
import { FileText, Brain, FileCheck, TrendingUp } from 'lucide-react'
import useSWR from 'swr'
import { motion } from 'framer-motion'

const fetcher = (url: string) => fetch(url).then(r => r.json())

export function Stats() {
  const { data, isLoading } = useSWR('/api/stats', fetcher, {
    refreshInterval: 5000,
  })

  const stats = [
    { label: 'Documents', value: data?.total_documents || 0, icon: FileText, color: 'text-blue-400' },
    { label: 'Analyzed', value: data?.total_analyses || 0, icon: Brain, color: 'text-purple-400' },
    { label: 'Summarized', value: data?.total_summaries || 0, icon: FileCheck, color: 'text-green-400' },
    { label: 'Success Rate', value: `${data?.success_rate || 0}%`, icon: TrendingUp, color: 'text-yellow-400' },
  ]

  return (
    <Grid container spacing={3}>
      {stats.map((stat, i) => (
        <Grid item xs={12} sm={6} md={3} key={stat.label}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <Card className="glass hover:scale-105 transition-transform cursor-pointer">
              <CardContent>
                <Box className="flex items-center justify-between mb-2">
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                  <Typography variant="h4" className="font-bold">
                    {isLoading ? '...' : stat.value}
                  </Typography>
                </Box>
                <Typography variant="body2" className="text-gray-400">
                  {stat.label}
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      ))}
    </Grid>
  )
}
EOF

# Live Feed Component
cat > components/live-feed.tsx << 'EOF'
'use client'

import { Box, Card, CardContent, Typography, Chip, Link } from '@mui/material'
import { ExternalLink } from 'lucide-react'
import useSWR from 'swr'
import { motion } from 'framer-motion'
import type { Paper } from '@/types'

const fetcher = (url: string) => fetch(url).then(r => r.json())

interface Props {
  searchQuery: string
  selectedTopics: string[]
  dateRange: { start: Date | null, end: Date | null }
}

export function LiveFeed({ searchQuery, selectedTopics }: Props) {
  const { data, isLoading } = useSWR<{papers: Paper[]}>('/api/papers?limit=20', fetcher, {
    refreshInterval: 10000,
  })

  const papers = data?.papers || []
  
  const filtered = papers.filter(p => {
    if (searchQuery && !p.title.toLowerCase().includes(searchQuery.toLowerCase())) return false
    if (selectedTopics.length > 0 && !p.topics.some(t => selectedTopics.includes(t))) return false
    return true
  })

  return (
    <Card className="glass-dark">
      <CardContent>
        <Typography variant="h6" className="mb-4 font-bold">
          Live Research Feed
        </Typography>
        <Box className="space-y-4 max-h-[600px] overflow-y-auto">
          {isLoading && <Typography>Loading...</Typography>}
          {filtered.map((paper, i) => (
            <motion.div
              key={paper.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Card className="glass hover:bg-white/10 transition-colors">
                <CardContent>
                  <Link href={paper.link} target="_blank" className="flex items-start gap-2 no-underline">
                    <Box className="flex-1">
                      <Typography variant="subtitle1" className="font-semibold text-primary-300">
                        {paper.title}
                      </Typography>
                      <Typography variant="body2" className="text-gray-400 my-2 line-clamp-2">
                        {paper.summary}
                      </Typography>
                      <Box className="flex gap-2 flex-wrap">
                        {paper.topics.map(topic => (
                          <Chip key={topic} label={topic} size="small" className="bg-primary-900/50" />
                        ))}
                      </Box>
                    </Box>
                    <ExternalLink className="w-4 h-4 text-gray-500" />
                  </Link>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </Box>
      </CardContent>
    </Card>
  )
}
EOF

# Search Bar Component
cat > components/search-bar.tsx << 'EOF'
'use client'

import { TextField, InputAdornment } from '@mui/material'
import { Search } from 'lucide-react'

interface Props {
  value: string
  onChange: (value: string) => void
}

export function SearchBar({ value, onChange }: Props) {
  return (
    <TextField
      fullWidth
      placeholder="Search papers..."
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="glass"
      InputProps={{
        startAdornment: (
          <InputAdornment position="start">
            <Search className="w-5 h-5 text-gray-400" />
          </InputAdornment>
        ),
      }}
    />
  )
}
EOF

# Filter Panel Component
cat > components/filter-panel.tsx << 'EOF'
'use client'

import { Box, Chip, Typography } from '@mui/material'

const TOPICS = ['machine learning', 'nlp', 'computer vision', 'systems', 'theory', 'robotics']

interface Props {
  selectedTopics: string[]
  onTopicsChange: (topics: string[]) => void
  dateRange: { start: Date | null, end: Date | null }
  onDateRangeChange: (range: { start: Date | null, end: Date | null }) => void
}

export function FilterPanel({ selectedTopics, onTopicsChange }: Props) {
  const toggleTopic = (topic: string) => {
    if (selectedTopics.includes(topic)) {
      onTopicsChange(selectedTopics.filter(t => t !== topic))
    } else {
      onTopicsChange([...selectedTopics, topic])
    }
  }

  return (
    <Box className="glass p-4 rounded-lg">
      <Typography variant="subtitle2" className="mb-2 text-gray-400">
        Filter by Topic
      </Typography>
      <Box className="flex gap-2 flex-wrap">
        {TOPICS.map(topic => (
          <Chip
            key={topic}
            label={topic}
            onClick={() => toggleTopic(topic)}
            color={selectedTopics.includes(topic) ? 'primary' : 'default'}
            className="cursor-pointer"
          />
        ))}
      </Box>
    </Box>
  )
}
EOF

# Topic Chart Component
cat > components/topic-chart.tsx << 'EOF'
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
EOF

# Pipeline Status Component
cat > components/pipeline-status.tsx << 'EOF'
'use client'

import { Card, CardContent, Typography, Box, Chip } from '@mui/material'
import { CheckCircle, AlertCircle, XCircle } from 'lucide-react'

const services = [
  { name: 'Analyzer', status: 'healthy' as const },
  { name: 'Summarizer', status: 'healthy' as const },
  { name: 'Reporter', status: 'healthy' as const },
  { name: 'Crawler', status: 'healthy' as const },
]

const StatusIcon = ({ status }: { status: string }) => {
  if (status === 'healthy') return <CheckCircle className="w-5 h-5 text-green-400" />
  if (status === 'degraded') return <AlertCircle className="w-5 h-5 text-yellow-400" />
  return <XCircle className="w-5 h-5 text-red-400" />
}

export function PipelineStatus() {
  return (
    <Card className="glass-dark">
      <CardContent>
        <Typography variant="h6" className="mb-4 font-bold">
          Pipeline Status
        </Typography>
        <Box className="space-y-3">
          {services.map(service => (
            <Box key={service.name} className="flex items-center justify-between p-3 glass rounded-lg">
              <Box className="flex items-center gap-2">
                <StatusIcon status={service.status} />
                <Typography variant="body2">{service.name}</Typography>
              </Box>
              <Chip 
                label={service.status} 
                size="small" 
                color={service.status === 'healthy' ? 'success' : 'warning'}
              />
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  )
}
EOF

# Status API Route
cat > app/api/status/route.ts << 'EOF'
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
EOF

# Utility functions
cat > lib/utils.ts << 'EOF'
export function formatDate(date: string | Date) {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export function formatRelativeTime(date: string | Date) {
  const now = new Date()
  const then = new Date(date)
  const seconds = Math.floor((now.getTime() - then.getTime()) / 1000)

  if (seconds < 60) return 'just now'
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
  return `${Math.floor(seconds / 86400)}d ago`
}

export function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ')
}
EOF

# Environment template
cat > .env.example << 'EOF'
REPORTER_URL=https://reporter-cfskbkrt4a-ez.a.run.app
ANALYZER_URL=https://analyzer-cfskbkrt4a-ez.a.run.app
SUMMARIZER_URL=https://summarizer-cfskbkrt4a-ez.a.run.app
GCP_PROJECT=echo-476821
EOF

echo "✅ All components generated!"
echo ""
echo "Next steps:"
echo "1. npm install"
echo "2. cp .env.example .env.local"
echo "3. npm run dev"
EOF

chmod +x generate-components.sh

echo "✅ Component generation script created!"
echo ""
echo "Run: cd dashboard && ./generate-components.sh"
