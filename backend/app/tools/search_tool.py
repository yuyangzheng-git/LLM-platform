"""
DuckDuckGo web search tool
使用 ddgs 库进行搜索
"""
import logging
from typing import Dict, Any, List
from ddgs import DDGS
from .schemas import ToolDefinition, ToolParameter, ToolParameterType
from .registry import tool_registry

logger = logging.getLogger(__name__)


async def search_web(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    使用DuckDuckGo搜索网络

    Args:
        query: 搜索查询字符串
        max_results: 返回的最大结果数（默认5）

    Returns:
        包含搜索结果的字典，包括成功状态、查询、结果数和结果列表
    """
    try:
        logger.info(f"Searching DuckDuckGo with query: {query}")

        # 使用 duckduckgo_search 库进行搜索
        with DDGS() as ddgs:
            search_results = list(ddgs.text(
                query,
                max_results=max_results,
                region='wt-wt',  # 全球搜索
                safesearch='moderate'
            ))

        if not search_results:
            logger.warning(f"No results found for query: {query}")
            return {
                "success": False,
                "query": query,
                "error": "未找到搜索结果，请尝试不同的关键词"
            }

        # 格式化结果
        results = []
        for idx, result in enumerate(search_results, 1):
            results.append({
                "position": idx,
                "title": result.get('title', ''),
                "url": result.get('href', ''),
                "content": result.get('body', ''),
            })

        # 生成结果摘要
        summary = f"找到 {len(results)} 条搜索结果:\n\n"
        for i, result in enumerate(results[:3], 1):
            summary += f"{i}. {result['title']}\n"
            summary += f"   {result['url']}\n"
            if result['content']:
                summary += f"   {result['content'][:100]}...\n"
            summary += "\n"

        logger.info(f"✅ Search successful: {query} ({len(results)} results)")

        return {
            "success": True,
            "query": query,
            "result_count": len(results),
            "results": results,
            "summary": summary
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Search failed: {query} - {error_msg}")

        return {
            "success": False,
            "query": query,
            "error": f"搜索失败: {error_msg}"
        }


def register_search_tool():
    """注册搜索工具到工具注册表"""
    tool_def = ToolDefinition(
        name="web_search",
        description="在网络上搜索信息。使用DuckDuckGo搜索引擎返回相关网页结果。适用于需要最新信息、实时数据或网络内容的问题。",
        parameters=[
            ToolParameter(
                name="query",
                type=ToolParameterType.STRING,
                description="要搜索的查询字符串",
                required=True
            ),
            ToolParameter(
                name="max_results",
                type=ToolParameterType.INTEGER,
                description="返回的最大结果数（默认5，最多10）",
                required=False
            )
        ],
        function=search_web
    )

    tool_registry.register_tool(tool_def)
    logger.info("✅ Search tool (DuckDuckGo) registered successfully")
