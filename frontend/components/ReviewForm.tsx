'use client'

import { FormEvent, useState } from 'react'

interface ReviewFormProps {
  onSubmit: (repositoryUrl: string, branch: string) => Promise<void>
  isSubmitting?: boolean
}

export function ReviewForm({ onSubmit, isSubmitting = false }: ReviewFormProps) {
  const [repositoryUrl, setRepositoryUrl] = useState('')
  const [branch, setBranch] = useState('main')
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    const value = repositoryUrl.trim()
    const branchValue = branch.trim()

    if (!value.startsWith('https://github.com/')) {
      setError('Enter a valid GitHub repository URL')
      return
    }
    if (!branchValue) {
      setError('Enter a Git branch')
      return
    }

    setError(null)
    try {
      await onSubmit(value, branchValue)
    } catch {
      setError('Failed to submit review')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <label htmlFor="repositoryUrl" className="block text-sm font-medium">
        GitHub Repository URL
      </label>
      <div className="space-y-3">
        <input
          id="repositoryUrl"
          type="url"
          value={repositoryUrl}
          onChange={(event) => setRepositoryUrl(event.target.value)}
          placeholder="https://github.com/owner/repository"
          className="w-full rounded-lg border border-zinc-300 bg-white px-4 py-3 text-zinc-900 outline-none focus:border-zinc-900"
          disabled={isSubmitting}
        />
        <label htmlFor="branch" className="block text-sm font-medium">
          Git Branch
        </label>
        <input
          id="branch"
          type="text"
          value={branch}
          onChange={(event) => setBranch(event.target.value)}
          placeholder="main"
          className="w-full rounded-lg border border-zinc-300 bg-white px-4 py-3 text-zinc-900 outline-none focus:border-zinc-900"
          disabled={isSubmitting}
        />
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full rounded-lg bg-zinc-900 px-5 py-3 text-sm font-medium text-white disabled:opacity-60"
        >
          {isSubmitting ? 'Submitting...' : 'Analyze'}
        </button>
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}
    </form>
  )
}
