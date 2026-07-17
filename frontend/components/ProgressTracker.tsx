'use client'

import { AnalysisStep } from '@/types'
import { CheckCircle2, Circle, AlertCircle, Loader } from 'lucide-react'
import { motion } from 'framer-motion'

interface ProgressTrackerProps {
  steps: AnalysisStep[]
  currentProgress: number
}

export function ProgressTracker({ steps, currentProgress }: ProgressTrackerProps) {
  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-6 w-6 text-emerald-600" />
      case 'in-progress':
        return (
          <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity }}>
            <Loader className="h-6 w-6 text-primary" />
          </motion.div>
        )
      case 'failed':
        return <AlertCircle className="h-6 w-6 text-red-600" />
      default:
        return <Circle className="h-6 w-6 text-muted-foreground" />
    }
  }

  const activeStepIndex = steps.findIndex((step) => step.status === 'in-progress')
  const completedSteps = steps.filter((step) => step.status === 'completed').length

  return (
    <div className="space-y-8">
      <div className="rounded-lg border border-border bg-card p-6">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-foreground">Analysis Progress</h3>
          <span className="text-2xl font-bold text-primary">{currentProgress}%</span>
        </div>
        <div className="h-3 overflow-hidden rounded-full bg-muted">
          <motion.div
            className="h-full bg-gradient-to-r from-primary to-primary/70"
            initial={{ width: 0 }}
            animate={{ width: `${currentProgress}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
        <p className="mt-3 text-sm text-muted-foreground">
          {completedSteps} of {steps.length} steps completed
        </p>
      </div>

      <div className="space-y-4">
        {steps.map((step, index) => (
          <motion.div
            key={step.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`flex gap-4 rounded-lg border p-4 ${
              step.status === 'completed' || step.status === 'in-progress'
                ? 'border-primary/30 bg-primary/5'
                : 'border-border bg-card'
            }`}
          >
            <div className="mt-1">{getStepIcon(step.status)}</div>
            <div className="flex-1">
              <h4 className="font-medium text-foreground">{step.name}</h4>
              <p className="text-sm text-muted-foreground">{step.description}</p>
              {step.estimatedTime && (
                <p className="mt-2 text-xs text-muted-foreground">
                  Estimated time: {step.estimatedTime}s
                </p>
              )}
            </div>
            <div className="text-right">
              <span
                className={`inline-block rounded-full px-3 py-1 text-xs font-medium ${
                  step.status === 'completed'
                    ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200'
                    : step.status === 'in-progress'
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-200'
                      : step.status === 'failed'
                        ? 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-200'
                        : 'bg-muted text-muted-foreground'
                }`}
              >
                {step.status.replace('-', ' ')}
              </span>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

export default ProgressTracker
