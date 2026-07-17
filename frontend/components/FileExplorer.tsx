'use client'

import { FileReview } from '@/types'
import { File, ChevronRight } from 'lucide-react'
import { useState } from 'react'

interface FileExplorerProps {
  files: FileReview[]
  selectedFile?: FileReview
  onSelectFile: (file: FileReview) => void
}

export function FileExplorer({ files, selectedFile, onSelectFile }: FileExplorerProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-600 dark:text-emerald-400'
    if (score >= 60) return 'text-amber-600 dark:text-amber-400'
    if (score >= 40) return 'text-orange-600 dark:text-orange-400'
    return 'text-red-600 dark:text-red-400'
  }

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-emerald-100 dark:bg-emerald-950'
    if (score >= 60) return 'bg-amber-100 dark:bg-amber-950'
    if (score >= 40) return 'bg-orange-100 dark:bg-orange-950'
    return 'bg-red-100 dark:bg-red-950'
  }

  return (
    <div className="flex flex-col gap-2">
      {files.map((file) => (
        <button
          key={file.path}
          onClick={() => onSelectFile(file)}
          className={`flex items-center justify-between rounded-lg border px-4 py-3 text-left transition-all ${
            selectedFile?.path === file.path
              ? 'border-primary bg-primary/10'
              : 'border-border hover:bg-muted'
          }`}
        >
          <div className="flex flex-1 items-center gap-2">
            <File className="h-4 w-4 text-muted-foreground" />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">{file.name}</p>
              <p className="truncate text-xs text-muted-foreground">{file.path}</p>
            </div>
          </div>
          <div className="ml-2 flex items-center gap-2">
            {file.issues.length > 0 && (
              <span className="inline-block rounded bg-red-100 px-2 py-1 text-xs font-medium text-red-800 dark:bg-red-950 dark:text-red-200">
                {file.issues.length}
              </span>
            )}
            <div
              className={`flex h-8 w-8 items-center justify-center rounded font-mono text-sm font-bold ${getScoreBg(file.score)} ${getScoreColor(file.score)}`}
            >
              {file.score}
            </div>
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          </div>
        </button>
      ))}
    </div>
  )
}

export default FileExplorer
