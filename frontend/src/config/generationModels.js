// 图片生成模型配置
export const IMAGE_MODELS = [
  // DALL-E
  { id: 'dall-e-3', name: 'DALL-E 3', provider: 'OpenAI', sizes: ['1024x1024', '1024x1792', '1792x1024'] },
  { id: 'dall-e-2', name: 'DALL-E 2', provider: 'OpenAI', sizes: ['256x256', '512x512', '1024x1024'] },
  
  // Flux
  { id: 'flux-pro', name: 'Flux Pro', provider: 'Flux', sizes: ['1024x1024', '1024x1536', '1536x1024'] },
  { id: 'flux-1-dev', name: 'Flux 1 Dev', provider: 'Flux', sizes: ['1024x1024', '1024x1536', '1536x1024'] },
  { id: 'flux-schnell', name: 'Flux Schnell', provider: 'Flux', sizes: ['1024x1024'] },
  
  // Stable Diffusion
  { id: 'sd3.5-large', name: 'SD 3.5 Large', provider: 'Stability AI', sizes: ['1024x1024', '1152x896', '896x1152'] },
  { id: 'sd3.5-medium', name: 'SD 3.5 Medium', provider: 'Stability AI', sizes: ['1024x1024'] },
  
  // 其他
  { id: 'recraft-v3', name: 'Recraft V3', provider: 'Recraft', sizes: ['1024x1024', '1024x1536'] },
  { id: 'ideogram', name: 'Ideogram', provider: 'Ideogram', sizes: ['1024x1024'] },
]

// 视频生成模型配置
export const VIDEO_MODELS = [
  // Sora
  { id: 'sora-2', name: 'Sora 2', provider: 'OpenAI', durations: ['5s', '10s'], resolutions: ['480p', '720p'], aspectRatios: ['16:9', '9:16', '1:1'] },
  { id: 'sora-16:9-720p-5s', name: 'Sora 16:9 720p 5s', provider: 'OpenAI', durations: ['5s'], resolutions: ['720p'], aspectRatios: ['16:9'] },
  { id: 'sora-16:9-480p-10s', name: 'Sora 16:9 480p 10s', provider: 'OpenAI', durations: ['10s'], resolutions: ['480p'], aspectRatios: ['16:9'] },
  
  // Runway
  { id: 'runway-video', name: 'Runway Gen-3', provider: 'Runway', durations: ['5s', '10s'], resolutions: ['720p'], aspectRatios: ['16:9'] },
  { id: 'runway-vip-video', name: 'Runway Gen-3 VIP', provider: 'Runway', durations: ['5s', '10s'], resolutions: ['720p', '1080p'], aspectRatios: ['16:9'] },
  
  // Kling
  { id: 'kling-video-pro-10s', name: 'Kling Pro 10s', provider: 'Kling', durations: ['10s'], resolutions: ['1080p'], aspectRatios: ['16:9', '9:16', '1:1'] },
  { id: 'kling-video-pro-5s', name: 'Kling Pro 5s', provider: 'Kling', durations: ['5s'], resolutions: ['1080p'], aspectRatios: ['16:9', '9:16', '1:1'] },
  
  // Luma
  { id: 'luma-pro-video', name: 'Luma Dream Machine Pro', provider: 'Luma', durations: ['5s', '10s'], resolutions: ['720p'], aspectRatios: ['16:9'] },
  { id: 'luma-video', name: 'Luma Dream Machine', provider: 'Luma', durations: ['5s'], resolutions: ['720p'], aspectRatios: ['16:9'] },
  
  // Veo (Google)
  { id: 'veo3.1-pro', name: 'Veo 3.1 Pro', provider: 'Google', durations: ['5s', '10s'], resolutions: ['1080p'], aspectRatios: ['16:9', '9:16'] },
  { id: 'veo3', name: 'Veo 3', provider: 'Google', durations: ['5s'], resolutions: ['720p'], aspectRatios: ['16:9'] },
  
  // Pika
  { id: 'pika-1.5', name: 'Pika 1.5', provider: 'Pika', durations: ['3s', '5s'], resolutions: ['720p'], aspectRatios: ['16:9', '1:1'] },
]
