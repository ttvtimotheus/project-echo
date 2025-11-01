'use client'

import { Box, Card, CardContent, Typography, Chip, Link, CircularProgress, Paper } from '@mui/material'
import { OpenInNew as OpenInNewIcon } from '@mui/icons-material'
import useSWR from 'swr'
import type { Paper as PaperType } from '@/types'

const fetcher = (url: string) => fetch(url).then(r => r.json())

interface Props {
  searchQuery: string
  selectedTopics: string[]
  dateRange: { start: Date | null, end: Date | null }
}

export function LiveFeed({ searchQuery, selectedTopics }: Props) {
  const { data, isLoading } = useSWR<{papers: PaperType[]}>('/api/papers?limit=20', fetcher, {
    refreshInterval: 10000,
  })

  const papers = data?.papers || []
  
  const filtered = papers.filter(p => {
    if (searchQuery && !p.title.toLowerCase().includes(searchQuery.toLowerCase())) return false
    if (selectedTopics.length > 0 && !p.topics.some(t => selectedTopics.includes(t))) return false
    return true
  })

  return (
    <Card 
      sx={{ 
        backgroundColor: 'var(--md-sys-color-surface-container)',
        borderRadius: '12px',
        boxShadow: 'none'
      }}
    >
      <CardContent>
        <Typography 
          variant="h6" 
          sx={{ 
            mb: 3,
            fontSize: 20,
            fontWeight: 500,
            color: 'var(--md-sys-color-on-surface)'
          }}
        >
          Research Feed
        </Typography>
        
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={32} />
          </Box>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, maxHeight: 600, overflowY: 'auto' }}>
            {filtered.map((paper) => (
              <Paper
                key={paper.id}
                sx={{
                  p: 2,
                  backgroundColor: 'var(--md-sys-color-surface)',
                  borderRadius: '8px',
                  '&:hover': {
                    backgroundColor: 'var(--md-sys-color-surface-container-high)',
                  },
                  cursor: 'pointer'
                }}
              >
                <Link 
                  href={paper.link} 
                  target="_blank" 
                  underline="none"
                  sx={{ 
                    display: 'flex', 
                    gap: 2,
                    color: 'inherit'
                  }}
                >
                  <Box sx={{ flex: 1 }}>
                    <Typography 
                      variant="subtitle1" 
                      sx={{ 
                        fontWeight: 500,
                        color: 'var(--md-sys-color-primary)',
                        mb: 1
                      }}
                    >
                      {paper.title}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: 'var(--md-sys-color-on-surface-variant)',
                        mb: 2,
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden'
                      }}
                    >
                      {paper.summary}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {paper.topics.map(topic => (
                        <Chip 
                          key={topic} 
                          label={topic} 
                          size="small" 
                          sx={{
                            backgroundColor: 'var(--md-sys-color-primary-container)',
                            color: 'var(--md-sys-color-on-primary-container)',
                            fontWeight: 500,
                            fontSize: 12
                          }}
                        />
                      ))}
                    </Box>
                  </Box>
                  <OpenInNewIcon sx={{ fontSize: 18, color: 'var(--md-sys-color-on-surface-variant)' }} />
                </Link>
              </Paper>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  )
}
