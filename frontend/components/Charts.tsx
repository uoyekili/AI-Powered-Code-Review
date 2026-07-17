'use client'

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import { CodeReviewMetrics, IssueSeverity } from '@/types'

interface ScoreRadarProps {
  metrics: CodeReviewMetrics
}

export function ScoreRadar({ metrics }: ScoreRadarProps) {
  const data = [
    { subject: 'Security', value: metrics.securityScore },
    { subject: 'Performance', value: metrics.performanceScore },
    { subject: 'Maintainability', value: metrics.maintainabilityScore },
    { subject: 'Code Quality', value: metrics.codeQualityScore },
    { subject: 'Architecture', value: metrics.architectureScore },
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={data}>
        <PolarGrid stroke="hsl(var(--border))" />
        <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12 }} />
        <PolarRadiusAxis tick={{ fontSize: 12 }} />
        <Radar
          name="Score"
          dataKey="value"
          stroke="hsl(var(--primary))"
          fill="hsl(var(--primary))"
          fillOpacity={0.6}
        />
      </RadarChart>
    </ResponsiveContainer>
  )
}

interface SeverityDistributionProps {
  issueSeverity: IssueSeverity
}

export function SeverityDistribution({ issueSeverity }: SeverityDistributionProps) {
  const data = [
    { name: 'Critical', value: issueSeverity.critical, color: '#dc2626' },
    { name: 'High', value: issueSeverity.high, color: '#ea580c' },
    { name: 'Medium', value: issueSeverity.medium, color: '#f59e0b' },
    { name: 'Low', value: issueSeverity.low, color: '#3b82f6' },
    { name: 'Info', value: issueSeverity.info, color: '#10b981' },
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, value }) => `${name}: ${value}`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  )
}

interface IssuesByCategoryProps {
  issuesByCategory: Record<string, number>
}

export function IssuesByCategory({ issuesByCategory }: IssuesByCategoryProps) {
  const data = [
    { name: 'Security', value: issuesByCategory.security || 0 },
    { name: 'Performance', value: issuesByCategory.performance || 0 },
    { name: 'Maintainability', value: issuesByCategory.maintainability || 0 },
    { name: 'Code Quality', value: issuesByCategory.codeQuality || 0 },
    { name: 'Architecture', value: issuesByCategory.architecture || 0 },
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }} />
        <Bar dataKey="value" fill="hsl(var(--primary))" radius={[8, 8, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
