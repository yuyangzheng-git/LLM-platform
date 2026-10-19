import { useState } from 'react'
import { useToast } from '../../hooks/custom/useToast'
import { downloadFile } from '../../utils/download'
import { Wand2, Download, Loader2, Image as ImageIcon } from 'lucide-react'
import { IMAGE_MODELS } from '../../config/generationModels'

export function ImageGeneration() {
  const { showToast } = useToast()
  const [prompt, setPrompt] = useState('')
  const [selectedModel, setSelectedModel] = useState('dall-e-3')
  const [size, setSize] = useState('1024x1024')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedImages, setGeneratedImages] = useState([])

  const currentModel = IMAGE_MODELS.find(m => m.id === selectedModel)

  const handleGenerate = async () => {
    if (!prompt.trim()) return

    setIsGenerating(true)
    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL !== undefined ? import.meta.env.VITE_API_BASE_URL : 'http://localhost:3211'
      const response = await fetch(`${API_BASE_URL}/api/v1/generation/image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: selectedModel,
          prompt: prompt,
          size: size,
        }),
      })

      if (!response.ok) {
        const body = await response.json().catch(() => null)
        throw new Error(body?.detail || `HTTP ${response.status}`)
      }

      const data = await response.json()
      setGeneratedImages((prev) => [data, ...prev])
    } catch (error) {
      console.error('Image generation error:', error)
      showToast(`图片生成失败：${error.message}`)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleDownload = async (imageUrl, index) => {
    const result = await downloadFile(imageUrl, `generated-image-${Date.now()}-${index}.png`)
    if (result === 'opened') {
      showToast('已在新标签页打开，可在那里保存文件', 'info')
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* Input Area */}
      <div className="flex-shrink-0 p-4 sm:p-6 md:p-8 bg-white/50 dark:bg-bg-secondary/50 backdrop-blur-xl border-b border-border-primary">
        <div className="max-w-4xl mx-auto space-y-4">
          {/* Prompt Input */}
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              图片描述提示词
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="描述你想生成的图片，越详细越好..."
              className="w-full px-4 py-3 bg-white dark:bg-bg-tertiary border-2 border-border-primary rounded-xl focus:border-orange-400 dark:focus:border-amber-400 outline-none resize-none text-text-primary placeholder-text-tertiary"
              rows={3}
            />
          </div>

          {/* Settings Row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Model Select */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                模型
              </label>
              <select
                value={selectedModel}
                onChange={(e) => {
                  setSelectedModel(e.target.value)
                  const model = IMAGE_MODELS.find(m => m.id === e.target.value)
                  if (model && model.sizes.length > 0) {
                    setSize(model.sizes[0])
                  }
                }}
                className="w-full px-3 py-2 bg-white dark:bg-bg-tertiary border-2 border-border-primary rounded-lg focus:border-orange-400 dark:focus:border-amber-400 outline-none text-text-primary"
              >
                {IMAGE_MODELS.map((model) => (
                  <option key={model.id} value={model.id}>
                    {model.name} ({model.provider})
                  </option>
                ))}
              </select>
            </div>

            {/* Size Select */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                尺寸
              </label>
              <select
                value={size}
                onChange={(e) => setSize(e.target.value)}
                className="w-full px-3 py-2 bg-white dark:bg-bg-tertiary border-2 border-border-primary rounded-lg focus:border-orange-400 dark:focus:border-amber-400 outline-none text-text-primary"
              >
                {currentModel?.sizes.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>

            {/* Generate Button */}
            <div className="flex items-end">
              <button
                onClick={handleGenerate}
                disabled={isGenerating || !prompt.trim()}
                className="w-full px-6 py-2 bg-gradient-main hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg font-medium flex items-center justify-center space-x-2 transition-all shadow-lg hover:shadow-xl"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>生成中...</span>
                  </>
                ) : (
                  <>
                    <Wand2 className="w-5 h-5" />
                    <span>生成图片</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Gallery Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 md:p-8">
        <div className="max-w-6xl mx-auto">
          {generatedImages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <ImageIcon className="w-20 h-20 text-text-tertiary mb-4" />
              <p className="text-text-secondary text-lg font-medium">还没有生成图片</p>
              <p className="text-text-tertiary text-sm mt-2">输入提示词开始创作吧</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {generatedImages.map((img, index) => (
                <div
                  key={index}
                  className="group bg-white dark:bg-bg-secondary rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all border border-border-primary"
                >
                  <div className="relative aspect-square">
                    <img
                      src={img.url}
                      alt={img.prompt}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
                      <button
                        onClick={() => handleDownload(img.url, index)}
                        className="px-4 py-2 bg-white text-gray-900 rounded-lg font-medium flex items-center space-x-2 shadow-lg hover:bg-gray-100 transition-all"
                      >
                        <Download className="w-4 h-4" />
                        <span>下载</span>
                      </button>
                    </div>
                  </div>
                  <div className="p-4">
                    <p className="text-sm text-text-secondary line-clamp-2">
                      {img.prompt}
                    </p>
                    <div className="mt-2 flex items-center justify-between text-xs text-text-tertiary">
                      <span>{img.model}</span>
                      <span>{img.size}</span>
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
