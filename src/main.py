import logging
import sys
from pathlib import Path

# src モジュールをインポートパスに追加 (実行場所対策)
sys.path.append(str(Path(__file__).parent.parent))

from src import fetcher, output, translator

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
        
        # 1.5 辞書取得
        # index_content = fetcher.fetch_index()
        # API負荷軽減のため、本来はキャッシュや条件分岐が必要だが、
        # 今回は毎回取得する (ただし fetcher 内でダウンロード済みチェックなどはしていない)
        index_content = fetcher.fetch_index()
        dict_data = fetcher.fetch_dictionary(index_content)
        
        # 2. 変換
        logger.info("翻訳処理を開始します...")
        translation_map = translator.build_translation_map(dict_data)
        translated_data = translator.recursive_translate(data, translation_map)
        logger.info("翻訳処理完了")
        
        # 3. 保存
        output.save_yaml(translated_data)
        
        logger.info("[成功] 全処理完了")
        
    except Exception as e:
        logger.error(f"[失敗] 致命的なエラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
