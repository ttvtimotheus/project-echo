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
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
      {/* Background effects */}
      <div className="fixed inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]" />
      <div className="fixed inset-0 flex items-center justify-center">
        <div className="h-[40rem] w-[40rem] animate-pulse-slow rounded-full bg-primary-500/20 blur-3xl" />
      </div>

      {/* Content */}
      <div className="relative">
        <Header />
        
        <div className="container mx-auto px-4 py-8 space-y-8">
          {/* Hero Section */}
          <Hero />

          {/* Stats Overview */}
          <Stats />

          {/* Search and Filter */}
          <div className="flex flex-col lg:flex-row gap-4">
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
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Live Feed - Takes 2 columns */}
            <div className="lg:col-span-2">
              <LiveFeed
                searchQuery={searchQuery}
                selectedTopics={selectedTopics}
                dateRange={dateRange}
              />
            </div>

            {/* Right Sidebar */}
            <div className="space-y-6">
              {/* Pipeline Status */}
              <PipelineStatus />

              {/* Topic Analytics */}
              <TopicChart />
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
