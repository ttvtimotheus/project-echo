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
