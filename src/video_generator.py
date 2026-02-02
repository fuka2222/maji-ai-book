#!/usr/bin/env python3
"""
動画生成統合システム
編集マッピングを作成し、Remotionで動画を生成
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any


class VideoGenerator:
    """動画生成クラス"""

    def __init__(self, base_dir: str = "内部データ格納フォルダ"):
        """
        初期化

        Args:
            base_dir: ベースディレクトリ
        """
        self.base_dir = base_dir
        self.mapping_dir = os.path.join(base_dir, "編集マッピング")
        os.makedirs(self.mapping_dir, exist_ok=True)

    def create_edit_mapping(
        self,
        script_data: Dict[str, Any],
        slide_data: Dict[str, Any],
        asset_manifest: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        編集マッピングを作成

        Args:
            script_data: 台本データ
            slide_data: スライドデータ
            asset_manifest: 素材マニフェスト

        Returns:
            編集マッピングデータ
        """
        project_id = script_data.get('project_id', 'unknown')

        # タイムライン構築
        timeline = []
        current_time = 0

        # シーンとスライドのマッピング
        scene_slide_mapping = {
            item['scene_number']: item['slide_numbers']
            for item in slide_data.get('scene_slide_mapping', [])
        }

        for scene in script_data.get('scenes', []):
            scene_num = scene['scene_number']
            duration = scene['duration']

            # 対応するスライドを取得
            slide_numbers = scene_slide_mapping.get(scene_num, [])
            slides = [
                slide for slide in slide_data.get('slides', [])
                if slide['slide_number'] in slide_numbers
            ]

            # タイムラインアイテム作成
            timeline_item = {
                "start_time": current_time,
                "duration": duration,
                "scene_number": scene_num,
                "scene_type": scene['type'],
                "layers": self._create_layers(scene, slides, asset_manifest)
            }

            timeline.append(timeline_item)
            current_time += duration

        # 編集マッピング
        edit_mapping = {
            "project_id": project_id,
            "title": script_data.get('title', ''),
            "total_duration": current_time,
            "fps": 30,
            "resolution": {
                "width": 1920,
                "height": 1080
            },
            "timeline": timeline,
            "audio": {
                "bgm": self._get_bgm_path(asset_manifest),
                "narrations": self._get_narration_paths(asset_manifest)
            },
            "created_at": datetime.now().isoformat()
        }

        return edit_mapping

    def _create_layers(
        self,
        scene: Dict[str, Any],
        slides: List[Dict[str, Any]],
        asset_manifest: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        シーンのレイヤーを作成

        Args:
            scene: シーンデータ
            slides: スライドデータ
            asset_manifest: 素材マニフェスト

        Returns:
            レイヤーリスト
        """
        layers = []

        # スライドレイヤー
        for i, slide in enumerate(slides):
            layer = {
                "type": "slide",
                "z_index": 10 + i,
                "slide_number": slide['slide_number'],
                "content": {
                    "title": slide.get('title_text', ''),
                    "body": slide.get('body_text', ''),
                    "layout": slide.get('layout', 'center')
                },
                "animation": {
                    "in": "fadeIn",
                    "out": "fadeOut",
                    "duration": 0.5
                }
            }
            layers.append(layer)

        # 画像レイヤー
        images = self._find_assets_for_scene(scene, asset_manifest, "images")
        for i, image in enumerate(images):
            layer = {
                "type": "image",
                "z_index": 5 + i,
                "src": image.get('stored_path', ''),
                "position": "center",
                "scale": 1.0,
                "animation": {
                    "in": "zoomIn",
                    "out": "fadeOut",
                    "duration": 0.3
                }
            }
            layers.append(layer)

        # 動画レイヤー
        videos = self._find_assets_for_scene(scene, asset_manifest, "videos")
        for i, video in enumerate(videos):
            layer = {
                "type": "video",
                "z_index": 1 + i,
                "src": video.get('stored_path', ''),
                "start_time": 0,
                "playback_rate": 1.0
            }
            layers.append(layer)

        return layers

    def _find_assets_for_scene(
        self,
        scene: Dict[str, Any],
        asset_manifest: Dict[str, Any],
        asset_type: str
    ) -> List[Dict[str, Any]]:
        """シーンに対応する素材を検索"""
        scene_num = scene['scene_number']
        assets = asset_manifest.get('assets', {}).get(asset_type, [])

        # シーン番号でフィルタリング
        return [
            asset for asset in assets
            if f"シーン{scene_num}" in asset.get('metadata', {}).get('description', '')
        ]

    def _get_bgm_path(self, asset_manifest: Dict[str, Any]) -> str:
        """BGMパスを取得"""
        bgm_list = asset_manifest.get('assets', {}).get('audio', [])
        if bgm_list:
            return bgm_list[0].get('stored_path', '')
        return ''

    def _get_narration_paths(self, asset_manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
        """ナレーションパスリストを取得"""
        narrations = asset_manifest.get('assets', {}).get('narrations', [])
        return [
            {
                "scene_number": self._extract_scene_number(n.get('metadata', {}).get('description', '')),
                "path": n.get('stored_path', '')
            }
            for n in narrations
        ]

    def _extract_scene_number(self, description: str) -> int:
        """説明文からシーン番号を抽出"""
        import re
        match = re.search(r'シーン(\d+)', description)
        if match:
            return int(match.group(1))
        return 0

    def save_edit_mapping(self, mapping: Dict[str, Any]) -> str:
        """
        編集マッピングを保存

        Args:
            mapping: 編集マッピングデータ

        Returns:
            保存したファイルパス
        """
        project_id = mapping.get('project_id', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"edit_mapping_{project_id}_{timestamp}.json"
        filepath = os.path.join(self.mapping_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)

        print(f"編集マッピングを保存しました: {filepath}")
        return filepath

    def export_to_remotion(self, mapping: Dict[str, Any], output_path: str = None) -> str:
        """
        Remotion用の形式でエクスポート

        Args:
            mapping: 編集マッピングデータ
            output_path: 出力ファイルパス

        Returns:
            保存したファイルパス
        """
        if output_path is None:
            project_id = mapping.get('project_id', 'unknown')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"remotion/src/data/composition_{project_id}_{timestamp}.json"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Remotion用のシンプルな形式に変換
        remotion_data = {
            "id": mapping.get('project_id'),
            "title": mapping.get('title'),
            "durationInFrames": int(mapping.get('total_duration', 0) * mapping.get('fps', 30)),
            "fps": mapping.get('fps', 30),
            "width": mapping['resolution']['width'],
            "height": mapping['resolution']['height'],
            "scenes": []
        }

        for item in mapping.get('timeline', []):
            scene = {
                "from": int(item['start_time'] * mapping.get('fps', 30)),
                "durationInFrames": int(item['duration'] * mapping.get('fps', 30)),
                "type": item['scene_type'],
                "layers": item['layers']
            }
            remotion_data["scenes"].append(scene)

        # オーディオ情報を追加
        remotion_data["audio"] = mapping.get('audio', {})

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(remotion_data, f, ensure_ascii=False, indent=2)

        print(f"Remotion用ファイルを保存しました: {output_path}")
        return output_path


def main():
    """メイン処理"""
    import sys

    if len(sys.argv) < 4:
        print("使用方法: python video_generator.py <台本JSON> <スライドJSON> <素材マニフェストJSON>")
        print("例: python video_generator.py script.json slides.json manifest.json")
        sys.exit(1)

    script_file = sys.argv[1]
    slide_file = sys.argv[2]
    manifest_file = sys.argv[3]

    try:
        # データ読み込み
        with open(script_file, 'r', encoding='utf-8') as f:
            script_data = json.load(f)

        with open(slide_file, 'r', encoding='utf-8') as f:
            slide_data = json.load(f)

        with open(manifest_file, 'r', encoding='utf-8') as f:
            asset_manifest = json.load(f)

        # 編集マッピング生成
        generator = VideoGenerator()
        mapping = generator.create_edit_mapping(script_data, slide_data, asset_manifest)

        # 保存
        mapping_path = generator.save_edit_mapping(mapping)

        # Remotion用にエクスポート
        remotion_path = generator.export_to_remotion(mapping)

        print(f"\n✓ 編集マッピング生成完了")
        print(f"  タイトル: {mapping['title']}")
        print(f"  総尺: {mapping['total_duration']}秒")
        print(f"  シーン数: {len(mapping['timeline'])}")
        print(f"  マッピングファイル: {mapping_path}")
        print(f"  Remotionファイル: {remotion_path}")

    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
