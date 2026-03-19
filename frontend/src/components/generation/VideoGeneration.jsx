import { useState } from 'react'
import { Video, Download, Loader2, Play } from 'lucide-react'
import { VIDEO_MODELS } from '../../config/generationModels'

export function VideoGeneration() {
  const [prompt, setPrompt] = useState('')
  const [selectedModel, setSelectedModel] = useState('sora-2')
  const [duration, setDuration] = useState('5s')
  const [resolution, setResolution] = useState('720p')
  const [aspectRatio, setAspectRatio] = useState('16:9')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedVideos, setGeneratedVideos] = useState([])

  const currentModel = VIDEO_MODELS.find(m => m.id === selectedModel)

  const handleGenerate = async () => {
    if (!prompt.trim()) return

    setIsGenerating(true)
    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL !== undefined ? import.meta.env.VITE_API_BASE_URL : 'http://localhost:3211'
      const response = await fetch(`${API_BASE_URL}/api/v1/generation/video`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: selectedModel,
          prompt: prompt,
          duration: duration,
          resolution: resolution,
          aspect_ratio: aspectRatio,
        }),
      })

      if (!response.ok) {
        throw new Error(`生成失败: ${response.status}`)
      }

      const data = await response.json()
      setGeneratedVideos([data, ...generatedVideos])
    } catch (error) {
      console.error('Video generation error:', error)
      alert('视频生成失败: ' + error.message)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleDownload = (videoUrl, index) => {
    const link = document.createElement('a')
    link.href = videoUrl
    link.download = `generated-video-${Date.now()}-${index}.mp4`
    link.click()
  }

  return (
    <div className="h-full flex flex-col">
      {/* Input Area */}
      <div className="flex-shrink-0 p-4 sm:p-6 md:p-8 bg-white/50 dark:bg-bg-secondary/50 backdrop-blur-xl border-b border-border-primary">
        <div className="max-w-4xl mx-auto space-y-4">
          {/* Prompt Input */}
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              视频描述提示词
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="描述你想生成的视频场景，越详细越好..."
              className="w-full px-4 py-3 bg-white dark:bg-bg-tertiary border-2 border-border-primary rounded-xl focus:border-orange-400 dark:focus:border-amber-400 outline-none resize-none text-text-primary placeholder-text-tertiary"
              rows={3}
            />
          </div>

          {/* Settings Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {/* Model Select */}
            <div className="lg:col-span-2">
              <label className="block text-sm font-medium text-text-primary mb-2">
                模型
              </label>
              <select
                value={selectedModel}
                onChange={(e) => {
                  setSelectedModel(e.target.value)
                  const model = VIDEO_MODELS.find(m => m.id === e.target.value)
                  if (model) {
                    if (model.durations.length > 0) setDuration(model.durations[0])
                    if (model.resolutions.length > 0) setResolution(model.resolutions[0])
                    if (model.aspectRatios.length > 0) setAspectRatio(model.aspectRatios[0])
                  }
                }}
                className="w-full px-3 py-2 bg-white dark:bg-bg-tertiary border-2 border-border-primary rounded-lg focus:border-orange-400 dark:focus:border-amber-400 outline-none text-text-primary"
              >
                {VIDEO_MODELS.map((model) => (
                  <option key={model.id} value={model.id}>
                    {model.name} ({model.provider})
                  </option>
                ))}
              </select>
            </div>

            {/* Duration Select */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                时长
              </label>
              <select
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                className="w-full px-3 py-2 bg-white dark:bg-bg-tertiary border-2 border-border-primary rounded-lg focus:border-orange-400 dark:focus:border-amber-400 outline-none text-text-primary"
              >
                {currentModel?.durations.map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>

            {/* Resolution Select */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                分辨率
              </label>
              <select
                value={resolution}
                onChange={(e) => setResolution(e.target.value)}
                className="w-full px-3 py-2 bg-white dark:bg-bg-tertiary border-2 border-border-primary rounded-lg focus:border-orange-400 dark:focus:border-amber-400 outline-none text-text-primary"
              >
                {currentModel?.resolutions.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>

            {/* Aspect Ratio Select */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                宽高比
              </label>
              <select
                value={aspectRatio}
                onChange={(e) => setAspectRatio(e.target.value)}
                className="w-full px-3 py-2 bg-white dark:bg-bg-tertiary border-2 border-border-primary rounded-lg focus:border-orange-400 dark:focus:border-amber-400 outline-none text-text-primary"
              >
                {currentModel?.aspectRatios.map((ar) => (
                  <option key={ar} value={ar}>{ar}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Generate Button */}
          <div className="flex justify-center">
            <button
              onClick={handleGenerate}
              disabled={isGenerating || !prompt.trim()}
              className="px-8 py-3 bg-gradient-main hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl font-medium flex items-center justify-center space-x-2 transition-all shadow-lg hover:shadow-xl"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>生成中...（可能需要1-3分钟）</span>
                </>
              ) : (
                <>
                  <Video className="w-5 h-5" />
                  <span>生成视频</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Gallery Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 md:p-8">
        <div className="max-w-6xl mx-auto">
          {generatedVideos.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Play className="w-20 h-20 text-text-tertiary mb-4" />
              <p className="text-text-secondary text-lg font-medium">还没有生成视频</p>
              <p className="text-text-tertiary text-sm mt-2">输入提示词开始创作吧</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {generatedVideos.map((vid, index) => (
                <div
                  key={index}
                  className="group bg-white dark:bg-bg-secondary rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all border border-border-primary"
                >
                  <div className="relative aspect-video bg-black">
                    <video
                      src={vid.url}
                      controls
                      className="w-full h-full object-contain"
                      preload="metadata"
                    >
                      您的浏览器不支持视频播放
                    </video>
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-all">
                      <button
                        onClick={() => handleDownload(vid.url, index)}
                        className="px-3 py-2 bg-white text-gray-900 rounded-lg font-medium flex items-center space-x-2 shadow-lg hover:bg-gray-100 transition-all text-sm"
                      >
                        <Download className="w-4 h-4" />
                        <span>下载</span>
                      </button>
                    </div>
                  </div>
                  <div className="p-4">
                    <p className="text-sm text-text-secondary line-clamp-2">
                      {vid.prompt}
                    </p>
                    <div className="mt-2 flex items-center justify-between text-xs text-text-tertiary">
                      <span>{vid.model}</span>
                      <span>{vid.duration} • {vid.resolution}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
