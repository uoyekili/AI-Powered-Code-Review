'use client'

import { Repository } from '@/types'
import { ExternalLink, GitFork, Star, Code2, FileText, Calendar } from 'lucide-react'

interface RepositoryInfoProps {
  repository: Repository
}

export function RepositoryInfo({ repository }: RepositoryInfoProps) {
  return (
    <div className="rounded-lg border border-border bg-card p-6">
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">
            {repository.owner}/{repository.name}
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">{repository.description}</p>
        </div>
        <a
          href={repository.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-3 py-2 text-sm font-medium text-primary-foreground transition-all hover:opacity-90"
        >
          <ExternalLink className="h-4 w-4" />
          View on GitHub
        </a>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
        <div className="rounded-lg border border-border/50 bg-muted/50 p-4">
          <div className="flex items-center gap-2">
            <Star className="h-4 w-4 text-muted-foreground" />
            <span className="text-xs font-medium text-muted-foreground">Stars</span>
          </div>
          <p className="mt-2 text-xl font-bold text-foreground">{repository.stars.toLocaleString()}</p>
        </div>

        <div className="rounded-lg border border-border/50 bg-muted/50 p-4">
          <div className="flex items-center gap-2">
            <GitFork className="h-4 w-4 text-muted-foreground" />
            <span className="text-xs font-medium text-muted-foreground">Forks</span>
          </div>
          <p className="mt-2 text-xl font-bold text-foreground">{repository.forks.toLocaleString()}</p>
        </div>

        <div className="rounded-lg border border-border/50 bg-muted/50 p-4">
          <div className="flex items-center gap-2">
            <Code2 className="h-4 w-4 text-muted-foreground" />
            <span className="text-xs font-medium text-muted-foreground">Language</span>
          </div>
          <p className="mt-2 text-xl font-bold text-foreground">{repository.primaryLanguage}</p>
        </div>

        <div className="rounded-lg border border-border/50 bg-muted/50 p-4">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-muted-foreground" />
            <span className="text-xs font-medium text-muted-foreground">Files</span>
          </div>
          <p className="mt-2 text-xl font-bold text-foreground">{repository.fileCount}</p>
        </div>

        <div className="rounded-lg border border-border/50 bg-muted/50 p-4">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-muted-foreground" />
            <span className="text-xs font-medium text-muted-foreground">Directories</span>
          </div>
          <p className="mt-2 text-xl font-bold text-foreground">{repository.dirCount}</p>
        </div>

        <div className="rounded-lg border border-border/50 bg-muted/50 p-4">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <span className="text-xs font-medium text-muted-foreground">Updated</span>
          </div>
          <p className="mt-2 text-sm font-bold text-foreground">
            {new Date(repository.lastUpdated).toLocaleDateString()}
          </p>
        </div>
      </div>

      <div className="mt-6 rounded-lg border border-border/50 bg-muted/50 p-4">
        <p className="text-xs font-medium text-muted-foreground">Languages</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {repository.languages.map((lang) => (
            <span
              key={lang}
              className="inline-block rounded-full bg-primary/20 px-3 py-1 text-xs font-medium text-primary"
            >
              {lang}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

export default RepositoryInfo
