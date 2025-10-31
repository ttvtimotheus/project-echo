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
