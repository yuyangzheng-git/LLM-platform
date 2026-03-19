function Loading({ message = 'Loading...' }) {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
        <p className="mt-4 text-gray-600">{message}</p>
      </div>
    </div>
  )
}

export default Loading
