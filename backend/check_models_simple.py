import os
from openai import OpenAI

# Read from .env
api_key = None
api_base_url = None

env_file = '/Users/2812019221qq.com/llm-chat-platform/backend/.env'
with open(env_file, 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith('OPENAI_API_KEY='):
            api_key = line.split('=', 1)[1].strip('"')
        elif line.startswith('OPENAI_API_BASE_URL='):
            api_base_url = line.split('=', 1)[1].strip('"')

if not api_key or not api_base_url:
    print("Failed to read API credentials from .env")
    exit(1)

# Initialize client
client = OpenAI(
    api_key=api_key,
    base_url=api_base_url
)

# Get all available models
try:
    models_response = client.models.list()
    all_models = [model.id for model in models_response.data]

    print(f"总共 {len(all_models)} 个模型\n")

    # Check if our configured models exist
    configured_models = [
        'gpt-4o',
        'gpt-5.4-pro',
        'claude-opus-4-6',
        'gemini-3.1-pro-preview',
        'o3',
        'deepseek-r1-0528',
        'grok-4.1'
    ]

    print("检查配置的模型是否存在:\n")
    for model_id in configured_models:
        exists = model_id in all_models
        status = "✓ 存在" if exists else "✗ 不存在"
        print(f"{status}: {model_id}")

    # Find actually available top models
    print("\n\n实际可用的顶级模型:")

    # GPT models
    gpt_models = [m for m in all_models if 'gpt' in m.lower()]
    print(f"\nGPT 系列 ({len(gpt_models)} 个):")
    for m in sorted(gpt_models)[:20]:
        print(f"  - {m}")

    # Claude models
    claude_models = [m for m in all_models if 'claude' in m.lower()]
    print(f"\nClaude 系列 ({len(claude_models)} 个):")
    for m in sorted(claude_models)[:20]:
        print(f"  - {m}")

    # Gemini models
    gemini_models = [m for m in all_models if 'gemini' in m.lower()]
    print(f"\nGemini 系列 ({len(gemini_models)} 个):")
    for m in sorted(gemini_models)[:20]:
        print(f"  - {m}")

    # DeepSeek models
    deepseek_models = [m for m in all_models if 'deepseek' in m.lower()]
    print(f"\nDeepSeek 系列 ({len(deepseek_models)} 个):")
    for m in sorted(deepseek_models)[:20]:
        print(f"  - {m}")

except Exception as e:
    print(f"Error: {e}")
