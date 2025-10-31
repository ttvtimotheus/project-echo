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
