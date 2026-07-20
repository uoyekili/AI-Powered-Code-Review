'use client'

import { useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ProgressTracker } from '@/components/ProgressTracker'
import { useReview } from '@/hooks/useReview'

export default function LoadingPage() {
  const router = useRouter()
  const params = useParams()
  const reviewId = params.id as string
  const { progress, steps, currentStep, pollProgress, review, error } = useReview()

  useEffect(() => {
    if (!reviewId) return
    pollProgress(reviewId, 2000)
  }, [reviewId, pollProgress])

  useEffect(() => {
    if (review && (review.status === 'completed' || progress >= 100)) {
      router.push(`/dashboard/${reviewId}`)
    }
  }, [review, progress, reviewId, router])

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold">Analyzing Repository</h1>
        <p className="mt-2 text-zinc-500">{currentStep || 'Initializing analysis...'}</p>
      </header>

      {error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center">
          <p className="font-medium text-red-700">{error}</p>
        </div>
      ) : (
        <ProgressTracker steps={steps} currentProgress={progress} />
      )}
    </div>
  )
}
