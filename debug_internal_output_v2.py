import logging
import sys
import os

# Ensure src is in path
sys.path.append(os.getcwd())

from src import fetcher

logging.basicConfig(level=logging.INFO)

def test_internal_output():
    logging.info("Testing internal output generation...")
    
    try:
        # Index取得 (修正されたロジックでサイズチェックを通過するはず)
        index = fetcher.fetch_index()
        if not index:
             logging.warning("Index fetch returned empty! Fallback might be triggered next.")
        else:
             logging.info(f"Index fetched successfully. Length: {len(index)}")

        # 辞書取得 (Indexが空ならフォールバック、空でなければ通常取得)
        data = fetcher.fetch_dictionary(index)
        logging.info("Fetch dictionary completed.")
        
    except Exception as e:
        logging.error(f"Error during fetch: {e}")

if __name__ == "__main__":
    test_internal_output()
