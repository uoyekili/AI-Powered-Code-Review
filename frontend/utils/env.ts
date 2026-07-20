const REQUIRED_ENV = {
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
} as const

function validateEnv(): Record<keyof typeof REQUIRED_ENV, string> {
  const missing = Object.entries(REQUIRED_ENV)
    .filter(([, value]) => !value?.trim())
    .map(([key]) => key)

  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variable(s): ${missing.join(', ')}. ` +
        'Copy frontend/.env.example to frontend/.env and set the values.',
    )
  }

  return {
    NEXT_PUBLIC_API_URL: REQUIRED_ENV.NEXT_PUBLIC_API_URL!.trim(),
  }
}

export const env = validateEnv()
