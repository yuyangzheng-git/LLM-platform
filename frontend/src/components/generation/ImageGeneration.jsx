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
    <div className="scroll-area h-full overflow-y-auto pb-[env(safe-area-inset-bottom)]">
      {/* Input Area */}
      <div className="px-3 pt-3 sm:px-6 sm:pt-6 md:px-8 md:pt-8">
        <div className="max-w-4xl mx-auto space-y-4 bg-glass backdrop-blur-xl border border-border-primary/80 rounded-[1.75rem] shadow-paper p-4 sm:p-6">
          {/* Prompt Input */}
          <div>
            <label className="block text-sm font-display font-semibold text-text-primary mb-2">
              图片描述提示词
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="描述你想生成的图片，越详细越好..."
              className="w-full px-4 py-3 bg-cream/80 dark:bg-bg-tertiary/80 border border-border-primary rounded-2xl focus:border-roots-300 focus:ring-4 focus:ring-roots-100/70 dark:focus:border-road-500 dark:focus:ring-road-900/40 outline-none resize-none text-text-primary placeholder-text-tertiary"
              rows={3}
            />
          </div>

          {/* Settings Row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Model Select */}
            <div>
              <label className="block text-sm font-display font-semibold text-text-primary mb-2">
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
                className="w-full px-3 py-2 bg-cream/80 dark:bg-bg-tertiary/80 border border-border-primary rounded-2xl focus:border-roots-300 focus:ring-4 focus:ring-roots-100/70 dark:focus:border-road-500 dark:focus:ring-road-900/40 outline-none text-text-primary"
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
              <label className="block text-sm font-display font-semibold text-text-primary mb-2">
                尺寸
              </label>
              <select
                value={size}
                onChange={(e) => setSize(e.target.value)}
                className="w-full px-3 py-2 bg-cream/80 dark:bg-bg-tertiary/80 border border-border-primary rounded-2xl focus:border-roots-300 focus:ring-4 focus:ring-roots-100/70 dark:focus:border-road-500 dark:focus:ring-road-900/40 outline-none text-text-primary"
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
                className="w-full px-6 py-2 bg-roots-500 hover:bg-roots-600 disabled:bg-border-secondary/70 disabled:text-text-tertiary dark:disabled:bg-bg-tertiary disabled:cursor-not-allowed text-cream rounded-full font-display font-semibold flex items-center justify-center space-x-2 transition-all shadow-glow-roots disabled:shadow-none"
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
      <div className="p-3 sm:p-6 md:p-8">
        <div className="max-w-6xl mx-auto">
          {generatedImages.length === 0 ? (
            <div className="flex flex-col items-center justify-center text-center py-8 md:py-16">
              <div className="bg-cream/70 dark:bg-bg-secondary/70 backdrop-blur-md rounded-[1.75rem] px-10 py-8 shadow-paper border border-border-primary/70 flex flex-col items-center">
              <ImageIcon className="w-20 h-20 text-text-tertiary mb-4" />
              <p className="font-display text-text-primary text-lg font-semibold">还没有生成图片</p>
              <p className="text-text-secondary text-sm mt-2">输入提示词开始创作吧</p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {generatedImages.map((img, index) => (
                <div
                  key={index}
                  className="group bg-glass backdrop-blur-xl rounded-[1.5rem] overflow-hidden shadow-paper hover:shadow-xl hover:-translate-y-0.5 transition-all border border-border-primary/80"
                >
                  <div className="relative aspect-square">
                    <img
                      src={img.url}
                      alt={img.prompt}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 transition-all flex items-end justify-end p-2 md:p-0 md:items-center md:justify-center md:bg-black/0 md:group-hover:bg-black/40 opacity-100 md:opacity-0 md:group-hover:opacity-100 md:focus-within:opacity-100">
                      <button
                        onClick={() => handleDownload(img.url, index)}
                        className="touch-target px-4 py-2 bg-cream/95 text-ink rounded-full font-display font-semibold flex items-center space-x-2 shadow-paper hover:bg-cream transition-all"
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
