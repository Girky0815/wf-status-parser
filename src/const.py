"""定数定義モジュール"""
import os
# URL定義
# PC (Aggressive blocking): https://api.warframe.com/cdn/worldState.php
# Alternative PC: https://content.warframe.com/dynamic/worldState.php
# PS4: https://content-ps4.warframe.com/dynamic/worldState.php
# Switch: https://content-swi.warframe.com/dynamic/worldState.php
# XB1: https://content-xb1.warframe.com/dynamic/worldState.php

WORLDSTATE_URL = os.environ.get("WF_WORLDSTATE_URL", "https://api.warframe.com/cdn/worldState.php")
PUBLIC_EXPORT_URL = "https://origin.warframe.com/PublicExport/index_ja.txt.lzma"
BASE_DICT_URL = "http://content.warframe.com/PublicExport/Manifest/"
DICT_ITEM_URL = "http://content.warframe.com/PublicExport/Manifest/"

# ローカルパス
OUTPUT_DIR = "output"
INTERNAL_OUTPUT_DIR = "internal_output"

# ユーザーエージェント設定 (GitHub Actionsなどで403エラーが出る対策)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"

# プロキシ設定 (環境変数から取得)
WF_PROXY_URL = os.environ.get("WF_PROXY_URL", "")
