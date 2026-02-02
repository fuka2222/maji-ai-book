#!/usr/bin/env python3
"""
メインオーケストレーター
企画から動画生成までの全プロセスを統合管理
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any

# 各モジュールをインポート
from script_generator import ScriptGenerator
from slide_generator import SlideGenerator
from asset_manager import AssetManager
from video_generator import VideoGenerator


class VideoProductionOrchestrator:
    """動画制作オーケストレータークラス"""

    def __init__(self, api_key: str = None):
        """
        初期化

        Args:
            api_key: Anthropic API key
        """
        self.script_gen = ScriptGenerator(api_key)
        self.slide_gen = SlideGenerator(api_key)
        self.asset_mgr = AssetManager()
        self.video_gen = VideoGenerator()

        self.project_dir = "内部データ格納フォルダ/企画"
        os.makedirs(self.project_dir, exist_ok=True)

    def create_project(self, project_data: Dict[str, Any]) -> str:
        """
        新規プロジェクトを作成

        Args:
            project_data: プロジェクトデータ

        Returns:
            プロジェクトID
        """
        project_id = f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        project_data['id'] = project_id
        project_data['created_at'] = datetime.now().isoformat()
        project_data['status'] = 'created'

        # プロジェクトファイルを保存
        project_file = os.path.join(self.project_dir, f"{project_id}.json")
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)

        print(f"✓ プロジェクト作成: {project_id}")
        return project_id

    def run_full_pipeline(self, project_id: str) -> Dict[str, str]:
        """
        完全なパイプラインを実行

        Args:
            project_id: プロジェクトID

        Returns:
            各ステップの出力ファイルパス
        """
        print(f"\n{'='*60}")
        print(f"動画制作パイプライン開始: {project_id}")
        print(f"{'='*60}\n")

        results = {}

        # 1. プロジェクトデータ読み込み
        print("📋 ステップ1: プロジェクトデータ読み込み")
        project_file = os.path.join(self.project_dir, f"{project_id}.json")
        with open(project_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        print(f"  タイトル: {project_data.get('title')}")
        print(f"  カテゴリ: {project_data.get('category')}")
        print()

        # 2. 台本生成
        print("📝 ステップ2: 台本生成")
        script_data = self.script_gen.generate_script(project_data)
        script_path = self.script_gen.save_script(script_data)
        results['script'] = script_path
        print(f"  ✓ 台本生成完了: {len(script_data['scenes'])}シーン")
        print()

        # 3. スライド生成
        print("🖼️  ステップ3: スライド生成")
        slide_data = self.slide_gen.generate_slides(script_data)
        slide_path = self.slide_gen.save_slides(slide_data)
        figma_path = self.slide_gen.export_to_figma_format(slide_data)
        results['slides'] = slide_path
        results['figma'] = figma_path
        print(f"  ✓ スライド生成完了: {len(slide_data['slides'])}スライド")
        print()

        # 4. 素材要件生成
        print("🎨 ステップ4: 素材要件分析")
        requirements = self.asset_mgr.generate_asset_requirements(script_data)
        manifest_path = self.asset_mgr.create_asset_manifest(project_id, requirements)
        results['asset_manifest'] = manifest_path
        print(f"  ✓ 必要な素材を特定:")
        for asset_type, items in requirements.items():
            print(f"    - {asset_type}: {len(items)}件")
        print()

        # 5. 編集マッピング生成
        print("🎬 ステップ5: 編集マッピング生成")

        # マニフェストを読み込み
        with open(manifest_path, 'r', encoding='utf-8') as f:
            asset_manifest = json.load(f)

        mapping = self.video_gen.create_edit_mapping(script_data, slide_data, asset_manifest)
        mapping_path = self.video_gen.save_edit_mapping(mapping)
        remotion_path = self.video_gen.export_to_remotion(mapping)
        results['mapping'] = mapping_path
        results['remotion'] = remotion_path
        print(f"  ✓ 編集マッピング完了")
        print(f"    総尺: {mapping['total_duration']}秒")
        print(f"    シーン数: {len(mapping['timeline'])}")
        print()

        # 6. プロジェクトステータス更新
        project_data['status'] = 'ready_for_production'
        project_data['updated_at'] = datetime.now().isoformat()
        project_data['outputs'] = results

        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)

        print(f"\n{'='*60}")
        print("✅ パイプライン完了!")
        print(f"{'='*60}\n")

        return results

    def show_results(self, results: Dict[str, str]):
        """結果を表示"""
        print("\n📦 生成されたファイル:")
        for key, path in results.items():
            print(f"  - {key}: {path}")

        print("\n📋 次のステップ:")
        print("  1. 生成された台本を確認・編集")
        print("  2. Figmaテンプレートを使用してスライドをデザイン")
        print("  3. 必要な素材（画像、動画、BGM、ナレーション）を準備")
        print("  4. 素材をasset_managerで登録")
        print("  5. Remotionで動画をレンダリング")
        print()


def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  新規プロジェクト: python main_orchestrator.py create <企画JSONファイル>")
        print("  パイプライン実行: python main_orchestrator.py run <プロジェクトID>")
        print()
        print("例:")
        print("  python main_orchestrator.py create config/sample_project.json")
        print("  python main_orchestrator.py run proj_20250128_143022")
        sys.exit(1)

    command = sys.argv[1]
    orchestrator = VideoProductionOrchestrator()

    try:
        if command == "create":
            if len(sys.argv) < 3:
                print("使用方法: python main_orchestrator.py create <企画JSONファイル>")
                sys.exit(1)

            input_file = sys.argv[2]

            with open(input_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)

            project_id = orchestrator.create_project(project_data)
            print(f"\nプロジェクトID: {project_id}")
            print(f"\nパイプライン実行:")
            print(f"  python src/main_orchestrator.py run {project_id}")

        elif command == "run":
            if len(sys.argv) < 3:
                print("使用方法: python main_orchestrator.py run <プロジェクトID>")
                sys.exit(1)

            project_id = sys.argv[2]

            results = orchestrator.run_full_pipeline(project_id)
            orchestrator.show_results(results)

        else:
            print(f"不明なコマンド: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
