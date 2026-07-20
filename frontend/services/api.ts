import axios from 'axios'
import type { ProgressResponse, Review } from '@/types'
import { env } from '@/utils/env'

const api = axios.create({
  baseURL: env.NEXT_PUBLIC_API_URL,
  timeout: 120_000,
})

export const reviewService = {
  async submitReview(repositoryUrl: string, branch: string): Promise<{ reviewId: string }> {
    const response = await api.post<{ reviewId: string }>('/review', {
      repositoryUrl,
      branch,
    })
    return response.data
  },

  async getReview(reviewId: string): Promise<Review> {
    const response = await api.get<Review>(`/review/${reviewId}`)
    return response.data
  },

  async getProgress(reviewId: string): Promise<ProgressResponse> {
    const response = await api.get<ProgressResponse>(`/review/${reviewId}/progress`)
    return response.data
  },

  async getReport(reviewId: string): Promise<string> {
    const response = await api.get<string>(`/report/${reviewId}`, {
      responseType: 'text',
    })
    return response.data
  },

  async downloadReport(reviewId: string): Promise<Blob> {
    const reportContent = await this.getReport(reviewId)
    return new Blob([reportContent], { type: 'text/markdown' })
  },
}

export default api
