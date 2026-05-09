"""
二维码 URL 生成模块
"""


def make_qr_url(base_url: str, material_code: str) -> str:
    """
    生成物料详情页访问链接。
    示例：https://code.zestrade.com:34433/wuping/material/2101010001
    """
    base = base_url.rstrip("/")
    return f"{base}/material/{material_code}"
