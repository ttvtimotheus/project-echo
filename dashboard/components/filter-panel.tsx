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
