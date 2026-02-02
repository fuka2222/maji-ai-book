#!/usr/bin/env python3
"""
スライド生成システム
台本からスライド計画と台本-スライドマッピングを生成
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
import anthropic


class SlideGenerator:
    """スライド生成クラス"""

    def __init__(self, api_key: str = None):
        """
        初期化

        Args:
            api_key: Anthropic API key
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
            print("警告: ANTHROPIC_API_KEYが設定されていません。モックモードで動作します。")

    def generate_slide_plan_prompt(self, script_data: Dict[str, Any]) -> str:
        """
        スライド計画生成用プロンプトを作成

        Args:
            script_data: 台本データ

        Returns:
            生成されたプロンプト
        """
        title = script_data.get('title', '')
        scenes = script_data.get('scenes', [])

        scenes_text = ""
        for scene in scenes:
            scenes_text += f"\nシーン{scene['scene_number']}: {scene['type']}\n"
            scenes_text += f"  時間: {scene['duration']}秒\n"
            scenes_text += f"  ナレーション: {scene['narration']}\n"
            scenes_text += f"  ビジュアル: {scene['visual_description']}\n"

        prompt = f"""あなたは動画用のスライドデザイナーです。以下の台本から、効果的なスライド構成を設計してください。

【動画情報】
タイトル: {title}

【台本内容】
{scenes_text}

【スライド設計の要件】
1. 各シーンに適切なスライドを割り当てる
2. 視覚的にわかりやすく、情報が整理されている
3. テキストは簡潔で読みやすい
4. 適切なビジュアル要素（アイコン、図表、画像）を配置
5. Figmaテンプレートで実装可能なデザイン

【出力形式】
JSON形式で以下の構造で出力してください：

{{
  "title": "動画タイトル",
  "slides": [
    {{
      "slide_number": 1,
      "scene_number": 対応するシーン番号,
      "type": "title/content/quote/image/closing",
      "layout": "center/left/right/split",
      "title_text": "スライドタイトル",
      "body_text": "本文テキスト",
      "visual_elements": [
        {{
          "type": "icon/image/chart/diagram",
          "description": "要素の説明",
          "position": "top/center/bottom/left/right"
        }}
      ],
      "design_notes": "デザイン指示",
      "figma_template": "使用するFigmaテンプレート名"
    }}
  ],
  "scene_slide_mapping": [
    {{
      "scene_number": 1,
      "slide_numbers": [1, 2],
      "transition": "トランジション方法"
    }}
  ]
}}

視覚的に魅力的で、メッセージが伝わりやすいスライド構成を作成してください。"""

        return prompt

    def generate_slides(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        台本からスライドを生成

        Args:
            script_data: 台本データ

        Returns:
            生成されたスライドデータ
        """
        prompt = self.generate_slide_plan_prompt(script_data)

        if self.client:
            try:
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4096,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                response_text = message.content[0].text

                # JSONブロックを抽出
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

                slide_data = json.loads(json_text)

            except Exception as e:
                print(f"API呼び出しエラー: {e}")
                slide_data = self._generate_mock_slides(script_data)
        else:
            slide_data = self._generate_mock_slides(script_data)

        # メタデータを追加
        slide_data['project_id'] = script_data.get('project_id', 'unknown')
        slide_data['generated_at'] = datetime.now().isoformat()

        return slide_data

    def _generate_mock_slides(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """モックスライドを生成"""
        title = script_data.get('title', '動画タイトル')
        scenes = script_data.get('scenes', [])

        slides = []
        scene_slide_mapping = []

        slide_num = 1
        for scene in scenes:
            # 各シーンに1枚のスライドを割り当て
            slide = {
                "slide_number": slide_num,
                "scene_number": scene['scene_number'],
                "type": "title" if scene['type'] == 'opening' else "content",
                "layout": "center" if scene['type'] == 'opening' else "left",
                "title_text": scene.get('text_overlay', title),
                "body_text": scene.get('narration', ''),
                "visual_elements": [
                    {
                        "type": "icon",
                        "description": "装飾アイコン",
                        "position": "top"
                    }
                ],
                "design_notes": scene.get('notes', ''),
                "figma_template": "template_basic"
            }
            slides.append(slide)

            scene_slide_mapping.append({
                "scene_number": scene['scene_number'],
                "slide_numbers": [slide_num],
                "transition": "fade"
            })

            slide_num += 1

        return {
            "title": title,
            "slides": slides,
            "scene_slide_mapping": scene_slide_mapping
        }

    def save_slides(self, slide_data: Dict[str, Any], output_dir: str = None) -> str:
        """
        スライドデータをファイルに保存

        Args:
            slide_data: スライドデータ
            output_dir: 出力ディレクトリ

        Returns:
            保存したファイルパス
        """
        if output_dir is None:
            output_dir = "内部データ格納フォルダ/スライド"

        os.makedirs(output_dir, exist_ok=True)

        project_id = slide_data.get('project_id', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"slides_{project_id}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(slide_data, f, ensure_ascii=False, indent=2)

        print(f"スライドデータを保存しました: {filepath}")
        return filepath

    def export_to_figma_format(self, slide_data: Dict[str, Any], output_path: str = None) -> str:
        """
        Figma連携用のフォーマットで出力

        Args:
            slide_data: スライドデータ
            output_path: 出力ファイルパス

        Returns:
            保存したファイルパス
        """
        if output_path is None:
            project_id = slide_data.get('project_id', 'unknown')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"内部データ格納フォルダ/スライド/figma_export_{project_id}_{timestamp}.json"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Figma用のシンプルなフォーマットに変換
        figma_data = {
            "project_name": slide_data['title'],
            "frames": []
        }

        for slide in slide_data['slides']:
            frame = {
                "name": f"Slide {slide['slide_number']}",
                "template": slide.get('figma_template', 'template_basic'),
                "text_layers": {
                    "title": slide.get('title_text', ''),
                    "body": slide.get('body_text', '')
                },
                "layout": slide.get('layout', 'center')
            }
            figma_data["frames"].append(frame)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(figma_data, f, ensure_ascii=False, indent=2)

        print(f"Figma用エクスポートファイルを保存しました: {output_path}")
        return output_path


def main():
    """メイン処理"""
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python slide_generator.py <台本JSONファイル>")
        print("例: python slide_generator.py 内部データ格納フォルダ/台本/script_001.json")
        sys.exit(1)

    script_file = sys.argv[1]

    try:
        # 台本ファイルを読み込み
        with open(script_file, 'r', encoding='utf-8') as f:
            script_data = json.load(f)

        # スライド生成
        generator = SlideGenerator()
        slide_data = generator.generate_slides(script_data)

        # 保存
        output_path = generator.save_slides(slide_data)

        # Figma形式でもエクスポート
        figma_path = generator.export_to_figma_format(slide_data)

        print(f"\n✓ スライド生成完了")
        print(f"  タイトル: {slide_data['title']}")
        print(f"  スライド数: {len(slide_data['slides'])}")
        print(f"  ファイル: {output_path}")
        print(f"  Figmaエクスポート: {figma_path}")

    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
