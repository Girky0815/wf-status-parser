# プロジェクト: Warframe Status JP YAML 生成ツール

## 概要
Digital Extremes (DE) 公式の WorldState JSON を取得し、Public Export データを参照して内部パスを日本語化した YAML を自動生成・運用する。

## 技術スタック
- 言語: Python 3.14
- ライブラリ: requests, ruamel.yaml
- 標準ライブラリ: lzma, json, os, datetime, logging
- プラットフォーム: GitHub Actions (ubuntu-latest)
- エンコーディング: UTF-8 (入力・出力ともに)

## 言語制約 (最重要)
- **すべての対話、コード内のコメント、docstring、ログ出力は日本語で行うこと。**
- 日本語以外の言語（英語等）での回答を禁止する。ただし、技術用語や Warframe 固有の内部パス（/Lotus/...）はそのまま使用してよい。

## AIエージェントへの行動指針
1. コード生成時は必ず Google スタイルの日本語 Docstring を含めること。
2. インデントは厳密にスペース 2 とすること。
3. logging モジュールを使用し、処理の進捗を逐次日本語(作業中の内容含む)で出力すること。
  - 作業に成功した場合は[成功]、失敗した場合は[失敗]と色付きでログに出力すること。
  - インデントを活用し、見やすいログを出力すること。
4. YAML 出力時は ruamel.yaml を使い、セクションごとに日本語の解説コメントを挿入すること。

## データソース
1. WorldState: `https://api.warframe.com/cdn/worldState.php`
2. マニフェスト・インデックス: `https://origin.warframe.com/PublicExport/index_ja.txt.lzma`
3. 辞書ベースURL: `http://content.warframe.com/PublicExport/Manifest/`
4. アイテムのパス: `https://content.warframe.com/PublicExport/<Lotus/...>

## ロジック手順
1. **取得とビルドチェック**: WorldState 内の `BuildLabel` を前回の実行結果と比較し、変更がある場合のみ続行。
2. **辞書構築**: `index_ja.txt.lzma` を解凍(unlzma)し、動的なハッシュ付きURLから辞書JSONを取得。`/Lotus/` パスをキーとした日本語変換マップを作成。
3. **再帰的翻訳**: JSON 構造を再帰的に走査し、内部パスを日本語に置換。辞書にない場合は元のパスを保持（フォールバック）。
4. **コメント付き YAML 出力**: `ruamel.yaml` を使用。WorldStateをYAMLに変換し、主要セクションに日本語のヘッダーコメントを挿入。
5. **ファイル・ローテーション**: `output/` 内に最新の YAML を保存し、履歴を最大 5 件に制限。

## AIエージェントへの指示
- 生成する Python コードには必ず型ヒント (Type Hinting) を含めること。
- Warframe の「地層（階層構造）」の変化に耐えられるよう、`.get()` メソッドや例外処理を徹底し、堅牢なコードを記述すること。
- YAML 出力時は `allow_unicode=True` を設定し、日本語が正しく表示されるようにすること。

## GitHub Actions 運用
- 定期実行 (15-30分毎) + `.py` プッシュ時のテスト実行。
- 生成物は `output/` ディレクトリへ出力。
- 常に `latest.yaml` と過去 5 件の履歴ファイルを維持する（古いものは順次削除）。

## 作業に役立ちそうなページ
- https://wiki.warframe.com/w/Public_Export: Public Exportの概要や方法が書かれているので，理解してから作業すること．
- 

## 参考 
- データソース1 の JSON 例を置く(sample/wf-status_1771495618.json)ので，それを参考にすること．
- 星系データのサンプルは，wf-星系.jsonにあるので，それを参考にすること．
- 言うまでもないが，このデータを辞書データに使ってはならない．あくまで実装時のサンプルとして使うこと．
