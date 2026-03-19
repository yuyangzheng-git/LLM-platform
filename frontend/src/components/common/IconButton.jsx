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
  const baseClasses = 'inline-flex items-center justify-center rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2'

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
    default: 'bg-white/70 dark:bg-bg-secondary/70 backdrop-blur-md hover:bg-white/90 dark:hover:bg-bg-secondary shadow-lg hover:shadow-xl border border-glass',
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
