"""
网页分析工具
提供URL抓取和内容分析功能
"""

import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, List
import logging
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)

# 请求头
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

async def analyze_website(url: str, max_content_length: int = 5000) -> Dict[str, Any]:
    """
    分析网站内容

    Args:
        url: 要分析的网站URL
        max_content_length: 最大内容长度（字符数）

    Returns:
        包含网站信息的字典
    """
    try:
        logger.info(f"开始分析网站: {url}")

        # 验证URL格式
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = f"https://{url}"
            parsed_url = urlparse(url)

        if not parsed_url.netloc:
            return {
                "success": False,
                "error": "无效的URL格式",
                "url": url
            }

        # 发送请求
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

        # 检查内容类型
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
            return {
                "success": False,
                "error": f"不支持的内容类型: {content_type}",
                "url": url
            }

        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 移除脚本和样式标签
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # 提取标题
        title = ""
        if soup.title:
            title = soup.title.get_text().strip()
        elif soup.find('h1'):
            title = soup.find('h1').get_text().strip()

        # 提取描述
        description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            description = meta_desc.get('content').strip()
        elif soup.find('meta', attrs={'property': 'og:description'}):
            og_desc = soup.find('meta', attrs={'property': 'og:description'})
            if og_desc and og_desc.get('content'):
                description = og_desc.get('content').strip()

        # 提取关键词
        keywords = []
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            keywords = [k.strip() for k in meta_keywords.get('content').split(',')]

        # 提取主要内容
        main_content = ""

        # 尝试查找主要内容区域
        main_selectors = [
            soup.find('main'),
            soup.find('article'),
            soup.find('div', class_=re.compile(r'content|main|article|post', re.I)),
            soup.find('div', id=re.compile(r'content|main|article|post', re.I)),
        ]

        main_element = None
        for selector in main_selectors:
            if selector:
                main_element = selector
                break

        if main_element:
            # 提取文本内容
            paragraphs = main_element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
            texts = []
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 20:  # 过滤太短的内容
                    texts.append(text)
            main_content = '\n\n'.join(texts)
        else:
            # 如果找不到主要内容区域，使用body
            body = soup.find('body')
            if body:
                main_content = body.get_text(separator='\n', strip=True)

        # 清理内容
        main_content = re.sub(r'\n{3,}', '\n\n', main_content)  # 移除多余空行
        main_content = re.sub(r' {2,}', ' ', main_content)  # 移除多余空格

        # 限制内容长度
        if len(main_content) > max_content_length:
            main_content = main_content[:max_content_length] + "...\n\n[内容已截断]"

        # 提取主要链接
        links = []
        for link in soup.find_all('a', href=True, limit=20):
            href = link.get('href')
            text = link.get_text().strip()

            if href and text and len(text) > 3:
                # 转换为绝对URL
                absolute_url = urljoin(url, href)

                # 过滤掉某些类型的链接
                if not any(x in absolute_url.lower() for x in ['javascript:', 'mailto:', '#', 'tel:']):
                    links.append({
                        "text": text[:100],  # 限制长度
                        "url": absolute_url
                    })

        # 提取图片
        images = []
        for img in soup.find_all('img', src=True, limit=10):
            src = img.get('src')
            alt = img.get('alt', '')

            if src:
                absolute_src = urljoin(url, src)
                images.append({
                    "src": absolute_src,
                    "alt": alt[:100]
                })

        # 构建结果
        result = {
            "success": True,
            "url": url,
            "final_url": str(response.url),  # 处理重定向后的最终URL
            "title": title,
            "description": description,
            "keywords": keywords[:10],  # 限制关键词数量
            "content": main_content,
            "content_length": len(main_content),
            "links": links[:15],  # 限制链接数量
            "images": images[:8],  # 限制图片数量
            "language": soup.find('html').get('lang', 'unknown') if soup.find('html') else 'unknown',
        }

        logger.info(f"✅ 网站分析成功: {url} (标题: {title})")
        return result

    except httpx.TimeoutException:
        logger.error(f"❌ 网站分析超时: {url}")
        return {
            "success": False,
            "error": "请求超时，网站响应时间过长",
            "url": url
        }
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ HTTP错误: {url} - {e.response.status_code}")
        return {
            "success": False,
            "error": f"HTTP错误 {e.response.status_code}",
            "url": url
        }
    except Exception as e:
        logger.error(f"❌ 网站分析失败: {url} - {str(e)}")
        return {
            "success": False,
            "error": f"分析失败: {str(e)}",
            "url": url
        }


def register_web_scraper_tool():
    """注册网页分析工具"""
    from .registry import tool_registry
    from .schemas import ToolDefinition, ToolParameter, ToolParameterType

    tool_def = ToolDefinition(
        name="analyze_website",
        description="分析网站内容，提取标题、描述、主要文本、链接和图片等信息。适用于用户提供URL并想了解网站内容的情况。",
        parameters=[
            ToolParameter(
                name="url",
                type=ToolParameterType.STRING,
                description="要分析的网站URL（例如: https://example.com 或 example.com）",
                required=True
            ),
            ToolParameter(
                name="max_content_length",
                type=ToolParameterType.INTEGER,
                description="返回内容的最大长度（字符数），默认5000",
                required=False
            )
        ],
        function=analyze_website
    )

    tool_registry.register_tool(tool_def)
    logger.info("✅ Web scraper tool registered successfully")
