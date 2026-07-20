'use client'

import { useEffect, useMemo } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { IssueList } from '@/components/IssueList'
import { ReviewSummary } from '@/components/ReviewSummary'
import { useReview } from '@/hooks/useReview'
import type { Issue } from '@/types'

export default function DashboardPage() {
  const params = useParams()
  const reviewId = params.id as string
  const { review, isLoading, error, fetchReview, downloadReport } = useReview()

  useEffect(() => {
    if (reviewId) {
      void fetchReview(reviewId)
    }
  }, [reviewId, fetchReview])

  const issues = useMemo<Issue[]>(() => {
    if (!review) return []
    return review.files.flatMap((file) => file.issues)
  }, [review])

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-zinc-500">
        Loading review...
      </div>
    )
  }

  if (error || !review) {
    return (
      <div className="mx-auto max-w-xl px-4 py-16 text-center">
        <h1 className="text-2xl font-bold">Review not found</h1>
        <p className="mt-2 text-zinc-500">{error}</p>
        <Link href="/" className="mt-6 inline-block text-sm font-medium underline">
          Go home
        </Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <header className="mb-8 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Review Result</h1>
          <p className="text-sm text-zinc-500">Status: {review.status}</p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => void downloadReport(reviewId)}
            className="rounded-lg border border-zinc-300 bg-white px-4 py-2 text-sm"
          >
            Download Markdown
          </button>
          <Link
            href="/"
            className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white"
          >
            New Review
          </Link>
        </div>
      </header>

      <div className="space-y-8">
        <ReviewSummary review={review} />
        <section>
          <h2 className="mb-3 text-lg font-semibold">Issues</h2>
          <IssueList issues={issues} />
        </section>
      </div>
    </div>
  )
}
