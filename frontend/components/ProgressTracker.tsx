'use client'

import type { AnalysisStep } from '@/types'
import { formatLabel } from '@/utils/format'

interface ProgressTrackerProps {
  steps: AnalysisStep[]
  currentProgress: number
}

export function ProgressTracker({ steps, currentProgress }: ProgressTrackerProps) {
  const completedSteps = steps.filter((step) => step.status === 'completed').length

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-zinc-200 bg-white p-6">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-lg font-semibold">Analysis Progress</h3>
          <span className="text-2xl font-bold">{currentProgress}%</span>
        </div>
        <div className="h-3 overflow-hidden rounded-full bg-zinc-100">
          <div
            className="h-full bg-zinc-900 transition-all"
            style={{ width: `${currentProgress}%` }}
          />
        </div>
        <p className="mt-3 text-sm text-zinc-500">
          {completedSteps} of {steps.length} steps completed
        </p>
      </div>

      <div className="space-y-3">
        {steps.map((step) => (
          <div
            key={step.id}
            className="flex items-start justify-between gap-4 rounded-lg border border-zinc-200 bg-white p-4"
          >
            <div>
              <h4 className="font-medium">{step.name}</h4>
              <p className="text-sm text-zinc-500">{step.description}</p>
            </div>
            <span className="rounded-full bg-zinc-100 px-3 py-1 text-xs font-medium capitalize">
              {formatLabel(step.status)}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
