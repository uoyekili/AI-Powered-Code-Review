export interface Repository {
  id: string
  name: string
  owner: string
  url: string
  description: string
  stars: number
  forks: number
  primaryLanguage: string
  languages: string[]
  fileCount: number
  dirCount: number
  totalLines: number
  lastUpdated: string
}

export interface CodeReviewMetrics {
  overallScore: number
  securityScore: number
  performanceScore: number
  maintainabilityScore: number
  codeQualityScore: number
  architectureScore: number
}

export interface IssueSeverity {
  critical: number
  high: number
  medium: number
  low: number
  info: number
}

export interface Issue {
  id: string
  file: string
  line: number
  type: 'security' | 'performance' | 'maintainability' | 'code-quality' | 'architecture'
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
  title: string
  description: string
  suggestion: string
  code?: string
}

export interface FileReview {
  path: string
  name: string
  extension: string
  lines: number
  issues: Issue[]
  summary: string
  score: number
}

export interface Review {
  id: string
  repositoryUrl: string
  repository: Repository
  metrics: CodeReviewMetrics
  issueSeverity: IssueSeverity
  files: FileReview[]
  issuesByCategory: {
    security: number
    performance: number
    maintainability: number
    codeQuality: number
    architecture: number
  }
  createdAt: string
  status: 'pending' | 'in-progress' | 'completed' | 'failed'
  progress: number
  currentStep: string
}

export interface AnalysisStep {
  id: string
  name: string
  description: string
  status: 'pending' | 'in-progress' | 'completed' | 'failed'
  estimatedTime: number
}
