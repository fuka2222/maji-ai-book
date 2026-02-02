#!/usr/bin/env python3
"""
素材管理システム
動画素材、画像素材、BGM、ナレーションなどの素材を管理
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path


class AssetManager:
    """素材管理クラス"""

    def __init__(self, base_dir: str = "内部データ格納フォルダ"):
        """
        初期化

        Args:
            base_dir: ベースディレクトリ
        """
        self.base_dir = base_dir
        self.video_dir = os.path.join(base_dir, "動画素材")
        self.image_dir = os.path.join(base_dir, "画像素材")
        self.audio_dir = os.path.join(base_dir, "BGM")
        self.narration_dir = os.path.join(base_dir, "ナレーション")

        # ディレクトリを作成
        for directory in [self.video_dir, self.image_dir, self.audio_dir, self.narration_dir]:
            os.makedirs(directory, exist_ok=True)

        # 素材データベース（メタデータ管理）
        self.db_path = os.path.join(base_dir, "asset_database.json")
        self.db = self._load_database()

    def _load_database(self) -> Dict[str, Any]:
        """素材データベースを読み込む"""
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "videos": [],
            "images": [],
            "audio": [],
            "narrations": []
        }

    def _save_database(self):
        """素材データベースを保存"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, ensure_ascii=False, indent=2)

    def add_asset(self, asset_type: str, file_path: str, metadata: Dict[str, Any] = None) -> str:
        """
        素材を追加

        Args:
            asset_type: 素材タイプ (video/image/audio/narration)
            file_path: 元のファイルパス
            metadata: メタデータ

        Returns:
            管理用の素材ID
        """
        # ファイルをコピー
        filename = os.path.basename(file_path)
        asset_id = f"{asset_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"

        # コピー先ディレクトリを決定
        if asset_type == "video":
            dest_dir = self.video_dir
            db_key = "videos"
        elif asset_type == "image":
            dest_dir = self.image_dir
            db_key = "images"
        elif asset_type == "audio":
            dest_dir = self.audio_dir
            db_key = "audio"
        elif asset_type == "narration":
            dest_dir = self.narration_dir
            db_key = "narrations"
        else:
            raise ValueError(f"不明な素材タイプ: {asset_type}")

        dest_path = os.path.join(dest_dir, asset_id)

        # ファイルをコピー
        if os.path.exists(file_path):
            shutil.copy2(file_path, dest_path)
        else:
            # ファイルが存在しない場合はプレースホルダーを作成
            print(f"警告: ファイルが見つかりません: {file_path}")
            Path(dest_path).touch()

        # メタデータを作成
        asset_data = {
            "id": asset_id,
            "original_path": file_path,
            "stored_path": dest_path,
            "filename": filename,
            "added_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        # データベースに追加
        self.db[db_key].append(asset_data)
        self._save_database()

        print(f"素材を追加しました: {asset_id}")
        return asset_id

    def get_asset(self, asset_id: str) -> Dict[str, Any]:
        """
        素材IDから素材情報を取得

        Args:
            asset_id: 素材ID

        Returns:
            素材データ
        """
        for asset_type in ["videos", "images", "audio", "narrations"]:
            for asset in self.db[asset_type]:
                if asset["id"] == asset_id:
                    return asset

        raise ValueError(f"素材が見つかりません: {asset_id}")

    def list_assets(self, asset_type: str = None) -> List[Dict[str, Any]]:
        """
        素材一覧を取得

        Args:
            asset_type: 素材タイプ（Noneの場合は全て）

        Returns:
            素材リスト
        """
        if asset_type:
            if asset_type == "video":
                return self.db["videos"]
            elif asset_type == "image":
                return self.db["images"]
            elif asset_type == "audio":
                return self.db["audio"]
            elif asset_type == "narration":
                return self.db["narrations"]
        else:
            all_assets = []
            for asset_list in self.db.values():
                all_assets.extend(asset_list)
            return all_assets

    def generate_asset_requirements(self, script_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        台本から必要な素材リストを生成

        Args:
            script_data: 台本データ

        Returns:
            必要な素材のリスト
        """
        requirements = {
            "images": [],
            "videos": [],
            "audio": ["BGM"],  # BGMは基本的に必要
            "narrations": []
        }

        for scene in script_data.get('scenes', []):
            scene_num = scene['scene_number']

            # ビジュアル説明から素材要件を抽出
            visual_desc = scene.get('visual_description', '')

            if '画像' in visual_desc or 'イラスト' in visual_desc:
                requirements["images"].append(f"シーン{scene_num}: {visual_desc}")

            if '動画' in visual_desc or 'ビデオ' in visual_desc:
                requirements["videos"].append(f"シーン{scene_num}: {visual_desc}")

            # ナレーション
            if scene.get('narration'):
                requirements["narrations"].append(f"シーン{scene_num}: {scene['narration']}")

        return requirements

    def create_asset_manifest(self, project_id: str, requirements: Dict[str, List[str]]) -> str:
        """
        素材マニフェストを作成

        Args:
            project_id: プロジェクトID
            requirements: 必要な素材リスト

        Returns:
            マニフェストファイルパス
        """
        manifest = {
            "project_id": project_id,
            "created_at": datetime.now().isoformat(),
            "requirements": requirements,
            "assets": {
                "images": [],
                "videos": [],
                "audio": [],
                "narrations": []
            }
        }

        manifest_path = os.path.join(self.base_dir, f"asset_manifest_{project_id}.json")

        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        print(f"素材マニフェストを作成しました: {manifest_path}")
        return manifest_path


def main():
    """メイン処理"""
    import sys

    if len(sys.argv) < 2:
        print("使用方法:")
        print("  素材追加: python asset_manager.py add <タイプ> <ファイルパス>")
        print("  素材一覧: python asset_manager.py list [タイプ]")
        print("  素材要件生成: python asset_manager.py requirements <台本JSONファイル>")
        sys.exit(1)

    command = sys.argv[1]
    manager = AssetManager()

    try:
        if command == "add":
            if len(sys.argv) < 4:
                print("使用方法: python asset_manager.py add <タイプ> <ファイルパス>")
                sys.exit(1)

            asset_type = sys.argv[2]
            file_path = sys.argv[3]

            asset_id = manager.add_asset(asset_type, file_path)
            print(f"✓ 素材ID: {asset_id}")

        elif command == "list":
            asset_type = sys.argv[2] if len(sys.argv) > 2 else None
            assets = manager.list_assets(asset_type)

            print(f"\n素材一覧 ({len(assets)}件)")
            for asset in assets:
                print(f"  - {asset['id']}: {asset['filename']}")

        elif command == "requirements":
            if len(sys.argv) < 3:
                print("使用方法: python asset_manager.py requirements <台本JSONファイル>")
                sys.exit(1)

            script_file = sys.argv[2]
            with open(script_file, 'r', encoding='utf-8') as f:
                script_data = json.load(f)

            requirements = manager.generate_asset_requirements(script_data)
            project_id = script_data.get('project_id', 'unknown')
            manifest_path = manager.create_asset_manifest(project_id, requirements)

            print(f"\n✓ 必要な素材:")
            for asset_type, items in requirements.items():
                print(f"\n{asset_type}:")
                for item in items:
                    print(f"  - {item}")

            print(f"\nマニフェスト: {manifest_path}")

        else:
            print(f"不明なコマンド: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
