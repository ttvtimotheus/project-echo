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
