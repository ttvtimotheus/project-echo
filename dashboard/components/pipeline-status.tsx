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
