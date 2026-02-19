# Warframe Status JP YAML Generator

Digital Extremes 公式の Warframe WorldState API からデータを取得し、日本語訳を適用して YAML 形式で出力するツールです。

## 特徴

- **日本語化**: 公式の Public Export データを利用し、アイテム名、ノード名、ミッションタイプなどを可能な限り日本語に変換します。
- **YAML 出力**: `ruamel.yaml` を使用し、人間が読みやすく、かつプログラムで扱いやすい形式で出力します。
- **Index 自動取得 & フォールバック**: Public Export の Index ファイルを取得し、最新の辞書データを利用します。Index が破損している場合や取得できない場合は、GitHub (calamity-inc/warframe-public-export) から自動的にフォールバックして辞書を取得します。
- **GitHub Actions 対応**: 定期実行 (5分毎) により、常に最新のステータスを YAML として保持できます。

## 動作環境

- Python 3.x (3.12 推奨)
- 依存ライブラリ: `requests`, `ruamel.yaml`, `rich`

## インストール (ローカル実行)

1. リポジトリをクローンします。
2. 依存関係をインストールします。

```bash
pip install -r requirements.txt
```

## 使い方

メインスクリプトを実行すると、`output/` ディレクトリに YAML ファイルが生成されます。

```bash
python src/main.py
```

- `output/latest.yaml`: 最新の状態
- `output/wf-status_<timestamp>.yaml`: 履歴 (最新5件保持)

## GitHub Actions

`.github/workflows/update_status.yml` により、以下のトリガーで自動実行されます。
- **スケジュール**: 5分ごとに実行
- **手動実行**: Actions タブから `workflow_dispatch` で実行可能

実行結果はリポジトリの `output/` ディレクトリにコミットされます。

## 翻訳に関する制限事項

本ツールは Warframe Public Export のデータを利用して翻訳を行いますが、一部のデータ（特定のバンドル名、レシピ、UIテキストなど）は Public Export に含まれていない、または Index から参照できない場合があります。
その場合、該当箇所は英語のまま出力される、またはシステムパス (`/Lotus/...`) のまま出力されることがあります。
- **Index サイズ制限の回避**: 公式 Index ファイルが非常に小さい場合でも、必須ファイルが含まれていれば正常に処理するように調整されています。
- **フォールバック**: 辞書取得に失敗した場合、コミュニティリポジトリから辞書データを取得します。

## ライセンス

MIT License
