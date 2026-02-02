#!/bin/bash
# セットアップスクリプト

echo "======================================"
echo "AI動画制作自動化システム セットアップ"
echo "======================================"
echo ""

# Python依存パッケージのインストール
echo "📦 Python依存パッケージをインストール中..."
pip install -r requirements.txt

echo ""
echo "✓ セットアップ完了！"
echo ""
echo "次のステップ："
echo "1. Anthropic API keyを設定してください"
echo "   export ANTHROPIC_API_KEY='your-api-key-here'"
echo ""
echo "2. サンプルプロジェクトを実行してみましょう"
echo "   python src/main_orchestrator.py create config/sample_project.json"
echo ""
echo "3. 詳細はREADME.mdを参照してください"
echo ""
