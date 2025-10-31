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
