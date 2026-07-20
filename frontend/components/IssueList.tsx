'use client'

import type { Issue } from '@/types'
import { formatLabel } from '@/utils/format'

interface IssueListProps {
  issues: Issue[]
}

export function IssueList({ issues }: IssueListProps) {
  if (issues.length === 0) {
    return (
      <div className="rounded-lg border border-zinc-200 bg-white p-8 text-center">
        <p className="font-medium">No issues found</p>
        <p className="mt-1 text-sm text-zinc-500">
          Mock results currently return an empty issue list.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {issues.map((issue) => (
        <article key={issue.id} className="rounded-lg border border-zinc-200 bg-white p-4">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-medium">{issue.title}</h3>
            <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs capitalize">
              {formatLabel(issue.severity)}
            </span>
            <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs capitalize">
              {formatLabel(issue.type)}
            </span>
          </div>
          <p className="mt-2 text-sm text-zinc-600">{issue.description}</p>
          <p className="mt-2 text-xs text-zinc-500">
            {issue.file}:{issue.line}
          </p>
          <p className="mt-2 text-sm">
            <span className="font-medium">Suggestion:</span> {issue.suggestion}
          </p>
        </article>
      ))}
    </div>
  )
}
