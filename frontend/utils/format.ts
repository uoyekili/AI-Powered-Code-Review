/** Format a severity label for display. */
export function formatLabel(value: string): string {
  return value.replace(/-/g, ' ')
}
