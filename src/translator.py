import logging
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)

def build_translation_map(dict_data: Dict[str, Any]) -> Dict[str, str]:
    """辞書データから翻訳マップ(uniqueName -> name)を作成する"""
    translation_map = {}
    count = 0
    
    for section_name, items in dict_data.items():
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    unique_name = item.get('uniqueName')
                    name = item.get('name')
                    
                    if unique_name and name:
                        translation_map[unique_name] = name
                        count += 1
                        
    logger.info(f"翻訳マップ構築完了: {count} items")
    
    # デバッグ: 特定の未翻訳キーの存在確認
    debug_target = "/Lotus/StoreItems/Weapons/Corpus/LongGuns/CrpBFG/Vandal/VandalCrpBFG"
    if debug_target in translation_map:
        logger.info(f"[Debug] Key found: {debug_target} -> {translation_map[debug_target]}")
    else:
        logger.warning(f"[Debug] Key NOT found: {debug_target}")
        
    return translation_map

def recursive_translate(data: Any, translation_map: Dict[str, str]) -> Any:
    """再帰的にデータを走査し、文字列を翻訳マップに基づいて置換する"""
    if isinstance(data, dict):
        return {k: recursive_translate(v, translation_map) for k, v in data.items()}
    elif isinstance(data, list):
        return [recursive_translate(item, translation_map) for item in data]
    elif isinstance(data, str):
        # 完全一致で置換
        if data in translation_map:
            return translation_map[data]
        
        # /Lotus/StoreItems/ を削除して再試行
        if data.startswith("/Lotus/StoreItems/"):
            # パターン1: /Lotus/StoreItems/Weapons/... -> /Lotus/Weapons/...
            # パターン2: /Lotus/StoreItems/Upgrades/... -> /Lotus/Upgrades/...
            alt_key = data.replace("/Lotus/StoreItems/", "/Lotus/")
            if alt_key in translation_map:
                # logger.debug(f"Retried Match: {data} -> {translation_map[alt_key]}")
                return translation_map[alt_key]
        
        # デバッグ: 特定の未翻訳アイテムをログに出す (頻出するので警告は抑制気味に)
        if "VandalCrpBFG" in data:
                logger.warning(f"Translation FAILED for: {data}")
        
        return data
    else:
        return data
