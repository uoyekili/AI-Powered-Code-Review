'use client'

import { Issue } from '@/types'
import { AlertCircle, AlertTriangle, AlertOctagon, Info, Lightbulb } from 'lucide-react'

interface IssueListProps {
  issues: Issue[]
  onIssueClick?: (issue: Issue) => void
}

export function IssueList({ issues, onIssueClick }: IssueListProps) {
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertOctagon className="h-5 w-5 text-red-600" />
      case 'high':
        return <AlertTriangle className="h-5 w-5 text-orange-600" />
      case 'medium':
        return <AlertCircle className="h-5 w-5 text-amber-600" />
      case 'low':
        return <Info className="h-5 w-5 text-blue-600" />
      case 'info':
        return <Lightbulb className="h-5 w-5 text-green-600" />
      default:
        return <Info className="h-5 w-5" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950'
      case 'high':
        return 'border-orange-200 bg-orange-50 dark:border-orange-900 dark:bg-orange-950'
      case 'medium':
        return 'border-amber-200 bg-amber-50 dark:border-amber-900 dark:bg-amber-950'
      case 'low':
        return 'border-blue-200 bg-blue-50 dark:border-blue-900 dark:bg-blue-950'
      case 'info':
        return 'border-green-200 bg-green-50 dark:border-green-900 dark:bg-green-950'
      default:
        return 'border-border bg-card'
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'security':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      case 'performance':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
      case 'maintainability':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      case 'code-quality':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 'architecture':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (issues.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-card p-8 text-center">
        <div className="flex justify-center">
          <Lightbulb className="h-12 w-12 text-green-600" />
        </div>
        <p className="mt-4 font-medium text-foreground">No issues found</p>
        <p className="mt-1 text-sm text-muted-foreground">This file has excellent code quality!</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {issues.map((issue) => (
        <div
          key={issue.id}
          onClick={() => onIssueClick?.(issue)}
          className={`cursor-pointer rounded-lg border p-4 transition-all hover:shadow-md ${getSeverityColor(issue.severity)}`}
        >
          <div className="flex items-start gap-3">
            <div className="mt-0.5">{getSeverityIcon(issue.severity)}</div>
            <div className="flex-1">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h4 className="font-semibold text-foreground">{issue.title}</h4>
                  <p className="mt-1 text-sm text-muted-foreground">{issue.description}</p>
                </div>
                <span className={`inline-block rounded px-2 py-1 text-xs font-medium ${getTypeColor(issue.type)}`}>
                  {issue.type.replace('-', ' ')}
                </span>
              </div>
              <div className="mt-3 space-y-2">
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Suggestion:</p>
                  <p className="mt-0.5 text-sm text-foreground">{issue.suggestion}</p>
                </div>
                {issue.code && (
                  <div className="rounded bg-background p-2">
                    <p className="font-mono text-xs text-muted-foreground">{issue.code}</p>
                  </div>
                )}
              </div>
              <p className="mt-2 text-xs text-muted-foreground">{issue.file}:{issue.line}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default IssueList
