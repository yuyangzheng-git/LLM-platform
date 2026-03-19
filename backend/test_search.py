"""
测试DuckDuckGo搜索功能
运行: python test_search.py
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.tools.search_tool import search_web


async def test_search():
    """测试搜索功能"""

    print("=" * 60)
    print("DuckDuckGo搜索工具测试")
    print("=" * 60)
    print()

    # 测试1: 基本搜索
    print("测试1: 搜索 'Python programming'")
    print("-" * 60)
    result = await search_web("Python programming", max_results=3)

    if result['success']:
        print(f"✅ 搜索成功")
        print(f"查询: {result['query']}")
        print(f"结果数: {result['result_count']}")
        print()
        print("结果:")
        for item in result['results']:
            print(f"\n{item['position']}. {item['title']}")
            print(f"   URL: {item['url']}")
            print(f"   摘要: {item['content'][:100]}...")
    else:
        print(f"❌ 搜索失败: {result.get('error', '未知错误')}")

    print("\n" + "=" * 60)

    # 测试2: 中文搜索
    print("\n测试2: 搜索 'AI新闻'")
    print("-" * 60)
    result2 = await search_web("AI新闻", max_results=3)

    if result2['success']:
        print(f"✅ 搜索成功")
        print(f"查询: {result2['query']}")
        print(f"结果数: {result2['result_count']}")
        print()
        print("结果:")
        for item in result2['results']:
            print(f"\n{item['position']}. {item['title']}")
            print(f"   URL: {item['url']}")
            print(f"   摘要: {item['content'][:100]}...")
    else:
        print(f"❌ 搜索失败: {result2.get('error', '未知错误')}")

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_search())
