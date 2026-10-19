// "Zachary's LLM" set like "Roots & Roads": serif, terracotta + river teal
export function BrandTitle({ className = '' }) {
  return (
    <span className={`font-brand font-bold tracking-tight whitespace-nowrap ${className}`}>
      <span className="text-roots-500 dark:text-roots-300">Zachary&apos;s</span>{' '}
      <span className="text-road-500 dark:text-road-300">LLM</span>
    </span>
  )
}
