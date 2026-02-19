import logging
import requests
from typing import Dict, Any

from . import const

logger = logging.getLogger(__name__)

def fetch_worldstate() -> Dict[str, Any]:
    """WorldState JSONを取得する"""
    logger.info("WorldState を取得中...")
    try:
        response = requests.get(const.WORLDSTATE_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        build_label = data.get('BuildLabel', data.get('WorldStatePublished', {}).get('BuildLabel', 'Unknown'))
        logger.info(f"[成功] WorldState 取得完了 (BuildLabel: {build_label})")
        return data
    except Exception as e:
        logger.error(f"[失敗] WorldState 取得エラー: {e}")
        raise
