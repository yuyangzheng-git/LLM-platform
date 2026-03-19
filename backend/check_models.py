import asyncio
import sys
sys.path.insert(0, '/Users/2812019221qq.com/llm-chat-platform/backend')

from app.database import get_db
from app.models.model_config import ModelConfig
from sqlalchemy import select
from openai import AsyncOpenAI
import json

async def check_models():
    # Get database session
    async for db in get_db():
        try:
            # Get OpenAI config
            query = select(ModelConfig).where(ModelConfig.provider == 'openai')
            result = await db.execute(query)
            config = result.scalar_one_or_none()
            
            if not config:
                print("No OpenAI config found")
                return
            
            # Decrypt API key
            from app.api.models import decrypt_api_key
            api_key = decrypt_api_key(config.api_key)
            
            print(f"Using base URL: {config.api_base_url}")
            print("=" * 80)
            
            # Create client
            client = AsyncOpenAI(
                api_key=api_key,
                base_url=config.api_base_url or "https://api.openai.com/v1"
            )
            
            # List models
            models = await client.models.list()
            
            # Sort by ID
            model_list = sorted([m.id for m in models.data])
            
            print(f"\n找到 {len(model_list)} 个模型：\n")
            
            # Group by category
            openai_models = [m for m in model_list if m.startswith(('gpt', 'o1', 'text-', 'davinci', 'babbage', 'curie'))]
            claude_models = [m for m in model_list if 'claude' in m.lower()]
            gemini_models = [m for m in model_list if 'gemini' in m.lower()]
            deepseek_models = [m for m in model_list if 'deepseek' in m.lower()]
            grok_models = [m for m in model_list if 'grok' in m.lower()]
            other_models = [m for m in model_list if m not in openai_models + claude_models + gemini_models + deepseek_models + grok_models]
            
            if openai_models:
                print("🔷 OpenAI 模型：")
                for m in openai_models:
                    print(f"  - {m}")
                print()
            
            if claude_models:
                print("🟣 Claude 模型：")
                for m in claude_models:
                    print(f"  - {m}")
                print()
            
            if gemini_models:
                print("🔴 Gemini 模型：")
                for m in gemini_models:
                    print(f"  - {m}")
                print()
            
            if deepseek_models:
                print("🔵 DeepSeek 模型：")
                for m in deepseek_models:
                    print(f"  - {m}")
                print()
            
            if grok_models:
                print("⚫ Grok 模型：")
                for m in grok_models:
                    print(f"  - {m}")
                print()
            
            if other_models:
                print("🟡 其他模型：")
                for m in other_models:
                    print(f"  - {m}")
                print()
            
            print("=" * 80)
            print(f"总计：{len(model_list)} 个模型")
            
        except Exception as e:
            print(f"错误：{e}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()
        break

if __name__ == '__main__':
    asyncio.run(check_models())
