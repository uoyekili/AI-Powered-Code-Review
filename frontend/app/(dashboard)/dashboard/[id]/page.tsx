'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useReview } from '@/hooks/useReview'
import { ScoreCard } from '@/components/ScoreCard'
import { ScoreRadar, SeverityDistribution, IssuesByCategory } from '@/components/Charts'
import { RepositoryInfo } from '@/components/RepositoryInfo'
import { FileExplorer } from '@/components/FileExplorer'
import { IssueList } from '@/components/IssueList'
import { FileReview } from '@/types'
import { Button } from '@/components/ui/button'
import { Download, Home, ArrowLeft } from 'lucide-react'
import { motion } from 'framer-motion'
import Link from 'next/link'

export default function DashboardPage() {
  const router = useRouter()
  const params = useParams()
  const reviewId = params.id as string
  const [selectedFile, setSelectedFile] = useState<FileReview | null>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'files'>('overview')

  const { review, isLoading, fetchReview, downloadReport } = useReview()

  useEffect(() => {
    if (reviewId) {
      fetchReview(reviewId)
    }
  }, [reviewId, fetchReview])

  useEffect(() => {
    if (review && review.files.length > 0 && !selectedFile) {
      setSelectedFile(review.files[0])
    }
  }, [review, selectedFile])

  const handleDownload = async () => {
    await downloadReport(reviewId, 'markdown')
  }

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-border border-t-primary" />
          <p className="mt-4 text-muted-foreground">Loading review...</p>
        </div>
      </div>
    )
  }

  if (!review) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-foreground">Review not found</h2>
          <Link href="/" className="mt-4 inline-block">
            <Button>Go Home</Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/50 bg-background/95 sticky top-0 z-40 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.back()}
              className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              <span className="text-sm">Back</span>
            </button>
            <div className="h-6 w-px bg-border" />
            <h1 className="text-lg font-bold">
              {review.repository.owner}/{review.repository.name}
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleDownload} className="gap-2">
              <Download className="h-4 w-4" />
              Download Report
            </Button>
            <Link href="/">
              <Button variant="ghost" size="sm" className="gap-2">
                <Home className="h-4 w-4" />
                Home
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Repository Info */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <RepositoryInfo repository={review.repository} />
        </motion.div>

        {/* Scores Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mt-8"
        >
          <h2 className="text-2xl font-bold text-foreground">Code Review Scores</h2>
          <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <ScoreCard title="Overall Score" score={review.metrics.overallScore} delay={0} />
            <ScoreCard title="Security" score={review.metrics.securityScore} delay={0.1} />
            <ScoreCard title="Performance" score={review.metrics.performanceScore} delay={0.2} />
            <ScoreCard title="Maintainability" score={review.metrics.maintainabilityScore} delay={0.3} />
            <ScoreCard title="Code Quality" score={review.metrics.codeQualityScore} delay={0.4} />
            <ScoreCard title="Architecture" score={review.metrics.architectureScore} delay={0.5} />
          </div>
        </motion.div>

        {/* Charts Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-12 grid gap-8 lg:grid-cols-3"
        >
          <div className="rounded-lg border border-border bg-card p-6 lg:col-span-1">
            <h3 className="text-lg font-semibold text-foreground">Score Overview</h3>
            <div className="mt-4">
              <ScoreRadar metrics={review.metrics} />
            </div>
          </div>

          <div className="rounded-lg border border-border bg-card p-6">
            <h3 className="text-lg font-semibold text-foreground">Issue Severity</h3>
            <div className="mt-4">
              <SeverityDistribution issueSeverity={review.issueSeverity} />
            </div>
          </div>

          <div className="rounded-lg border border-border bg-card p-6">
            <h3 className="text-lg font-semibold text-foreground">Issues by Category</h3>
            <div className="mt-4">
              <IssuesByCategory issuesByCategory={review.issuesByCategory} />
            </div>
          </div>
        </motion.div>

        {/* Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-12"
        >
          <div className="flex gap-4 border-b border-border">
            {(['overview', 'files'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-3 font-medium transition-colors ${
                  activeTab === tab
                    ? 'border-b-2 border-primary text-primary'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {tab === 'overview' ? 'Overview' : 'File Reviews'}
              </button>
            ))}
          </div>

          <div className="mt-6">
            {activeTab === 'overview' ? (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground">Statistics</h3>
                  <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
                    {[
                      { label: 'Total Issues', value: Object.values(review.issuesByCategory).reduce((a, b) => a + b, 0) },
                      { label: 'Critical', value: review.issueSeverity.critical },
                      { label: 'High', value: review.issueSeverity.high },
                      { label: 'Files Reviewed', value: review.files.length },
                      { label: 'Average Score', value: Math.round(review.metrics.overallScore) },
                    ].map((stat) => (
                      <div key={stat.label} className="rounded-lg border border-border bg-card/50 p-4">
                        <p className="text-xs font-medium text-muted-foreground">{stat.label}</p>
                        <p className="mt-2 text-2xl font-bold text-foreground">{stat.value}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="grid gap-8 lg:grid-cols-3">
                <div className="lg:col-span-1">
                  <h3 className="text-lg font-semibold text-foreground">Files</h3>
                  <div className="mt-4">
                    <FileExplorer
                      files={review.files}
                      selectedFile={selectedFile || undefined}
                      onSelectFile={setSelectedFile}
                    />
                  </div>
                </div>

                {selectedFile && (
                  <div className="lg:col-span-2">
                    <div className="rounded-lg border border-border bg-card p-6">
                      <div className="mb-6 flex items-start justify-between">
                        <div>
                          <h3 className="text-lg font-semibold text-foreground">{selectedFile.name}</h3>
                          <p className="mt-1 text-sm text-muted-foreground">{selectedFile.path}</p>
                          <p className="mt-2 text-sm text-foreground">{selectedFile.lines} lines</p>
                        </div>
                        <div className="flex h-16 w-16 items-center justify-center rounded-lg bg-muted text-2xl font-bold text-foreground">
                          {selectedFile.score}
                        </div>
                      </div>

                      <p className="text-sm text-muted-foreground">{selectedFile.summary}</p>

                      <div className="mt-6">
                        <h4 className="font-semibold text-foreground">Issues</h4>
                        <div className="mt-4">
                          <IssueList issues={selectedFile.issues} />
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </motion.div>
      </main>
    </div>
  )
}
