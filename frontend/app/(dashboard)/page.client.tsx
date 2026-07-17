'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Button } from '@/components/ui/button'
import { useReview } from '@/hooks/useReview'
import { exampleRepositories } from '@/lib/constants'
import { GitBranch, Sparkles, ArrowRight, Code } from 'lucide-react'
import { motion } from 'framer-motion'

const reviewSchema = z.object({
  repositoryUrl: z.string().url('Please enter a valid GitHub URL'),
})

type ReviewFormData = z.infer<typeof reviewSchema>

export function HomePageClient() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { submitReview } = useReview()

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<ReviewFormData>({
    resolver: zodResolver(reviewSchema),
  })

  const onSubmit = async (data: ReviewFormData) => {
    setIsSubmitting(true)
    try {
      const reviewId = await submitReview(data.repositoryUrl)
      router.push(`/loading/${reviewId}`)
    } catch (error) {
      console.error('Failed to submit review:', error)
      setIsSubmitting(false)
    }
  }

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
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
          >
            <Code className="h-4 w-4" />
            GitHub
          </a>
        </div>
      </header>

      {/* Hero Section */}
      <main className="mx-auto max-w-4xl px-4 py-16 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <h2 className="text-balance text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            AI-Powered Code Review
          </h2>
          <p className="mt-4 text-balance text-lg text-muted-foreground">
            Submit your GitHub repository and receive comprehensive AI-generated code reviews
            covering security, performance, maintainability, and code quality.
          </p>
        </motion.div>

        {/* Input Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="mt-12"
        >
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label htmlFor="url" className="block text-sm font-medium text-foreground">
                GitHub Repository URL
              </label>
              <div className="mt-2 flex gap-2">
                <div className="relative flex-1">
                  <GitBranch className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
                  <input
                    {...register('repositoryUrl')}
                    type="url"
                    placeholder="https://github.com/owner/repository"
                    className="w-full rounded-lg border border-border bg-background px-4 py-3 pl-10 text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                  />
                </div>
                <Button
                  type="submit"
                  disabled={isSubmitting}
                  className="gap-2"
                  size="lg"
                >
                  {isSubmitting ? (
                    <>
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      Analyze
                      <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </Button>
              </div>
              {errors.repositoryUrl && (
                <p className="mt-2 text-sm text-red-600 dark:text-red-400">
                  {errors.repositoryUrl.message}
                </p>
              )}
            </div>
          </form>

          {/* Examples */}
          <div className="mt-8">
            <p className="text-sm font-medium text-muted-foreground">Try with an example:</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {exampleRepositories.map((repo) => (
                <motion.button
                  key={repo.url}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setValue('repositoryUrl', repo.url)}
                  className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2 text-sm text-foreground transition-all hover:border-primary hover:bg-primary/5"
                >
                  <Code className="h-4 w-4" />
                  {repo.owner}/{repo.name}
                </motion.button>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-16 grid gap-6 md:grid-cols-2"
        >
          {[
            {
              title: 'Security Analysis',
              description: 'Detect vulnerabilities and security issues in your codebase',
            },
            {
              title: 'Performance Review',
              description: 'Identify performance bottlenecks and optimization opportunities',
            },
            {
              title: 'Code Quality',
              description: 'Get insights on code complexity and maintainability',
            },
            {
              title: 'Architecture Review',
              description: 'Evaluate overall system design and patterns',
            },
          ].map((feature, index) => (
            <div
              key={index}
              className="rounded-lg border border-border bg-card/50 p-6 backdrop-blur-sm"
            >
              <h3 className="font-semibold text-foreground">{feature.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{feature.description}</p>
            </div>
          ))}
        </motion.div>
      </main>
    </div>
  )
}
