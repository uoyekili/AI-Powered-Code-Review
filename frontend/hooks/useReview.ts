'use client'

import { useState, useCallback, useEffect } from 'react'
import { Review, AnalysisStep } from '@/types'
import { reviewService } from '@/services/api'

export interface UseReviewState {
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

  // Submit a repository for analysis
  const submitReview = useCallback(async (repositoryUrl: string) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }))
    try {
      const result = await reviewService.submitReview(repositoryUrl)
      localStorage.setItem('lastReviewId', result.reviewId)
      return result.reviewId
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to submit review'
      setState((prev) => ({ ...prev, error: message, isLoading: false }))
      throw error
    }
  }, [])

  // Fetch review details
  const fetchReview = useCallback(async (reviewId: string) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }))
    try {
      const review = await reviewService.getReview(reviewId)
      setState((prev) => ({
        ...prev,
        review,
        progress: 100,
        isLoading: false,
      }))
      return review
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch review'
      setState((prev) => ({ ...prev, error: message, isLoading: false }))
      throw error
    }
  }, [])

  // Poll for progress updates
  const pollProgress = useCallback(
    async (reviewId: string, intervalMs: number = 2000) => {
      const poll = async () => {
        try {
          const progressData = await reviewService.getProgress(reviewId)
          setState((prev) => ({
            ...prev,
            progress: progressData.progress,
            currentStep: progressData.currentStep,
            steps: progressData.steps,
          }))

          // Stop polling if complete or failed
          if (progressData.progress >= 100 || progressData.status === 'completed') {
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

          // Continue polling
          setTimeout(poll, intervalMs)
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to fetch progress'
          setState((prev) => ({ ...prev, error: message }))
        }
      }

      poll()
    },
    [fetchReview]
  )

  // Download report
  const downloadReport = useCallback(async (reviewId: string, format: 'markdown' | 'pdf' = 'markdown') => {
    try {
      const blob = await reviewService.downloadReport(reviewId, format)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `review-${reviewId}.${format === 'markdown' ? 'md' : 'pdf'}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to download report'
      setState((prev) => ({ ...prev, error: message }))
      throw error
    }
  }, [])

  // Reset state
  const reset = useCallback(() => {
    setState({
      review: null,
      isLoading: false,
      error: null,
      progress: 0,
      steps: [],
      currentStep: '',
    })
  }, [])

  return {
    ...state,
    submitReview,
    fetchReview,
    pollProgress,
    downloadReport,
    reset,
  }
}
