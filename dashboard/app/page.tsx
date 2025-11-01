'use client'

import { useState } from 'react'
import { Hero } from '@/components/hero'
import { Stats } from '@/components/stats'
import { LiveFeed } from '@/components/live-feed'
import { TopicChart } from '@/components/topic-chart'
import { PipelineStatus } from '@/components/pipeline-status'
import { SearchBar } from '@/components/search-bar'
import { FilterPanel } from '@/components/filter-panel'
import { Header } from '@/components/header'

export default function Dashboard() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedTopics, setSelectedTopics] = useState<string[]>([])
  const [dateRange, setDateRange] = useState<{start: Date | null, end: Date | null}>({
    start: null,
    end: null
  })

  return (
    <main className="min-h-screen" style={{ background: 'var(--md-sys-color-background)' }}>
      <Header />
        
      <div className="max-w-screen-xl mx-auto px-4 py-6 space-y-6">
        {/* Stats Overview */}
        <Stats />

        {/* Search and Filter */}
        <div className="flex flex-col md:flex-row gap-4 items-start">
          <div className="flex-1">
            <SearchBar value={searchQuery} onChange={setSearchQuery} />
          </div>
          <FilterPanel
            selectedTopics={selectedTopics}
            onTopicsChange={setSelectedTopics}
            dateRange={dateRange}
            onDateRangeChange={setDateRange}
          />
        </div>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Live Feed - Takes 2 columns */}
          <div className="lg:col-span-2">
            <LiveFeed
              searchQuery={searchQuery}
              selectedTopics={selectedTopics}
              dateRange={dateRange}
            />
          </div>

          {/* Right Sidebar */}
          <div className="space-y-4">
            {/* Pipeline Status */}
            <PipelineStatus />

            {/* Topic Analytics */}
            <TopicChart />
          </div>
        </div>
      </div>
    </main>
  )
}
