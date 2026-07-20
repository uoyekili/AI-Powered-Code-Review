'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ReviewForm } from '@/components/ReviewForm'
import { useReview } from '@/hooks/useReview'

export function HomePageClient() {
  const router = useRouter()
  const { submitReview } = useReview()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (repositoryUrl: string, branch: string) => {
    setIsSubmitting(true)
    try {
      const reviewId = await submitReview(repositoryUrl, branch)
      router.push(`/loading/${reviewId}`)
    } catch {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-16">
      <header className="mb-10 text-center">
        <h1 className="text-4xl font-bold tracking-tight">AI-Powered Code Review</h1>
        <p className="mt-3 text-zinc-600">
          Submit a public GitHub repository URL to start a mock review pipeline.
        </p>
      </header>
      <ReviewForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />
    </div>
  )
}
