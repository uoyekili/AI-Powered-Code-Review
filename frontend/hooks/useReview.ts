'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import type { AnalysisStep, Review } from '@/types'
import { reviewService } from '@/services/api'

interface UseReviewState {
  review: Review | null
  isLoading: boolean
  error: string | null
  progress: number
  steps: AnalysisStep[]
  currentStep: string
}

export function useReview() {
  const [state, setState] = useState<UseReviewState>({
    review: null,
    isLoading: false,
    error: null,
    progress: 0,
    steps: [],
    currentStep: '',
  })
  const pollTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const active = useRef(true)

  useEffect(() => {
    active.current = true
    return () => {
      active.current = false
      if (pollTimer.current) {
        clearTimeout(pollTimer.current)
      }
    }
  }, [])

  const submitReview = useCallback(async (repositoryUrl: string, branch: string) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }))
    try {
      const result = await reviewService.submitReview(repositoryUrl, branch)
      setState((prev) => ({ ...prev, isLoading: false }))
      return result.reviewId
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to submit review'
      setState((prev) => ({ ...prev, error: message, isLoading: false }))
      throw error
    }
  }, [])

  const fetchReview = useCallback(async (reviewId: string) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }))
    try {
      const review = await reviewService.getReview(reviewId)
      if (!active.current) return review
      setState((prev) => ({
        ...prev,
        review,
        progress: review.progress,
        isLoading: false,
      }))
      return review
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch review'
      if (active.current) {
        setState((prev) => ({ ...prev, error: message, isLoading: false }))
      }
      throw error
    }
  }, [])

  const pollProgress = useCallback(
    (reviewId: string, intervalMs = 2000) => {
      const poll = async () => {
        try {
          const progressData = await reviewService.getProgress(reviewId)
          if (!active.current) return

          setState((prev) => ({
            ...prev,
            progress: progressData.progress,
            currentStep: progressData.currentStep,
            steps: progressData.steps,
          }))

          if (progressData.status === 'completed' || progressData.progress >= 100) {
            await fetchReview(reviewId)
            return
          }

          if (progressData.status === 'failed') {
            setState((prev) => ({
              ...prev,
              isLoading: false,
              error: progressData.currentStep || 'Analysis failed',
            }))
            return
          }

          pollTimer.current = setTimeout(poll, intervalMs)
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to fetch progress'
          if (active.current) {
            setState((prev) => ({ ...prev, error: message }))
          }
        }
      }

      void poll()
    },
    [fetchReview],
  )

  const downloadReport = useCallback(async (reviewId: string) => {
    const blob = await reviewService.downloadReport(reviewId)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `review-${reviewId}.md`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }, [])

  return {
    ...state,
    submitReview,
    fetchReview,
    pollProgress,
    downloadReport,
  }
}
