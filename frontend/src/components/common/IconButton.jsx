export function IconButton({
  icon: Icon,
  onClick,
  label,
  variant = 'default',
  size = 'md',
  disabled = false,
  className = '',
  ...props
}) {
  const baseClasses = 'touch-target inline-flex items-center justify-center rounded-full transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-roots-300 focus-visible:ring-offset-2'

  const sizeClasses = {
    sm: 'p-1.5',
    md: 'p-2 sm:p-2.5',
    lg: 'p-2.5 sm:p-3',
  }

  const iconSizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  }

  const variantClasses = {
    default: 'bg-cream/70 dark:bg-bg-secondary/70 backdrop-blur-md hover:bg-cream/90 dark:hover:bg-bg-secondary shadow-paper hover:shadow-lg border border-glass',
    primary: 'bg-gradient-main text-white hover:shadow-2xl hover:scale-105',
    ghost: 'hover:bg-bg-tertiary/50',
    danger: 'hover:bg-red-100 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400',
  }

  const disabledClasses = disabled
    ? 'opacity-50 cursor-not-allowed hover:scale-100 hover:shadow-none'
    : ''

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${disabledClasses} ${className}`}
      aria-label={label}
      title={label}
      {...props}
    >
      <Icon className={iconSizeClasses[size]} />
    </button>
  )
}
