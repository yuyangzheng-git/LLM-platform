// 精选顶级模型配置 - 2026年3月
export const TOP_MODELS = [
  // === 顶级对话模型 ===
  { id: 'gpt-4o', name: 'GPT-4o', provider: 'OpenAI' },
  { id: 'gpt-5.4-pro', name: 'GPT-5.4 Pro', provider: 'OpenAI' },
  { id: 'claude-opus-4-6', name: 'Claude Opus 4.6', provider: 'Anthropic' },
  { id: 'gemini-3.1-pro-preview', name: 'Gemini 3.1 Pro', provider: 'Google' },

  // === 深度推理模型 ===
  { id: 'o3', name: 'O3 (深度推理)', provider: 'OpenAI' },
  { id: 'deepseek-r1-0528', name: 'DeepSeek R1', provider: 'DeepSeek' },

  // === 其他顶级模型 ===
  { id: 'grok-4.1', name: 'Grok 4.1', provider: 'xAI' },
]

// Friendly name for a model id; falls back to the id for models not listed
export function modelDisplayName(modelId) {
  return TOP_MODELS.find((m) => m.id === modelId)?.name || modelId
}
