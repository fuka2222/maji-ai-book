# AI動画制作自動化システム

Claude CodeとRemotionを使った動画制作の完全自動化システムです。企画から動画完成までのワークフローを自動化します。

## システム概要

```
企画 → 台本生成 → スライド生成 → 素材準備 → 編集マッピング → 動画出力
```

### 主要コンポーネント

1. **台本生成** (`script_generator.py`)
   - 企画情報からClaude APIで台本を自動生成
   - シーン構成、ナレーション、ビジュアル指示を含む

2. **スライド生成** (`slide_generator.py`)
   - 台本からスライド構成を自動生成
   - Figmaテンプレート連携用データをエクスポート

3. **素材管理** (`asset_manager.py`)
   - 画像、動画、BGM、ナレーションを一元管理
   - 素材要件の自動抽出

4. **動画生成統合** (`video_generator.py`)
   - 編集マッピング作成
   - Remotion用データ出力

5. **オーケストレーター** (`main_orchestrator.py`)
   - 全プロセスを統合管理
   - ワンコマンドで完全なパイプライン実行

## ディレクトリ構造

```
まじAI模倣/
├── 外部データ格納フォルダ/     # 外部からの素材
├── 内部データ格納フォルダ/     # 処理データ
│   ├── カテゴリ/
│   ├── 企画/
│   ├── 台本/
│   ├── 動画素材/
│   ├── 画像素材/
│   ├── ナレーション/
│   ├── BGM/
│   ├── スライド/
│   └── 編集マッピング/
├── src/                       # Pythonスクリプト
│   ├── script_generator.py
│   ├── slide_generator.py
│   ├── asset_manager.py
│   ├── video_generator.py
│   └── main_orchestrator.py
├── config/                    # 設定ファイル
│   └── sample_project.json
└── remotion/                  # Remotionプロジェクト
```

## セットアップ

### 必要な環境

- Python 3.8以上
- Anthropic API key
- Node.js 18以上（Remotion用）

### インストール

```bash
# Python依存パッケージのインストール
pip install anthropic

# Remotionのセットアップ（別途必要な場合）
cd remotion
npm install
```

### 環境変数の設定

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

## 使い方

### 1. プロジェクト作成

企画情報を含むJSONファイルを作成し、プロジェクトを作成します。

```bash
cd /Users/fuka/01_AI/まじAI模倣
python src/main_orchestrator.py create config/sample_project.json
```

出力例:
```
✓ プロジェクト作成: proj_20250128_143022

プロジェクトID: proj_20250128_143022

パイプライン実行:
  python src/main_orchestrator.py run proj_20250128_143022
```

### 2. 完全パイプライン実行

プロジェクトIDを使って、台本生成からマッピング作成までを一括実行します。

```bash
python src/main_orchestrator.py run proj_20250128_143022
```

実行されるステップ:
1. プロジェクトデータ読み込み
2. 台本生成（Claude API使用）
3. スライド生成（Claude API使用）
4. 素材要件分析
5. 編集マッピング生成

### 3. 個別コンポーネントの使用

各コンポーネントは個別に実行することもできます。

#### 台本生成のみ

```bash
python src/script_generator.py 内部データ格納フォルダ/企画/proj_xxx.json
```

#### スライド生成のみ

```bash
python src/slide_generator.py 内部データ格納フォルダ/台本/script_xxx.json
```

#### 素材管理

```bash
# 素材追加
python src/asset_manager.py add image /path/to/image.png
python src/asset_manager.py add video /path/to/video.mp4
python src/asset_manager.py add audio /path/to/bgm.mp3

# 素材一覧
python src/asset_manager.py list

# 素材要件生成
python src/asset_manager.py requirements 内部データ格納フォルダ/台本/script_xxx.json
```

#### 動画生成マッピング

```bash
python src/video_generator.py \
  内部データ格納フォルダ/台本/script_xxx.json \
  内部データ格納フォルダ/スライド/slides_xxx.json \
  内部データ格納フォルダ/asset_manifest_xxx.json
```

## 企画JSONフォーマット

```json
{
  "title": "動画タイトル",
  "thumbnail_concept": "サムネイルのコンセプト",
  "category": "カテゴリ（教育/エンターテイメント/テクノロジーなど）",
  "target_audience": "ターゲット視聴者",
  "duration": 180,
  "key_points": [
    "伝えたいポイント1",
    "伝えたいポイント2"
  ],
  "description": "動画の説明"
}
```

## 出力ファイル

### 台本 (script_*.json)
```json
{
  "title": "動画タイトル",
  "duration": 180,
  "scenes": [
    {
      "scene_number": 1,
      "type": "opening",
      "duration": 10,
      "narration": "ナレーション内容",
      "visual_description": "ビジュアル説明",
      "text_overlay": "画面テキスト",
      "notes": "演出ノート"
    }
  ]
}
```

### スライド (slides_*.json)
```json
{
  "title": "動画タイトル",
  "slides": [
    {
      "slide_number": 1,
      "scene_number": 1,
      "type": "title",
      "layout": "center",
      "title_text": "スライドタイトル",
      "body_text": "本文",
      "visual_elements": [...],
      "figma_template": "template_basic"
    }
  ],
  "scene_slide_mapping": [...]
}
```

### 編集マッピング (edit_mapping_*.json)
```json
{
  "project_id": "proj_xxx",
  "title": "動画タイトル",
  "total_duration": 180,
  "fps": 30,
  "resolution": {
    "width": 1920,
    "height": 1080
  },
  "timeline": [
    {
      "start_time": 0,
      "duration": 10,
      "scene_number": 1,
      "layers": [...]
    }
  ],
  "audio": {
    "bgm": "path/to/bgm.mp3",
    "narrations": [...]
  }
}
```

## Remotion連携

生成された `remotion/src/data/composition_*.json` をRemotionで読み込んで動画をレンダリングします。

```bash
cd remotion
npm run build
npx remotion render
```

## ワークフロー例

1. **企画作成**
   ```bash
   # config/my_project.json を作成
   python src/main_orchestrator.py create config/my_project.json
   ```

2. **パイプライン実行**
   ```bash
   python src/main_orchestrator.py run proj_20250128_143022
   ```

3. **素材準備**
   - 生成されたスライドをFigmaでデザイン
   - 必要な画像・動画素材を準備
   - ナレーション録音またはTTS生成
   - BGM選定

4. **素材登録**
   ```bash
   python src/asset_manager.py add image スライド/slide_001.png
   python src/asset_manager.py add narration ナレーション/scene_001.mp3
   python src/asset_manager.py add audio BGM/background.mp3
   ```

5. **動画生成**
   ```bash
   cd remotion
   npm run build
   ```

## トラブルシューティング

### API keyが設定されていない

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

または、APIキーなしでモックモードで動作します（開発・テスト用）。

### Pythonモジュールが見つからない

```bash
pip install anthropic
```

### ファイルが見つからない

パスが正しいか確認してください。相対パスではなく、プロジェクトルートからのパスを使用してください。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。
