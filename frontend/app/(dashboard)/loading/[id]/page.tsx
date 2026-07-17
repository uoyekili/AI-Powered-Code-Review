'use client'

import { useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useReview } from '@/hooks/useReview'
import { ProgressTracker } from '@/components/ProgressTracker'
import { motion } from 'framer-motion'
import { Sparkles } from 'lucide-react'

export default function LoadingPage() {
  const router = useRouter()
  const params = useParams()
  const reviewId = params.id as string
  const { progress, steps, currentStep, pollProgress, review, error } = useReview()

  useEffect(() => {
    if (!reviewId) return

    // Start polling for progress
    pollProgress(reviewId, 2000)
  }, [reviewId, pollProgress])

  useEffect(() => {
    // When review is complete, redirect to dashboard
    if (review && progress === 100) {
      const timer = setTimeout(() => {
        router.push(`/dashboard/${reviewId}`)
      }, 1000)
      return () => clearTimeout(timer)
    }
  }, [review, progress, reviewId, router])

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/50">
      {/* Header */}
      <header className="border-b border-border/50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-primary p-2">
              <Sparkles className="h-5 w-5 text-primary-foreground" />
            </div>
            <h1 className="text-xl font-bold">Code Review Assistant</h1>
          </div>
        </div>
      </header>

      {/* Progress Section */}
      <main className="mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <div className="mx-auto w-12 h-12 rounded-lg bg-primary p-2">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            >
              <Sparkles className="h-full w-full text-primary-foreground" />
            </motion.div>
          </div>
          <h2 className="mt-6 text-3xl font-bold text-foreground">Analyzing Your Repository</h2>
          <p className="mt-2 text-muted-foreground">
            {currentStep || 'Initializing analysis...'}
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-12"
        >
          {error ? (
            <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center dark:border-red-900 dark:bg-red-950">
              <p className="font-medium text-red-800 dark:text-red-200">{error}</p>
              <p className="mt-2 text-sm text-red-600 dark:text-red-400">
                Please return home and try again with a different repository.
              </p>
            </div>
          ) : (
            <ProgressTracker steps={steps} currentProgress={progress} />
          )}
        </motion.div>

        {/* Estimated Time */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-8 text-center"
        >
          <p className="text-sm text-muted-foreground">
            {progress === 100 ? (
              'Analysis complete! Redirecting to dashboard...'
            ) : (
              <>
                This typically takes 2-5 minutes.
                <br />
                <span className="font-medium">Please keep this page open.</span>
              </>
            )}
          </p>
        </motion.div>
      </main>
    </div>
  )
}
