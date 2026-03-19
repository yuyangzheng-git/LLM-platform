#!/usr/bin/env python3
"""
测试网站分析工具
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.tools.web_scraper_tool import analyze_website


async def test_analyze():
    """测试网站分析功能"""

    test_urls = [
        "https://www.example.com",
        "https://www.python.org",
        "baidu.com",  # 测试自动添加https://
    ]

    print("🧪 测试网站分析工具\n")
    print("=" * 60)

    for url in test_urls:
        print(f"\n📝 测试URL: {url}")
        print("-" * 60)

        result = await analyze_website(url, max_content_length=500)

        if result['success']:
            print(f"✅ 分析成功")
            print(f"   标题: {result.get('title', 'N/A')}")
            print(f"   最终URL: {result.get('final_url', 'N/A')}")
            print(f"   描述: {result.get('description', 'N/A')[:100]}...")
            print(f"   内容长度: {result.get('content_length', 0)} 字符")
            print(f"   链接数: {len(result.get('links', []))}")
            print(f"   图片数: {len(result.get('images', []))}")
            print(f"   语言: {result.get('language', 'unknown')}")

            # 显示前3个链接
            if result.get('links'):
                print(f"\n   主要链接:")
                for i, link in enumerate(result['links'][:3], 1):
                    print(f"     {i}. {link['text'][:50]}")
                    print(f"        {link['url'][:80]}")
        else:
            print(f"❌ 分析失败: {result.get('error', 'Unknown error')}")

        print()

    print("=" * 60)
    print("✅ 测试完成")


if __name__ == "__main__":
    asyncio.run(test_analyze())
