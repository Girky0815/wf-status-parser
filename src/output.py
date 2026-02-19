import os
import logging
import datetime
from pathlib import Path
from typing import Any, Dict

from ruamel.yaml import YAML

from . import const

logger = logging.getLogger(__name__)

def save_yaml(data: Dict[str, Any]) -> None:
    """JSONデータをYAMLとして保存する"""
    output_dir = Path(const.OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = int(datetime.datetime.now().timestamp())
    filename = f"wf-status_{timestamp}.yaml"
    filepath = output_dir / filename
    
    logger.info(f"YAML を保存中: {filepath}")
    
    yaml = YAML()
    yaml.allow_unicode = True
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=2, offset=2)
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# Warframe WorldState Status (JP)\n")
            f.write(f"# Generated at: {datetime.datetime.now()}\n")
            # WorldStatePublished またはトップレベルから BuildLabel を取得
            build_label = data.get('BuildLabel', data.get('WorldStatePublished', {}).get('BuildLabel', 'Unknown'))
            f.write(f"# BuildLabel: {build_label}\n\n")

            yaml.dump(data, f)
        
        logger.info(f"[成功] YAML 保存完了: {filepath}")
        
        # rotation
        _rotate_files(output_dir)
        
        # latest.yaml の更新
        latest_path = output_dir / "latest.yaml"
        with open(latest_path, "w", encoding="utf-8") as f:
            f.write("# Warframe WorldState Status (JP) - Latest\n")
            yaml.dump(data, f)
        logger.info(f"[成功] latest.yaml 更新完了: {latest_path}")
            
    except Exception as e:
        logger.error(f"[失敗] YAML 保存エラー: {e}")
        raise

def _rotate_files(directory: Path, keep: int = 5) -> None:
    """古いファイルを削除して履歴数を維持する"""
    files = sorted(directory.glob("wf-status_*.yaml"), key=os.path.getmtime, reverse=True)
    if len(files) > keep:
        for f in files[keep:]:
            try:
                f.unlink()
                logger.info(f"古いログを削除: {f.name}")
            except Exception as e:
                logger.warning(f"ファイル削除失敗 {f.name}: {e}")
