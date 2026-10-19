"""
Outbound URL guard for tools that fetch user/model supplied URLs.

Blocks requests to loopback, private, link-local (cloud metadata),
reserved and multicast addresses so the web tools cannot be used to
reach services inside the deployment network (SSRF).
"""
import asyncio
import ipaddress
import socket
from typing import Optional
from urllib.parse import urlparse

ALLOWED_SCHEMES = {"http", "https"}


class UnsafeURLError(ValueError):
    """Raised when a URL points somewhere the server must not fetch."""


def _is_public_ip(ip: ipaddress._BaseAddress) -> bool:
    # IPv4-mapped IPv6 (::ffff:127.0.0.1) must be judged by its IPv4 part
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    return ip.is_global and not ip.is_multicast


async def assert_public_url(url: str, port: Optional[int] = None) -> None:
    """
    Raise UnsafeURLError unless every address the URL's host resolves to
    is a public internet address.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise UnsafeURLError(f"不支持的协议: {parsed.scheme or '(空)'}")

    host = parsed.hostname
    if not host:
        raise UnsafeURLError("无效的URL格式")

    port = port or parsed.port or (443 if parsed.scheme == "https" else 80)

    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None

    if literal is not None:
        addresses = [literal]
    else:
        loop = asyncio.get_running_loop()
        try:
            infos = await loop.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        except socket.gaierror:
            raise UnsafeURLError(f"无法解析域名: {host}")
        addresses = [ipaddress.ip_address(info[4][0].split("%")[0]) for info in infos]

    if not addresses or not all(_is_public_ip(ip) for ip in addresses):
        raise UnsafeURLError("不允许访问内网或本机地址")
