import logging
import sys
from pathlib import Path

# src モジュールをインポートパスに追加 (実行場所対策)
sys.path.append(str(Path(__file__).parent.parent))

from src import fetcher, output

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    logger.info("処理を開始します")
    try:
        # 1. 取得
        data = fetcher.fetch_worldstate()
        
        # 2. 変換 (現在はパススルー)
        translated_data = data
        
        # 3. 保存
        output.save_yaml(translated_data)
        
        logger.info("[成功] 全処理完了")
        
    except Exception as e:
        logger.error(f"[失敗] 致命的なエラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
