import { Search, Loader2, CheckCircle, XCircle, ExternalLink, Clock, MapPin, Globe } from 'lucide-react';

const ToolCallDisplay = ({ toolCalls }) => {
  if (!toolCalls || toolCalls.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3 my-4">
      {toolCalls.map((toolCall, index) => (
        <ToolCallItem key={toolCall.id || index} toolCall={toolCall} />
      ))}
    </div>
  );
};

const ToolCallItem = ({ toolCall }) => {
  const { name, arguments: args, status = 'calling', result, error } = toolCall;

  // Determine status
  const isCompleted = status === 'completed';
  const isError = status === 'error' || error;
  const isCalling = status === 'calling';

  // Get icon and color based on status
  const getStatusIcon = () => {
    if (isError) {
      return <XCircle className="w-4 h-4 text-red-500" />;
    }
    if (isCompleted) {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
    return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
  };

  const getToolIcon = () => {
    if (name === 'web_search') {
      return <Search className="w-4 h-4" />;
    }
    if (name === 'get_current_datetime') {
      return <Clock className="w-4 h-4" />;
    }
    if (name === 'geocode_address' || name === 'reverse_geocode') {
      return <MapPin className="w-4 h-4" />;
    }
    if (name === 'analyze_website') {
      return <Globe className="w-4 h-4" />;
    }
    return null;
  };

  const getToolName = () => {
    if (name === 'web_search') {
      return '网络搜索';
    }
    if (name === 'get_current_datetime') {
      return '获取时间';
    }
    if (name === 'geocode_address') {
      return '地址查询';
    }
    if (name === 'reverse_geocode') {
      return '坐标查询';
    }
    if (name === 'analyze_website') {
      return '网站分析';
    }
    return name;
  };

  // Full class names (not built from strings) so Tailwind generates them
  const getToolStyle = () => {
    if (name === 'web_search') {
      return 'bg-road-50/80 dark:bg-road-900/25 border-road-200 dark:border-road-800';
    }
    if (name === 'get_current_datetime') {
      return 'bg-sun-100/60 dark:bg-sun-600/10 border-sun-300/70 dark:border-sun-600/30';
    }
    if (name === 'geocode_address' || name === 'reverse_geocode') {
      return 'bg-emerald-50/80 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800';
    }
    if (name === 'analyze_website') {
      return 'bg-roots-50/80 dark:bg-roots-900/25 border-roots-200 dark:border-roots-800';
    }
    return 'bg-bg-tertiary/60 border-border-primary';
  };

  return (
    <div className={`${getToolStyle()} rounded-2xl p-4 border`}>
      {/* Header */}
      <div className="flex items-center gap-2 mb-2">
        {getToolIcon()}
        <span className="font-medium text-sm text-gray-800 dark:text-gray-200">
          {getToolName()}
        </span>
        {getStatusIcon()}
      </div>

      {/* Query or parameters */}
      {args?.query && (
        <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
          搜索: <span className="font-mono">{args.query}</span>
        </div>
      )}
      {args?.url && (
        <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
          网址: <span className="font-mono break-all">{args.url}</span>
        </div>
      )}
      {args?.address && (
        <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
          地址: <span className="font-mono">{args.address}</span>
        </div>
      )}
      {args?.timezone_name && (
        <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
          时区: <span className="font-mono">{args.timezone_name}</span>
        </div>
      )}

      {/* Status message */}
      {isCalling && (
        <div className="text-xs text-blue-600 dark:text-blue-400">
          {name === 'web_search' && '正在搜索...'}
          {name === 'get_current_datetime' && '获取时间中...'}
          {(name === 'geocode_address' || name === 'reverse_geocode') && '查询位置中...'}
          {name === 'analyze_website' && '分析网站中...'}
          {!['web_search', 'get_current_datetime', 'geocode_address', 'reverse_geocode', 'analyze_website'].includes(name) && '执行中...'}
        </div>
      )}

      {/* Error */}
      {isError && (
        <div className="text-sm text-red-600 dark:text-red-400 mt-2">
          错误: {error || '搜索失败'}
        </div>
      )}

      {/* Results */}
      {isCompleted && result && name === 'web_search' && (
        <SearchResults result={result} />
      )}
      {isCompleted && result && name === 'get_current_datetime' && (
        <DateTimeResults result={result} />
      )}
      {isCompleted && result && (name === 'geocode_address' || name === 'reverse_geocode') && (
        <LocationResults result={result} />
      )}
      {isCompleted && result && name === 'analyze_website' && (
        <WebsiteAnalysisResults result={result} />
      )}
    </div>
  );
};

const DateTimeResults = ({ result }) => {
  if (!result.success) {
    return (
      <div className="text-sm text-red-600 dark:text-red-400 mt-2">
        {result.error || '获取时间失败'}
      </div>
    );
  }

  return (
    <div className="mt-3 space-y-2">
      <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
        {result.formatted}
      </div>
      {result.timezone && (
        <div className="text-xs text-gray-600 dark:text-gray-400">
          时区: {result.timezone}
        </div>
      )}
    </div>
  );
};

const LocationResults = ({ result }) => {
  if (!result.success) {
    return (
      <div className="text-sm text-red-600 dark:text-red-400 mt-2">
        {result.error || '地址查询失败'}
      </div>
    );
  }

  // 反向地理编码结果（单个结果）
  if (result.display_name && !result.results) {
    return (
      <div className="mt-3 space-y-2">
        <div className="text-sm text-gray-700 dark:text-gray-300">
          📍 {result.display_name}
        </div>
        {result.latitude && result.longitude && (
          <div className="text-xs text-gray-600 dark:text-gray-400">
            坐标: {result.latitude.toFixed(6)}, {result.longitude.toFixed(6)}
          </div>
        )}
      </div>
    );
  }

  // 地理编码结果（可能多个结果）
  const { results = [], result_count = 0 } = result;

  if (results.length === 0) {
    return (
      <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">
        未找到匹配的地址
      </div>
    );
  }

  return (
    <div className="mt-3 space-y-2">
      <div className="text-xs font-medium text-gray-700 dark:text-gray-300">
        找到 {result_count} 个位置
      </div>

      {/* Show top 3 results */}
      <div className="space-y-2">
        {results.slice(0, 3).map((item, idx) => (
          <div
            key={idx}
            className="text-sm border-l-2 border-green-300 dark:border-green-700 pl-3 py-1"
          >
            <div className="font-medium text-gray-700 dark:text-gray-300">
              📍 {item.display_name}
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
              坐标: {item.latitude.toFixed(6)}, {item.longitude.toFixed(6)}
            </div>
            {item.type && (
              <div className="text-xs text-gray-500 dark:text-gray-500 mt-0.5">
                类型: {item.type}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Show more indicator */}
      {results.length > 3 && (
        <div className="text-xs text-gray-500 dark:text-gray-500 italic">
          还有 {results.length - 3} 个位置...
        </div>
      )}
    </div>
  );
};

const SearchResults = ({ result }) => {
  if (!result.success) {
    return (
      <div className="text-sm text-red-600 dark:text-red-400 mt-2">
        {result.error || '搜索失败'}
      </div>
    );
  }

  const { results = [], result_count = 0 } = result;

  if (results.length === 0) {
    return (
      <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">
        未找到搜索结果
      </div>
    );
  }

  return (
    <div className="mt-3 space-y-2">
      <div className="text-xs font-medium text-gray-700 dark:text-gray-300">
        找到 {result_count} 条结果
      </div>

      {/* Show top 3 results */}
      <div className="space-y-2">
        {results.slice(0, 3).map((item, idx) => (
          <div
            key={idx}
            className="text-sm border-l-2 border-blue-300 dark:border-blue-700 pl-3 py-1"
          >
            <div className="flex items-start gap-2">
              <span className="font-medium text-gray-700 dark:text-gray-300 flex-shrink-0">
                {item.position}.
              </span>
              <div className="flex-1 min-w-0">
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 dark:text-blue-400 hover:underline font-medium flex items-center gap-1 break-words"
                >
                  {item.title}
                  <ExternalLink className="w-3 h-3 flex-shrink-0" />
                </a>
                {item.content && (
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                    {item.content}
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Show more indicator */}
      {results.length > 3 && (
        <div className="text-xs text-gray-500 dark:text-gray-500 italic">
          还有 {results.length - 3} 条结果...
        </div>
      )}
    </div>
  );
};

const WebsiteAnalysisResults = ({ result }) => {
  if (!result.success) {
    return (
      <div className="text-sm text-red-600 dark:text-red-400 mt-2">
        {result.error || '网站分析失败'}
      </div>
    );
  }

  const {
    title,
    description,
    final_url,
    content,
    links = [],
    images = [],
    language,
    content_length,
  } = result;

  return (
    <div className="mt-3 space-y-3">
      {/* Title */}
      {title && (
        <div>
          <div className="text-xs font-medium text-gray-500 dark:text-gray-500 mb-1">
            标题
          </div>
          <div className="text-sm font-medium text-gray-800 dark:text-gray-200">
            {title}
          </div>
        </div>
      )}

      {/* URL */}
      {final_url && (
        <div>
          <div className="text-xs font-medium text-gray-500 dark:text-gray-500 mb-1">
            网址
          </div>
          <a
            href={final_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-roots-600 dark:text-roots-400 hover:underline flex items-center gap-1 break-all"
          >
            {final_url}
            <ExternalLink className="w-3 h-3 flex-shrink-0" />
          </a>
        </div>
      )}

      {/* Description */}
      {description && (
        <div>
          <div className="text-xs font-medium text-gray-500 dark:text-gray-500 mb-1">
            描述
          </div>
          <div className="text-sm text-gray-700 dark:text-gray-300">
            {description}
          </div>
        </div>
      )}

      {/* Content Preview */}
      {content && (
        <div>
          <div className="text-xs font-medium text-gray-500 dark:text-gray-500 mb-1">
            内容预览 ({content_length} 字符)
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-2 rounded max-h-32 overflow-y-auto">
            {content.substring(0, 300)}
            {content.length > 300 && '...'}
          </div>
        </div>
      )}

      {/* Links */}
      {links.length > 0 && (
        <div>
          <div className="text-xs font-medium text-gray-500 dark:text-gray-500 mb-1">
            主要链接 ({links.length})
          </div>
          <div className="space-y-1">
            {links.slice(0, 5).map((link, idx) => (
              <div key={idx} className="text-xs">
                <a
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-roots-600 dark:text-roots-400 hover:underline flex items-center gap-1"
                >
                  <ExternalLink className="w-3 h-3 flex-shrink-0" />
                  <span className="truncate">{link.text}</span>
                </a>
              </div>
            ))}
            {links.length > 5 && (
              <div className="text-xs text-gray-500 dark:text-gray-500 italic">
                还有 {links.length - 5} 个链接...
              </div>
            )}
          </div>
        </div>
      )}

      {/* Images */}
      {images.length > 0 && (
        <div>
          <div className="text-xs font-medium text-gray-500 dark:text-gray-500 mb-1">
            图片 ({images.length})
          </div>
          <div className="grid grid-cols-4 gap-2">
            {images.slice(0, 4).map((img, idx) => (
              <div key={idx} className="relative group">
                <img
                  src={img.src}
                  alt={img.alt || `Image ${idx + 1}`}
                  className="w-full h-16 object-cover rounded border border-gray-200 dark:border-gray-700"
                  loading="lazy"
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
              </div>
            ))}
          </div>
          {images.length > 4 && (
            <div className="text-xs text-gray-500 dark:text-gray-500 italic mt-1">
              还有 {images.length - 4} 张图片...
            </div>
          )}
        </div>
      )}

      {/* Language */}
      {language && language !== 'unknown' && (
        <div className="text-xs text-gray-500 dark:text-gray-500">
          语言: {language}
        </div>
      )}
    </div>
  );
};

export default ToolCallDisplay;
