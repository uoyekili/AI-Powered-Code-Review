import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI GitHub Code Review',
  description: 'Submit a GitHub repository and receive an AI-assisted code review',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-zinc-50 text-zinc-900 antialiased">{children}</body>
    </html>
  )
}
