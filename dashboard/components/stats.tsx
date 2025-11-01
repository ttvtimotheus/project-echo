'use client'

import { Box, Card, CardContent, Typography, Grid, Skeleton } from '@mui/material'
import { 
  Description as DescriptionIcon,
  Psychology as PsychologyIcon, 
  Summarize as SummarizeIcon, 
  TrendingUp as TrendingUpIcon 
} from '@mui/icons-material'
import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then(r => r.json())

export function Stats() {
  const { data, isLoading } = useSWR('/api/stats', fetcher, {
    refreshInterval: 10000,
  })

  const stats = [
    { 
      label: 'Documents', 
      value: data?.total_documents || 0, 
      icon: DescriptionIcon, 
      color: '#1E88E5' 
    },
    { 
      label: 'Analyzed', 
      value: data?.total_analyses || 0, 
      icon: PsychologyIcon, 
      color: '#9C27B0' 
    },
    { 
      label: 'Summarized', 
      value: data?.total_summaries || 0, 
      icon: SummarizeIcon, 
      color: '#43A047' 
    },
    { 
      label: 'Success Rate', 
      value: `${data?.success_rate || 0}%`, 
      icon: TrendingUpIcon, 
      color: '#FFA726' 
    },
  ]

  return (
    <Grid container spacing={2}>
      {stats.map((stat) => {
        const Icon = stat.icon
        return (
          <Grid item xs={12} sm={6} md={3} key={stat.label}>
            <Card 
              sx={{ 
                backgroundColor: 'var(--md-sys-color-surface-container)',
                borderRadius: '12px',
                boxShadow: 'none',
                height: '100%'
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                  <Icon sx={{ fontSize: 24, color: stat.color }} />
                  <Box sx={{ flex: 1 }}>
                    <Typography 
                      variant="h4" 
                      sx={{ 
                        fontSize: 28,
                        fontWeight: 400,
                        lineHeight: 1,
                        color: 'var(--md-sys-color-on-surface)',
                        mb: 0.5
                      }}
                    >
                      {isLoading ? (
                        <Skeleton width={80} />
                      ) : (
                        stat.value
                      )}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: 'var(--md-sys-color-on-surface-variant)',
                        fontSize: 14,
                        letterSpacing: 0.1
                      }}
                    >
                      {stat.label}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )
      })}
    </Grid>
  )
}
