"""
地址位置工具
提供地理编码、地址查询、坐标转换等功能
使用OpenStreetMap Nominatim API（免费，无需API密钥）
"""
import httpx
import logging
from typing import Dict, Any, List
from .schemas import ToolDefinition, ToolParameter, ToolParameterType
from .registry import tool_registry

logger = logging.getLogger(__name__)

# Nominatim API配置
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
REQUEST_TIMEOUT = 10
USER_AGENT = "LLM-Chat-Platform/1.0"


async def geocode_address(
    address: str,
    language: str = "zh-CN",
    limit: int = 1
) -> Dict[str, Any]:
    """
    地理编码：将地址转换为坐标和详细信息

    Args:
        address: 要查询的地址（中文或英文）
        language: 返回语言，默认"zh-CN"（简体中文）
        limit: 返回结果数量限制（1-10）

    Returns:
        包含地址详细信息、坐标等的字典
    """
    try:
        # 构建请求参数
        params = {
            "q": address,
            "format": "json",
            "addressdetails": 1,
            "limit": min(max(limit, 1), 10),
            "accept-language": language
        }

        headers = {
            "User-Agent": USER_AGENT
        }

        logger.info(f"Geocoding address: {address}")

        # 发送请求
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(
                f"{NOMINATIM_BASE_URL}/search",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

        if not data:
            return {
                "success": False,
                "error": f"未找到地址 '{address}' 的信息"
            }

        # 格式化结果
        results = []
        for item in data:
            address_parts = item.get("address", {})

            result = {
                "display_name": item.get("display_name"),
                "latitude": float(item.get("lat", 0)),
                "longitude": float(item.get("lon", 0)),
                "type": item.get("type"),
                "importance": item.get("importance"),
                "address": {
                    "country": address_parts.get("country"),
                    "state": address_parts.get("state"),
                    "city": address_parts.get("city") or address_parts.get("town") or address_parts.get("village"),
                    "district": address_parts.get("suburb") or address_parts.get("district"),
                    "street": address_parts.get("road"),
                    "postcode": address_parts.get("postcode"),
                }
            }
            results.append(result)

        # 构建格式化摘要
        main_result = results[0]
        summary = f"地址: {main_result['display_name']}\n"
        summary += f"坐标: {main_result['latitude']}, {main_result['longitude']}\n"
        summary += f"类型: {main_result['type']}"

        logger.info(f"Geocoding successful: {main_result['display_name']}")

        return {
            "success": True,
            "query": address,
            "result_count": len(results),
            "results": results,
            "summary": summary
        }

    except httpx.TimeoutException:
        error_msg = f"地址查询超时（{REQUEST_TIMEOUT}秒）"
        logger.error(error_msg)
        return {
            "success": False,
            "query": address,
            "error": error_msg
        }

    except httpx.HTTPStatusError as e:
        error_msg = f"地址查询服务返回错误: {e.response.status_code}"
        logger.error(f"{error_msg} - {str(e)}")
        return {
            "success": False,
            "query": address,
            "error": error_msg
        }

    except Exception as e:
        error_msg = f"地址查询失败: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "query": address,
            "error": error_msg
        }


async def reverse_geocode(
    latitude: float,
    longitude: float,
    language: str = "zh-CN"
) -> Dict[str, Any]:
    """
    反向地理编码：将坐标转换为地址

    Args:
        latitude: 纬度
        longitude: 经度
        language: 返回语言，默认"zh-CN"（简体中文）

    Returns:
        包含地址信息的字典
    """
    try:
        # 构建请求参数
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "addressdetails": 1,
            "accept-language": language
        }

        headers = {
            "User-Agent": USER_AGENT
        }

        logger.info(f"Reverse geocoding: {latitude}, {longitude}")

        # 发送请求
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(
                f"{NOMINATIM_BASE_URL}/reverse",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

        if "error" in data:
            return {
                "success": False,
                "error": f"未找到坐标 ({latitude}, {longitude}) 对应的地址"
            }

        # 格式化结果
        address_parts = data.get("address", {})

        result = {
            "success": True,
            "latitude": latitude,
            "longitude": longitude,
            "display_name": data.get("display_name"),
            "address": {
                "country": address_parts.get("country"),
                "state": address_parts.get("state"),
                "city": address_parts.get("city") or address_parts.get("town") or address_parts.get("village"),
                "district": address_parts.get("suburb") or address_parts.get("district"),
                "street": address_parts.get("road"),
                "postcode": address_parts.get("postcode"),
            },
            "summary": f"地址: {data.get('display_name')}"
        }

        logger.info(f"Reverse geocoding successful: {result['display_name']}")
        return result

    except Exception as e:
        error_msg = f"坐标转地址失败: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "latitude": latitude,
            "longitude": longitude,
            "error": error_msg
        }


# 定义地理编码工具
GEOCODE_TOOL_DEFINITION = ToolDefinition(
    name="geocode_address",
    description="查询地址的地理位置信息，包括坐标、详细地址等。当用户询问某个地方在哪里、某个地址的坐标、某个城市的位置等问题时使用此工具。",
    parameters=[
        ToolParameter(
            name="address",
            type=ToolParameterType.STRING,
            description="要查询的地址，可以是国家、城市、街道、地标等，支持中文和英文",
            required=True
        ),
        ToolParameter(
            name="language",
            type=ToolParameterType.STRING,
            description="返回语言代码，例如：'zh-CN'（简体中文）、'en'（英文）",
            required=False
        ),
        ToolParameter(
            name="limit",
            type=ToolParameterType.INTEGER,
            description="返回结果数量（1-10），默认1",
            required=False
        )
    ],
    function=geocode_address
)


# 定义反向地理编码工具
REVERSE_GEOCODE_TOOL_DEFINITION = ToolDefinition(
    name="reverse_geocode",
    description="根据经纬度坐标查询对应的地址信息。当用户提供坐标需要查询地址时使用此工具。",
    parameters=[
        ToolParameter(
            name="latitude",
            type=ToolParameterType.NUMBER,
            description="纬度（-90到90之间）",
            required=True
        ),
        ToolParameter(
            name="longitude",
            type=ToolParameterType.NUMBER,
            description="经度（-180到180之间）",
            required=True
        ),
        ToolParameter(
            name="language",
            type=ToolParameterType.STRING,
            description="返回语言代码，例如：'zh-CN'（简体中文）、'en'（英文）",
            required=False
        )
    ],
    function=reverse_geocode
)


def register_location_tools():
    """注册地址位置工具到全局注册表"""
    tool_registry.register_tool(GEOCODE_TOOL_DEFINITION)
    tool_registry.register_tool(REVERSE_GEOCODE_TOOL_DEFINITION)
    logger.info("Location tools registered successfully")
