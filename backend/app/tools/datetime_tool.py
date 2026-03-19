"""
日期时间工具
提供获取当前日期、时间、时区等信息的功能
"""
import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Dict, Any, Optional
from .schemas import ToolDefinition, ToolParameter, ToolParameterType
from .registry import tool_registry

logger = logging.getLogger(__name__)


async def get_current_datetime(
    timezone_name: str = "Asia/Shanghai",
    format: str = "full"
) -> Dict[str, Any]:
    """
    获取当前日期和时间信息

    Args:
        timezone_name: 时区名称，默认"Asia/Shanghai"（北京时间）
        format: 返回格式，可选值：
                - "full": 完整信息（默认）
                - "date": 仅日期
                - "time": 仅时间
                - "iso": ISO 8601格式

    Returns:
        包含日期时间信息的字典
    """
    try:
        # 获取指定时区的当前时间
        try:
            tz = ZoneInfo(timezone_name)
        except Exception:
            logger.warning(f"Invalid timezone '{timezone_name}', using Asia/Shanghai")
            tz = ZoneInfo("Asia/Shanghai")
            timezone_name = "Asia/Shanghai"

        now = datetime.now(tz)

        # 基础信息
        result = {
            "success": True,
            "timezone": timezone_name,
            "timestamp": now.timestamp(),
        }

        # 根据格式返回不同信息
        if format == "iso":
            result["datetime"] = now.isoformat()
            result["formatted"] = now.isoformat()

        elif format == "date":
            result["date"] = now.strftime("%Y-%m-%d")
            result["year"] = now.year
            result["month"] = now.month
            result["day"] = now.day
            result["weekday"] = now.strftime("%A")
            result["weekday_cn"] = _get_weekday_cn(now.weekday())
            result["formatted"] = f"{now.year}年{now.month}月{now.day}日 {result['weekday_cn']}"

        elif format == "time":
            result["time"] = now.strftime("%H:%M:%S")
            result["hour"] = now.hour
            result["minute"] = now.minute
            result["second"] = now.second
            result["formatted"] = now.strftime("%H:%M:%S")

        else:  # full
            result["datetime"] = now.isoformat()
            result["date"] = now.strftime("%Y-%m-%d")
            result["time"] = now.strftime("%H:%M:%S")
            result["year"] = now.year
            result["month"] = now.month
            result["day"] = now.day
            result["hour"] = now.hour
            result["minute"] = now.minute
            result["second"] = now.second
            result["weekday"] = now.strftime("%A")
            result["weekday_cn"] = _get_weekday_cn(now.weekday())
            result["formatted"] = f"{now.year}年{now.month}月{now.day}日 {result['weekday_cn']} {now.strftime('%H:%M:%S')}"

        logger.info(f"Retrieved datetime for timezone {timezone_name}: {result['formatted']}")
        return result

    except Exception as e:
        error_msg = f"Failed to get datetime: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }


def _get_weekday_cn(weekday: int) -> str:
    """转换星期数字为中文"""
    weekdays = {
        0: "星期一",
        1: "星期二",
        2: "星期三",
        3: "星期四",
        4: "星期五",
        5: "星期六",
        6: "星期日"
    }
    return weekdays.get(weekday, "未知")


# 定义日期时间工具
DATETIME_TOOL_DEFINITION = ToolDefinition(
    name="get_current_datetime",
    description="获取当前日期和时间信息。当用户询问现在几点、今天是几号、星期几等时间相关问题时使用此工具。",
    parameters=[
        ToolParameter(
            name="timezone_name",
            type=ToolParameterType.STRING,
            description="时区名称，例如：'Asia/Shanghai'（北京）、'America/New_York'（纽约）、'Europe/London'（伦敦）、'UTC'（UTC时间）",
            required=False
        ),
        ToolParameter(
            name="format",
            type=ToolParameterType.STRING,
            description="返回格式：'full'（完整信息）、'date'（仅日期）、'time'（仅时间）、'iso'（ISO格式）",
            required=False,
            enum=["full", "date", "time", "iso"]
        )
    ],
    function=get_current_datetime
)


def register_datetime_tool():
    """注册日期时间工具到全局注册表"""
    tool_registry.register_tool(DATETIME_TOOL_DEFINITION)
    logger.info("Datetime tool registered successfully")
