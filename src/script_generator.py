#!/usr/bin/env python3
"""
台本生成システム
企画（タイトル、サムネイル情報）から台本を自動生成
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
import anthropic


class ScriptGenerator:
    """台本生成クラス"""

    def __init__(self, api_key: str = None):
        """
        初期化

        Args:
            api_key: Anthropic API key (環境変数ANTHROPIC_API_KEYから取得可能)
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
            print("警告: ANTHROPIC_API_KEYが設定されていません。モックモードで動作します。")

    def generate_script_prompt(self, project_data: Dict[str, Any]) -> str:
        """
        台本生成用プロンプトを作成

        Args:
            project_data: 企画データ（タイトル、ターゲット、テーマなど）

        Returns:
            生成されたプロンプト
        """
        title = project_data.get('title', '')
        thumbnail_concept = project_data.get('thumbnail_concept', '')
        target_audience = project_data.get('target_audience', '一般視聴者')
        duration = project_data.get('duration', 300)  # 秒
        category = project_data.get('category', '教育')
        key_points = project_data.get('key_points', [])

        prompt = f"""あなたは優秀な動画台本ライターです。以下の企画情報をもとに、魅力的な動画台本を作成してください。

【企画情報】
タイトル: {title}
サムネイルコンセプト: {thumbnail_concept}
ターゲット視聴者: {target_audience}
動画尺: {duration}秒（約{duration//60}分）
カテゴリ: {category}
キーポイント: {', '.join(key_points) if key_points else '指定なし'}

【台本作成の要件】
1. オープニング（10-15秒）: 視聴者の注意を引く導入
2. メインコンテンツ（70-80%）: 明確な構成で情報を伝達
3. クロージング（10-15秒）: まとめと行動喚起

【出力形式】
JSON形式で以下の構造で出力してください：

{{
  "title": "動画タイトル",
  "duration": 予定秒数,
  "scenes": [
    {{
      "scene_number": 1,
      "type": "opening/main/closing",
      "duration": 秒数,
      "narration": "ナレーション台本",
      "visual_description": "画面に表示する内容の説明",
      "text_overlay": "画面に表示するテキスト",
      "notes": "演出やトランジションの指示"
    }}
  ]
}}

視聴者が最後まで見たくなる構成で、テンポよく進む台本を作成してください。"""

        return prompt

    def generate_script(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        企画から台本を生成

        Args:
            project_data: 企画データ

        Returns:
            生成された台本データ
        """
        prompt = self.generate_script_prompt(project_data)

        if self.client:
            # Claude APIを使用して台本生成
            try:
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4096,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                # レスポンスからJSON部分を抽出
                response_text = message.content[0].text

                # JSONブロックを抽出（```json ... ```の形式に対応）
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_text = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    json_text = response_text[json_start:json_end].strip()
                else:
                    json_text = response_text.strip()

                script_data = json.loads(json_text)

            except Exception as e:
                print(f"API呼び出しエラー: {e}")
                script_data = self._generate_mock_script(project_data)
        else:
            # モックデータを生成
            script_data = self._generate_mock_script(project_data)

        # メタデータを追加
        script_data['project_id'] = project_data.get('id', 'unknown')
        script_data['generated_at'] = datetime.now().isoformat()
        script_data['category'] = project_data.get('category', '未分類')

        return script_data

    def _generate_mock_script(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """モック台本を生成（API未使用時）"""
        title = project_data.get('title', '動画タイトル')
        duration = project_data.get('duration', 300)

        return {
            "title": title,
            "duration": duration,
            "scenes": [
                {
                    "scene_number": 1,
                    "type": "opening",
                    "duration": 10,
                    "narration": "こんにちは！今日は「{}」について解説します！".format(title),
                    "visual_description": "タイトルカードとアニメーション",
                    "text_overlay": title,
                    "notes": "ズームインエフェクト"
                },
                {
                    "scene_number": 2,
                    "type": "main",
                    "duration": duration - 20,
                    "narration": "メインコンテンツの説明が入ります。",
                    "visual_description": "スライドとビジュアル素材",
                    "text_overlay": "ポイント1: 重要な情報",
                    "notes": "スライド切り替え"
                },
                {
                    "scene_number": 3,
                    "type": "closing",
                    "duration": 10,
                    "narration": "今日のまとめです。チャンネル登録もお願いします！",
                    "visual_description": "エンドカードとCTA",
                    "text_overlay": "チャンネル登録お願いします！",
                    "notes": "フェードアウト"
                }
            ]
        }

    def save_script(self, script_data: Dict[str, Any], output_dir: str = None) -> str:
        """
        台本をファイルに保存

        Args:
            script_data: 台本データ
            output_dir: 出力ディレクトリ（デフォルト: 内部データ格納フォルダ/台本）

        Returns:
            保存したファイルパス
        """
        if output_dir is None:
            output_dir = "内部データ格納フォルダ/台本"

        os.makedirs(output_dir, exist_ok=True)

        # ファイル名を生成
        project_id = script_data.get('project_id', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"script_{project_id}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)

        # 保存
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(script_data, f, ensure_ascii=False, indent=2)

        print(f"台本を保存しました: {filepath}")
        return filepath


def main():
    """メイン処理"""
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python script_generator.py <企画JSONファイル>")
        print("例: python script_generator.py 内部データ格納フォルダ/企画/project_001.json")
        sys.exit(1)

    project_file = sys.argv[1]

    try:
        # 企画ファイルを読み込み
        with open(project_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)

        # 台本生成
        generator = ScriptGenerator()
        script_data = generator.generate_script(project_data)

        # 保存
        output_path = generator.save_script(script_data)

        print(f"\n✓ 台本生成完了")
        print(f"  タイトル: {script_data['title']}")
        print(f"  シーン数: {len(script_data['scenes'])}")
        print(f"  予定尺: {script_data['duration']}秒")
        print(f"  ファイル: {output_path}")

    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
