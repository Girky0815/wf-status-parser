import logging
import lzma
# import requests
from curl_cffi import requests
# import cloudscraper
from typing import Dict, Any, List

import json
import os
from . import const

logger = logging.getLogger(__name__)

FALLBACK_BASE_URL = "https://raw.githubusercontent.com/calamity-inc/warframe-public-export/master/"
FALLBACK_FILES = [
    "ExportWeapons_ja.json",
    "ExportWarframes_ja.json",
    "ExportUpgrades_ja.json",
    "ExportRelicArcane_ja.json",
    "ExportResources_ja.json",
    "ExportSentinels_ja.json",
    "ExportCustoms_ja.json",
    "ExportFlavour_ja.json",
    "ExportDrones_ja.json",
    "ExportKeys_ja.json",
    "ExportGear_ja.json",
    "ExportFusionBundles_ja.json",
    "ExportRegions_ja.json",
    "ExportSortieRewards_ja.json",
    "ExportManifest.json"
]
# Helper function for requests
def request_get(url: str, timeout: int = 30):
    """プロキシ設定があればプロキシ経由でリクエストする"""
    if const.WF_PROXY_URL:
        logger.info(f"Using Cloudflare Proxy for: {url}")
        # プロキシURLの形式: https://worker.dev/?url=<target_url>
        # URLエンコードは requests が params でやってくれるはずだが、
        # curl_cffi の挙動を確認する必要がある。ここでは単純に params を使う。
        return requests.get(const.WF_PROXY_URL, params={"url": url}, impersonate="chrome", timeout=timeout)
    else:
        # プロキシがない場合は直接アクセス (impersonate="chrome"に戻す)
        # Safari偽装は失敗したのでChromeに戻すが、どちらでも良い
        return requests.get(url, impersonate="chrome", timeout=timeout)

def fetch_index() -> str:
    """index_ja.txt.lzma を取得・解凍してテキストを返す"""
    logger.info("Public Export Index を取得中...")
    try:
        # response = request_get(const.PUBLIC_EXPORT_URL, timeout=30)
        # response = requests.get(const.PUBLIC_EXPORT_URL, impersonate="safari17_0", timeout=30)
        response = request_get(const.PUBLIC_EXPORT_URL, timeout=30)
        response.raise_for_status()
        
        # lzma 解凍 (ヘッダー修正)
        # Warframe Public Export の LZMA はプロパティ(5バイト) + データ長(8バイト)を含む場合があるが、
        # python の lzma モジュールは形式によって挙動が異なるため、RAW形式でプロパティを指定して解凍する。
        try:
            # プロパティ(1バイト目)から設定を読み取るなど複雑なため、
            # 一般的な workaround として知られる方法 (5バイト目以降をデータとして扱い、フィルターを手動設定) を試す
            # あるいは、単純に lzma.open を使うほうが頑健な場合がある
            content = lzma.decompress(response.content).decode('utf-8')
        except lzma.LZMAError:
            try:
                # FORMAT_RAW でフィルタを指定 (lc=3, lp=0, pb=2 は一般的な設定だが、データによる)
                # ここでは単純にヘッダー(13バイト)を無視して RAW 解凍を試みるなど、試行錯誤が必要
                # しかし requests の content は bytes なので、lzma.LZMADecompressor を使う
                
                # 方法2: 最初の13バイトを無視して RAW 解凍 (古くからある手法)
                # properties(5) + uncompressed_size(8) = 13 bytes
                filters = [
                    {"id": lzma.FILTER_LZMA1, "lc": 3, "lp": 0, "pb": 2, "dict_size": 16*1024*1024}
                ]
                # データ本体は13バイト目以降と仮定
                content = lzma.decompress(response.content[13:], format=lzma.FORMAT_RAW, filters=filters).decode('utf-8')
            except Exception as e2:
                 logger.warning(f"RAW解凍(skip 13)も失敗: {e2}")
                 # 方法3: そもそもサーバーが lzma ではなく lzla (lzma2) かもしれない、あるいは単に deflate
                 # ここでは一旦エラーとして再送
                 raise e2
            
        logger.info("[成功] Index 取得・解凍完了")
        
        msg = f"[成功] Index 取得・解凍完了 ({len(content)} bytes)"
        logger.info(msg)

        # 内容チェック (ExportWeapons_ja.json が含まれているか)
        if "ExportWeapons_ja.json" not in content:
            logger.warning(f"Index は取得できましたが、必要なエントリ (ExportWeapons_ja.json) が見つかりません。破損の可能性があります。Content len: {len(content)}")
            return ""
        
        # デバッグ: 特定のファイルのエントリを確認
        for line in content.splitlines():
            if "ExportWeapons" in line or "ExportLanguages" in line:
                logger.info(f"Index Entry: {line}")
        
        # デバッグ: 全ての内容を出力してファイル名を確認
        # logger.info(f"Index check: {content}")
        
        # デバッグ: Indexの内容をファイルに保存
        try:
            os.makedirs(const.INTERNAL_OUTPUT_DIR, exist_ok=True)
            with open(os.path.join(const.INTERNAL_OUTPUT_DIR, "index_dump.txt"), "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Index dump saved to {os.path.join(const.INTERNAL_OUTPUT_DIR, 'index_dump.txt')}")
        except Exception as e:
            logger.warning(f"Failed to save index dump: {e}")
        
        return content

    except Exception as e:
        logger.error(f"[失敗] Index 取得エラー: {e}")
        return ""

def fetch_dictionary(index_content: str) -> Dict[str, Any]:
    """Index から辞書(Export*_ja.json)のURLを特定して取得・統合する"""
    
    # 取得対象: *_ja.json
    # ExportManifest.json (言語なし) も含めるべきかもしれないが、まずは ja 付きを優先
    # 取得対象: *_ja.json と ExportManifest.json
    merged_data = {}
    total_items = 0
    debug_keys = []

    # フォールバックモード
    # Indexが空、あるいは必要なエントリが含まれていない場合はフォールバック
    if not index_content or "ExportWeapons_ja.json" not in index_content:
        logger.warning("有効なIndexがない(または必須エントリ欠落)ため、GitHubフォールバックモードを使用します。")
        for filename in FALLBACK_FILES:
            url = FALLBACK_BASE_URL + filename
            # logger.info(f"フォールバック取得: {url}")
            # headers = {"User-Agent": const.USER_AGENT}
            try:
                # response = requests.get(url, impersonate="safari17_0", timeout=30)
                response = request_get(url, timeout=30)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        # マージロジック
                        dict_count = 0
                        for key, value in data.items():
                            if isinstance(value, list):
                                merged_data[key] = value
                                total_items += len(value)
                                dict_count += len(value)
                        logger.info(f"Fetched Dictionary Key (Fallback): {filename}, Items: {dict_count}")
                    except Exception as e:
                        logger.error(f"JSONパースエラー ({filename}): {e}")
                else:
                    logger.warning(f"取得失敗 ({filename}): {response.status_code}")
            except Exception as e:
                logger.error(f"接続エラー ({filename}): {e}")
        
        if not merged_data:
             raise ValueError("フォールバックでも辞書データを取得できませんでした。")

        logger.info(f"[成功] フォールバック辞書統合完了: Total items: {total_items}")
        
        # デバッグ: フォールバックで取得した辞書も保存
        try:
            os.makedirs(const.INTERNAL_OUTPUT_DIR, exist_ok=True)
            dump_path = os.path.join(const.INTERNAL_OUTPUT_DIR, "merged_dictionary_fallback.json")
            with open(dump_path, "w", encoding="utf-8") as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Fallback dictionary saved to {dump_path}")
        except Exception as e:
             logger.warning(f"Failed to save fallback dictionary: {e}")

        # デバッグキー生成などは省略
        return merged_data

    # 通常モード
    target_lines = [line.strip() for line in index_content.splitlines() if "_ja.json" in line or "ExportManifest.json" in line]
    
    if not target_lines:
        logger.warning("辞書ファイル (*_ja.json) が Index 内に見つかりません。")
        return fetch_dictionary("")
    
    for line in target_lines:
        # line format: ExportWarframes_ja.json!00_xxxx
        filename = line.split('!')[0]
        # line format: ExportWarframes_ja.json!00_xxxx
        dict_url = const.DICT_ITEM_URL + line
        
        logger.info(f"辞書ファイルを取得中: {dict_url}")
        
        try:
            # response = requests.get(dict_url, impersonate="safari17_0", timeout=30)
            response = request_get(dict_url, timeout=30)
            response.raise_for_status()
            # テキストのクリーニングが必要な場合がある (BOMや制御文字など)
            # requests.json() は BOM (utf-8-sig) を自動処理するはず
            data = response.json()
            
            if "ExportManifest.json" in filename:
                logger.info(f"[Debug] ExportManifest keys: {list(data.keys())}")
            
            # JSONの構造は { "ExportWarframes": [ ... ] } のようになっているはず
            # ルートキーが1つだけならそれを使う、そうでなければフラットにするなど調整
            # JSONの構造は { "ExportWarframes": [ ... ] } のようになっているはず
            # ルートキーが1つだけならそれを使う、そうでなければフラットにするなど調整
            for key, value in data.items():
                if isinstance(value, list):
                    # リストの場合は辞書マップ構築用にはまだ早いので、まずはRawデータとして保持
                    merged_data[key] = value
                    total_items += len(value)
                    
                    # 取得したキー（ファイルタイプ）をログに出す
                    logger.info(f"Fetched Dictionary Key: {key}, Items: {len(value)}")

                    # デバッグ: 最初のアイテムの構造と uniqueName を確認
                    if value and len(debug_keys) < 20: # 少し増やす
                        try:
                            first_item = value[0]
                            if isinstance(first_item, dict):
                                item_preview = list(first_item.keys())
                                unique_name_sample = first_item.get('uniqueName', 'No uniqueName')
                                debug_keys.append(f"{key}: {item_preview}, Sample: {unique_name_sample}")
                                
                                # StoreItems パスのチェック
                                if "/Lotus/StoreItems/" in unique_name_sample:
                                    logger.info(f"[Debug] StoreItems path found in {key}: {unique_name_sample}")
                            else:
                                debug_keys.append(f"{key}: {str(first_item)[:50]}")
                        except Exception:
                            pass
                    
        except Exception as e:
            logger.warning(f"[警告] 辞書取得失敗 ({dict_url}): {e}")
            # 一つの失敗で全体を止めない
            continue



    logger.info(f"[成功] 辞書統合完了: {len(merged_data)} sections / Total items: {total_items}")
    logger.info(f"Dict Keys Preview: {debug_keys}")
    
    # デバッグ: 統合された辞書を保存
    try:
        os.makedirs(const.INTERNAL_OUTPUT_DIR, exist_ok=True)
        dump_path = os.path.join(const.INTERNAL_OUTPUT_DIR, "merged_dictionary.json")
        logger.info(f"Saving merged dictionary to {dump_path} ...")
        with open(dump_path, "w", encoding="utf-8") as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        logger.info("Merged dictionary saved.")
    except Exception as e:
        logger.warning(f"Failed to save merged dictionary: {e}")

    return merged_data

def fetch_worldstate() -> Dict[str, Any]:
    """WorldState JSONを取得する"""
    logger.info("WorldState を取得中...")
    try:
        # response = requests.get(const.WORLDSTATE_URL, impersonate="safari17_0", timeout=30)
        response = request_get(const.WORLDSTATE_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        build_label = data.get('BuildLabel', data.get('WorldStatePublished', {}).get('BuildLabel', 'Unknown'))
        logger.info(f"[成功] WorldState 取得完了 (BuildLabel: {build_label})")
        return data
    except Exception as e:
        logger.error(f"[失敗] WorldState 取得エラー: {e}")
        if 'response' in locals():
            logger.error(f"Response Headers: {response.headers}")
            logger.error(f"Response Status: {response.status_code}")
            try:
                logger.error(f"Response Content loaded: {response.text[:500]}")
            except:
                pass
        raise
