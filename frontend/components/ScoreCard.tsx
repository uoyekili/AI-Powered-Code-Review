'use client'

import { motion } from 'framer-motion'

interface ScoreCardProps {
  title: string
  score: number
  maxScore?: number
  delay?: number
  className?: string
}

export function ScoreCard({
  title,
  score,
  maxScore = 100,
  delay = 0,
  className = '',
}: ScoreCardProps) {
  const percentage = (score / maxScore) * 100
  const getColor = (value: number) => {
    if (value >= 80) return 'from-emerald-500 to-emerald-600'
    if (value >= 60) return 'from-amber-500 to-amber-600'
    if (value >= 40) return 'from-orange-500 to-orange-600'
    return 'from-red-500 to-red-600'
  }

  const getTextColor = (value: number) => {
    if (value >= 80) return 'text-emerald-600 dark:text-emerald-400'
    if (value >= 60) return 'text-amber-600 dark:text-amber-400'
    if (value >= 40) return 'text-orange-600 dark:text-orange-400'
    return 'text-red-600 dark:text-red-400'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className={`flex flex-col items-center justify-center rounded-lg border border-border bg-card p-6 ${className}`}
    >
      <div className="relative h-28 w-28">
        <svg className="h-full w-full" viewBox="0 0 120 120">
          <circle
            cx="60"
            cy="60"
            r="54"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-muted-foreground/20"
          />
          <motion.circle
            cx="60"
            cy="60"
            r="54"
            fill="none"
            strokeWidth="8"
            strokeDasharray={`${2 * Math.PI * 54}`}
            strokeDashoffset={`${2 * Math.PI * 54 * (1 - percentage / 100)}`}
            className={`${getTextColor(score)}`}
            strokeLinecap="round"
            initial={{ strokeDashoffset: 2 * Math.PI * 54 }}
            animate={{ strokeDashoffset: 2 * Math.PI * 54 * (1 - percentage / 100) }}
            transition={{ duration: 1, delay }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <span className="text-2xl font-bold">{score}</span>
            <span className="text-xs text-muted-foreground">/100</span>
          </div>
        </div>
      </div>
      <p className="mt-4 text-center text-sm font-medium text-foreground">{title}</p>
    </motion.div>
  )
}

export default ScoreCard
