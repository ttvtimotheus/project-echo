'use client'

import { AppBar, Toolbar, Typography, Box, Chip } from '@mui/material'
import { Analytics } from '@mui/icons-material'

export function Header() {
  return (
    <AppBar 
      position="sticky" 
      elevation={0} 
      sx={{ 
        backgroundColor: 'var(--md-sys-color-surface)',
        borderBottom: '1px solid var(--md-sys-color-outline-variant)'
      }}
    >
      <Toolbar sx={{ height: 64 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Analytics sx={{ fontSize: 28, color: 'var(--md-sys-color-primary)' }} />
          <Typography 
            variant="h6" 
            sx={{ 
              fontWeight: 500,
              letterSpacing: 0,
              color: 'var(--md-sys-color-on-surface)'
            }}
          >
            Project ECHO
          </Typography>
        </Box>
        <Box sx={{ flex: 1 }} />
        <Chip 
          label="LIVE" 
          size="small" 
          sx={{ 
            backgroundColor: '#1DB954',
            color: '#fff',
            fontWeight: 500,
            animation: 'pulse 2s infinite'
          }} 
        />
      </Toolbar>
    </AppBar>
  )
}
