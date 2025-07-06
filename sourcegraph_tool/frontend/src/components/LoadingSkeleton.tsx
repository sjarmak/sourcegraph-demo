export const LoadingSkeleton = () => {
  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {[...Array(6)].map((_, index) => (
        <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 animate-pulse">
          {/* Source badge skeleton */}
          <div className="flex items-center justify-between mb-3">
            <div className="h-5 bg-gray-200 rounded-full w-20"></div>
            <div className="h-4 bg-gray-200 rounded w-16"></div>
          </div>
          
          {/* Title skeleton */}
          <div className="h-6 bg-gray-200 rounded mb-3 w-full"></div>
          <div className="h-6 bg-gray-200 rounded mb-4 w-3/4"></div>
          
          {/* Summary skeleton */}
          <div className="space-y-2 mb-4">
            <div className="h-4 bg-gray-200 rounded w-full"></div>
            <div className="h-4 bg-gray-200 rounded w-full"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
          
          {/* Tags skeleton */}
          <div className="flex gap-2 mb-4">
            <div className="h-6 bg-gray-200 rounded-full w-16"></div>
            <div className="h-6 bg-gray-200 rounded-full w-20"></div>
            <div className="h-6 bg-gray-200 rounded-full w-14"></div>
          </div>
          
          {/* Link skeleton */}
          <div className="h-4 bg-gray-200 rounded w-24"></div>
        </div>
      ))}
    </div>
  );
};
