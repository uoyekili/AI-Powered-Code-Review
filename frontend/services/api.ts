import axios from 'axios'
import { Review, AnalysisStep } from '@/types'
import { env } from '@/lib/env'

const api = axios.create({
  baseURL: env.NEXT_PUBLIC_API_URL,
  timeout: 120000,
})

export const reviewService = {
  async submitReview(repositoryUrl: string): Promise<{ reviewId: string }> {
    const response = await api.post<{ reviewId: string }>('/review', {
      repositoryUrl,
    })
    return response.data
  },

  async getReview(reviewId: string): Promise<Review> {
    const response = await api.get<Review>(`/review/${reviewId}`)
    return response.data
  },

  async getProgress(reviewId: string): Promise<{
    progress: number
    currentStep: string
    steps: AnalysisStep[]
    status?: string
  }> {
    const response = await api.get<{
      progress: number
      currentStep: string
      steps: AnalysisStep[]
      status?: string
    }>(`/review/${reviewId}/progress`)
    return response.data
  },

  async getReport(reviewId: string): Promise<string> {
    const response = await api.get<string>(`/report/${reviewId}`, {
      responseType: 'text',
    })
    return response.data
  },

  async downloadReport(reviewId: string, format: 'markdown' | 'pdf' = 'markdown'): Promise<Blob> {
    const reportContent = await this.getReport(reviewId)
    const mimeType = format === 'markdown' ? 'text/markdown' : 'application/pdf'
    return new Blob([reportContent], { type: mimeType })
  },
}

export default api
